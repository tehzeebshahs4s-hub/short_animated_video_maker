import json
import time
import shutil
from pathlib import Path

from config import JOBS_DIR, OUTPUTS_DIR
from models import JobStatus, Storyboard
from storyboard import generate_storyboard
from tts import narrate_scenes
from images import generate_images
from render import render, prepare_assets


def job_dir(job_id: str) -> Path:
    return JOBS_DIR / job_id


def status_path(job_id: str) -> Path:
    return job_dir(job_id) / "status.json"


def read_status(job_id: str) -> dict:
    p = status_path(job_id)
    if p.exists():
        return json.loads(p.read_text())
    return {"jobId": job_id, "stage": "unknown", "percent": 0, "message": ""}


def write_status(job_id: str, stage: str, percent: int, message: str = "", error: str = None, output_url: str = None):
    p = status_path(job_id)
    p.parent.mkdir(parents=True, exist_ok=True)
    data = read_status(job_id)
    data.update({"jobId": job_id, "stage": stage, "percent": percent, "message": message, "updatedAt": time.time()})
    if error is not None:
        data["error"] = error
    if output_url is not None:
        data["outputUrl"] = output_url
    p.write_text(json.dumps(data))


def create_job(prompt: str) -> str:
    job_id = "job_" + str(int(time.time() * 1000))
    d = job_dir(job_id)
    d.mkdir(parents=True, exist_ok=True)
    (d / "prompt.txt").write_text(prompt)
    write_status(job_id, "queued", 0, "Job created", None)
    # store prompt in status
    s = read_status(job_id)
    s["prompt"] = prompt
    s["createdAt"] = time.time()
    status_path(job_id).write_text(json.dumps(s))
    return job_id


def run_job(job_id: str, draft: bool = False):
    d = job_dir(job_id)
    prompt = (d / "prompt.txt").read_text().strip()
    try:
        write_status(job_id, "storyboard", 5, "Generating storyboard...")
        sb = generate_storyboard(prompt, job_id)
        # save
        (d / "storyboard_raw.json").write_text(sb.model_dump_json(indent=2))

        write_status(job_id, "tts", 25, "Generating narration audio...")
        sb.scenes = narrate_scenes(sb.scenes, d)
        sb.totalDurationSec = sum(s.durationSec for s in sb.scenes)

        if not draft:
            write_status(job_id, "images", 45, "Generating scene images...")
            generate_images(sb.scenes, d)
        else:
            for s in sb.scenes:
                s.visual.kind = "text-only"

        write_status(job_id, "prepare", 60, "Preparing render assets...")
        (d / "storyboard.json").write_text(sb.model_dump_json(indent=2))

        write_status(job_id, "render", 65, "Rendering video (this may take a few minutes)...")
        out = render(job_id, d)

        write_status(job_id, "done", 100, "Done", output_url=f"/api/jobs/{job_id}/video")
    except Exception as e:
        write_status(job_id, "error", 0, "Failed", error=str(e))
        raise
