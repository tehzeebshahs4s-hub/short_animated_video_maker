import json
import os
import re
from typing import Dict

from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL
from models import Storyboard, Scene, Visual

client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL) if OPENAI_BASE_URL else OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """You are an educational animated-video scriptwriter.
You output ONLY valid JSON matching the provided schema. No markdown, no code fences, no commentary.

Rules:
- 8 to 14 scenes.
- Total duration between 180 and 300 seconds.
- Each scene narration: 1-4 sentences, spoken ~130 words/min. Set durationSec = ceil(words/130*60)+2, clamped 4..45.
- Scene types: "title" (intro), "content", "diagram", "outro".
- First scene type "title", last "outro".
- transition: fade/slide/zoom/none.
- visual.kind: "image" (needs imagePrompt), "shapes" (diagram with labels), or "text-only".
- For visual.kind=="image", provide a descriptive imagePrompt suitable for an image generator.
- bullets: 0-5 short phrases for content scenes.
- headline: short title for the scene.
- caption: optional subtitle (defaults to narration).
- Keep language clear and engaging for general audience.
"""


def _strip_fences(text: str) -> str:
    text = text.strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if m:
        text = m.group(1).strip()
    return text


def generate_storyboard(prompt: str, job_id: str) -> Storyboard:
    user_msg = (
        f"Topic/prompt: {prompt}\n\n"
        "Produce the storyboard JSON. Use jobId exactly: " + job_id
    )
    schema_hint = {
        "jobId": job_id,
        "title": "string",
        "fps": 30,
        "width": 1920,
        "height": 1080,
        "totalDurationSec": 0,
        "music": "upbeat-ambient",
        "scenes": [
            {
                "id": "s1",
                "type": "title",
                "durationSec": 8,
                "transition": "fade",
                "narration": "string",
                "audioFile": None,
                "visual": {"kind": "image", "imagePrompt": "string", "imageFile": None, "kenBurns": "zoom-in"},
                "headline": "string",
                "bullets": [],
                "caption": None,
            }
        ],
    }
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_msg + "\n\nSchema example:\n" + json.dumps(schema_hint)},
    ]

    last_err = None
    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.7,
            )
            raw = resp.choices[0].message.content
            data = json.loads(_strip_fences(raw))
            data["jobId"] = job_id
            # normalize scene ids / audioFile placeholders
            for i, sc in enumerate(data.get("scenes", []), start=1):
                sc.setdefault("id", f"s{i}")
                sc["audioFile"] = f"{sc['id']}.mp3"
                v = sc.setdefault("visual", {"kind": "text-only"})
                if v.get("kind") == "image":
                    v.setdefault("imageFile", f"{sc['id']}.png")
            # recompute total
            total = sum(s.get("durationSec", 5) for s in data["scenes"])
            data["totalDurationSec"] = total
            sb = Storyboard.model_validate(data)
            return sb
        except Exception as e:
            last_err = e
            messages.append({"role": "assistant", "content": raw if "raw" in locals() else ""})
            messages.append({"role": "user", "content": f"Your previous output failed validation: {e}. Output corrected JSON only."})
    raise RuntimeError(f"storyboard generation failed: {last_err}")
