# Prompt2Video

Generate 3-5 minute animated explainer videos from a text prompt.

## Stack
- Frontend: Vite + React
- Backend: FastAPI (Python)
- Renderer: Remotion (React -> MP4 via Chrome + ffmpeg)
- AI: OpenAI (GPT storyboard, TTS, image gen) with free fallbacks (edge-tts, Pillow placeholders)

## Prerequisites
- Node.js 18+ and npm
- Python 3.11+ with conda/pip
- ffmpeg + ffprobe on PATH (conda: `conda install ffmpeg`)
- Google Chrome (for Remotion)
- OpenAI API key with credits (optional; edge-tts fallback for voice)

## Local setup
```bash
# backend
cd backend
cp .env.example .env   # fill MY_OPEN_API_KEY
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# frontend (new terminal)
cd frontend
npm install
npm run dev            # http://localhost:5173

# remotion deps (once)
cd remotion
npm install
```
Set PATH to include ffmpeg + nodejs.

## Usage
Open http://localhost:5173, enter a prompt, click Generate. Polling shows progress; video appears when done.

## Deployment (StackCP - tehzeebshah.aiaiaiaiai.io)
1. Push repo to GitHub.
2. In StackCP: create Python app (Passenger) pointing at `backend/`, entry `passenger_wsgi.py`, install `requirements.txt`.
3. Set env vars in StackCP panel (MY_OPEN_API_KEY, etc.).
4. Frontend: `npm run build` in `frontend/`, upload `dist/` to doc root (or Git-deploy).
5. Enable HTTPS (Let's Encrypt) in StackCP.
6. Cron: run `python worker.py` every minute to process queued jobs (shared hosting has no long-running processes).
7. Note: shared hosting usually lacks ffmpeg/Chrome. Either (a) use a VPS tier, or (b) run the render worker on your PC that polls the API and uploads MP4s via SFTP (Design B).

SSH inspection (port 22) was blocked in testing; enable SSH in StackCP panel first, then run:
```
whoami; python3 --version; node --version; which ffmpeg; which google-chrome
```
to decide between all-in-one (A) vs hybrid (B).

## Notes
- Draft mode skips image generation.
- Max length capped at 5 min (MAX_DURATION_SEC).
- OpenAI key with no credits falls back to edge-tts (voice) and Pillow placeholders (images).
