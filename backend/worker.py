"""Cron/worker entrypoint: process queued jobs one at a time."""
import time
import sys
from pathlib import Path

from config import JOBS_DIR
from pipeline import read_status, run_job


def main(loop: bool = False, interval: int = 30):
    while True:
        processed = False
        for d in sorted(JOBS_DIR.iterdir()):
            if not d.is_dir():
                continue
            p = d / "status.json"
            if not p.exists():
                continue
            st = read_status(d.name)
            if st.get("stage") == "queued":
                print("Processing", d.name)
                try:
                    run_job(d.name)
                except Exception as e:
                    print("Failed", d.name, e)
                processed = True
                break
        if not loop:
            break
        if not processed:
            time.sleep(interval)


if __name__ == "__main__":
    loop = "--loop" in sys.argv
    main(loop=loop)
