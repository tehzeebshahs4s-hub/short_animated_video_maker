import json
import re
from typing import Dict

from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL
from models import Storyboard, Scene, Visual

client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL) if OPENAI_BASE_URL else OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """You are an educational animated-video scriptwriter.
Output ONLY valid JSON. No markdown, no code fences, no commentary.

Schema:
{
  "title": "string",
  "scenes": [
    {
      "id": "s1",
      "type": "title|content|diagram|outro",
      "durationSec": 8,
      "transition": "fade|slide|zoom|none",
      "narration": "string",
      "headline": "string",
      "bullets": ["short phrase"],
      "caption": "string or null",
      "visual": {"kind": "image|text-only", "imagePrompt": "string"}
    }
  ]
}

Rules:
- 5 to 8 scenes.
- Total duration 120-180 seconds.
- Each scene narration: 1-3 sentences.
- durationSec between 6 and 30.
- First scene type "title", last "outro".
- visual.kind "image" requires imagePrompt; otherwise "text-only".
- Keep language clear and engaging.
"""


def _strip_fences(text: str) -> str:
    text = text.strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if m:
        text = m.group(1).strip()
    return text


def _normalize(data: dict, job_id: str) -> dict:
    data["jobId"] = job_id
    data.setdefault("fps", 30)
    data.setdefault("width", 1920)
    data.setdefault("height", 1080)
    data.setdefault("music", None)
    scenes = data.get("scenes", [])
    for i, sc in enumerate(scenes, start=1):
        sc.setdefault("id", f"s{i}")
        sc["audioFile"] = f"{sc['id']}.mp3"
        sc.setdefault("type", "content")
        sc.setdefault("durationSec", 8)
        sc["durationSec"] = max(4, min(30, float(sc["durationSec"])))
        sc.setdefault("transition", "fade")
        sc.setdefault("narration", "")
        sc.setdefault("headline", "")
        if isinstance(sc.get("bullets"), str):
            sc["bullets"] = [sc["bullets"]]
        sc.setdefault("bullets", [])
        if not isinstance(sc["bullets"], list):
            sc["bullets"] = []
        sc.setdefault("caption", None)
        if not isinstance(sc.get("visual"), dict):
            sc["visual"] = {"kind": "text-only"}
        v = sc.setdefault("visual", {"kind": "text-only"})
        kind = str(v.get("kind", "text-only")).lower()
        if kind in ("image", "illustration", "photo", "picture"):
            v["kind"] = "image"
            v.setdefault("imagePrompt", sc.get("headline", ""))
            v.setdefault("imageFile", f"{sc['id']}.png")
            v.setdefault("kenBurns", "zoom-in")
        else:
            v["kind"] = "text-only"
    data["scenes"] = scenes
    data["totalDurationSec"] = sum(s["durationSec"] for s in scenes)
    return data


def generate_storyboard(prompt: str, job_id: str) -> Storyboard:
    user_msg = f"Topic: {prompt}\n\nProduce the storyboard JSON now."
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_msg},
    ]

    last_err = None
    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.5,
                max_tokens=1500,
            )
            raw = resp.choices[0].message.content
            data = json.loads(_strip_fences(raw))
            data = _normalize(data, job_id)
            sb = Storyboard.model_validate(data)
            return sb
        except Exception as e:
            last_err = e
            messages.append({"role": "assistant", "content": raw if "raw" in locals() else ""})
            messages.append({"role": "user", "content": f"Your previous output failed validation: {e}. Output corrected JSON only, no extra text."})
    raise RuntimeError(f"storyboard generation failed: {last_err}")
