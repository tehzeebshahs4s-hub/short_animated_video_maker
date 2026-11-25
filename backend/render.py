import json
import shutil
import subprocess
from pathlib import Path

from config import REMOTION_DIR, REMOTION_PUBLIC, OUTPUTS_DIR, FFMPEG


def prepare_assets(job_id: str, job_dir: Path) -> None:
    dst = REMOTION_PUBLIC / job_id
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True, exist_ok=True)
    # copy audio + images
    for sub in ("audio", "images"):
        src = job_dir / sub
        if src.exists():
            shutil.copytree(src, dst / sub, dirs_exist_ok=True)
    # write storyboard with relative public paths
    sb = json.loads((job_dir / "storyboard.json").read_text())
    for sc in sb["scenes"]:
        if sc.get("audioFile"):
            sc["audioFile"] = f"jobs/{job_id}/audio/{sc['audioFile']}"
        v = sc.get("visual", {})
        if v.get("imageFile"):
            v["imageFile"] = f"jobs/{job_id}/images/{v['imageFile']}"
    (dst / "storyboard.json").write_text(json.dumps(sb))
    # also keep a copy at job_dir for worker
    (job_dir / "storyboard_public.json").write_text(json.dumps(sb))


def render(job_id: str, job_dir: Path) -> Path:
    prepare_assets(job_id, job_dir)
    out = OUTPUTS_DIR / f"{job_id}.mp4"
    props_path = REMOTION_PUBLIC / job_id / "storyboard.json"
    import shutil as _sh
    npx = _sh.which("npx") or "npx.cmd"
    cmd = [
        npx, "remotion", "render", "src/index.ts", "Explainer",
        str(out),
        f"--props={props_path}",
        "--overwrite",
        "--bundle-cache=false",
    ]
    env = dict(**__import__("os").environ)
    env["PATH"] = r"C:\Program Files\nodejs;C:\Users\S4S\miniconda3\Library\bin;C:\Users\S4S\miniconda3\Scripts;" + env.get("PATH", "")
    subprocess.run(cmd, cwd=str(REMOTION_DIR), check=True, env=env)
    return out
