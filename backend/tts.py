import asyncio
import subprocess
from pathlib import Path

from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_BASE_URL, TTS_MODEL, TTS_VOICE, FFMPEG, FFPROBE, TTS_PROVIDER
from models import Scene


client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL) if OPENAI_BASE_URL else OpenAI(api_key=OPENAI_API_KEY)


def _openai_tts(text: str, out_path: Path) -> bool:
    if not OPENAI_API_KEY:
        return False
    try:
        with client.audio.speech.create(model=TTS_MODEL, voice=TTS_VOICE, input=text, response_format="mp3") as resp:
            with open(out_path, "wb") as f:
                for chunk in resp.iter_bytes():
                    f.write(chunk)
        return True
    except Exception as e:
        print("openai tts failed:", e)
        return False


def _edge_tts(text: str, out_path: Path) -> bool:
    try:
        import edge_tts
        async def main():
            comm = edge_tts.Communicate(text, "en-US-AriaNeural")
            await comm.save(str(out_path))
        asyncio.run(main())
        return out_path.exists()
    except Exception as e:
        print("edge tts failed:", e)
        return False


def _ffprobe_duration(out_path: Path) -> float:
    try:
        r = subprocess.run(
            [FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(out_path)],
            capture_output=True, text=True, check=True,
        )
        return float(r.stdout.strip())
    except Exception:
        return 0.0


def synthesize(text: str, out_path: Path) -> float:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    ok = False
    if TTS_PROVIDER in ("auto", "openai"):
        ok = _openai_tts(text, out_path)
    if not ok and TTS_PROVIDER in ("auto", "edge"):
        ok = _edge_tts(text, out_path)
    if not ok:
        # write silence? generate empty file not valid; try edge as last resort
        _edge_tts(text, out_path)
    return _ffprobe_duration(out_path)


def narrate_scenes(scenes: list, job_dir: Path) -> list:
    audio_dir = job_dir / "audio"
    audio_dir.mkdir(exist_ok=True)
    for sc in scenes:
        out = audio_dir / sc.audioFile
        dur = synthesize(sc.narration, out)
        if dur > 0:
            sc.durationSec = round(dur + 0.6, 2)
        sc.durationSec = max(4.0, min(45.0, sc.durationSec))
    return scenes
