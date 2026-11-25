import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
JOBS_DIR = BASE_DIR / "jobs"
OUTPUTS_DIR = BASE_DIR / "outputs"
REMOTION_DIR = BASE_DIR / "remotion"
REMOTION_PUBLIC = REMOTION_DIR / "public" / "jobs"
FFMPEG = os.environ.get("FFMPEG", r"C:\Users\S4S\miniconda3\Library\bin\ffmpeg.exe")
FFPROBE = os.environ.get("FFPROBE", r"C:\Users\S4S\miniconda3\Library\bin\ffprobe.exe")

OPENAI_API_KEY = os.environ.get("MY_OPEN_API_KEY") or os.environ.get("OPENAI_API_KEY")
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL")  # optional, for OpenAI-compatible providers
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-5.4")
TTS_PROVIDER = os.environ.get("TTS_PROVIDER", "auto")  # auto|openai|edge
TTS_MODEL = os.environ.get("TTS_MODEL", "tts-1-hd")
TTS_VOICE = os.environ.get("TTS_VOICE", "nova")
IMAGE_MODEL = os.environ.get("IMAGE_MODEL", "gpt-image-1.5")

MAX_DURATION_SEC = int(os.environ.get("MAX_DURATION_SEC", "300"))
FPS = 30
WIDTH = 1920
HEIGHT = 1080

JOBS_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)
REMOTION_PUBLIC.mkdir(parents=True, exist_ok=True)
