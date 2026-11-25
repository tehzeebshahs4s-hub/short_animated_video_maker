import json
import os
import time
from pathlib import Path

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from config import JOBS_DIR, OUTPUTS_DIR
from pipeline import create_job, run_job, read_status

app = FastAPI(title="Prompt2Video")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class CreateJobReq(BaseModel):
    prompt: str
    draft: bool = False


@app.get("/api/health")
def health():
    return {"ok": True, "time": time.time()}


@app.post("/api/jobs")
def create(req: CreateJobReq, bg: BackgroundTasks):
    if not req.prompt.strip():
        raise HTTPException(400, "prompt required")
    job_id = create_job(req.prompt.strip())
    bg.add_task(run_job, job_id, req.draft)
    return {"jobId": job_id}


@app.get("/api/jobs/{job_id}")
def status(job_id: str):
    p = JOBS_DIR / job_id / "status.json"
    if not p.exists():
        raise HTTPException(404, "not found")
    return json.loads(p.read_text())


@app.get("/api/jobs/{job_id}/video")
def video(job_id: str):
    out = OUTPUTS_DIR / f"{job_id}.mp4"
    if not out.exists():
        raise HTTPException(404, "not ready")
    return FileResponse(str(out), media_type="video/mp4", filename=f"{job_id}.mp4")


@app.get("/api/jobs")
def list_jobs():
    res = []
    for d in JOBS_DIR.iterdir():
        if d.is_dir():
            p = d / "status.json"
            if p.exists():
                res.append(json.loads(p.read_text()))
    return res
