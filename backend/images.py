import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_BASE_URL, IMAGE_MODEL
from models import Scene


client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL) if OPENAI_BASE_URL else OpenAI(api_key=OPENAI_API_KEY)


def gen_image(prompt: str, out_path: Path) -> bool:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        resp = client.images.generate(model=IMAGE_MODEL, prompt=prompt, size="1536x1024", n=1)
        b64 = resp.data[0].b64_json
        if b64:
            out_path.write_bytes(base64.b64decode(b64))
            return True
        # url fallback
        url = resp.data[0].url
        if url:
            import urllib.request
            urllib.request.urlretrieve(url, out_path)
            return True
    except Exception as e:
        print("image gen failed:", e)
    # placeholder
    try:
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new("RGB", (1536, 1024), (30, 41, 59))
        d = ImageDraw.Draw(img)
        d.text((80, 480), prompt[:120], fill=(148, 163, 184))
        img.save(out_path)
        return True
    except Exception as e:
        print("placeholder failed:", e)
    return False


def generate_images(scenes: list, job_dir: Path, max_workers: int = 3) -> None:
    img_dir = job_dir / "images"
    img_dir.mkdir(exist_ok=True)
    tasks = []
    for sc in scenes:
        if sc.visual.kind == "image" and sc.visual.imagePrompt:
            out = img_dir / (sc.visual.imageFile or f"{sc.id}.png")
            tasks.append((sc, out))
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = {ex.submit(gen_image, sc.visual.imagePrompt, out): sc for sc, out in tasks}
        for f in as_completed(futs):
            sc = futs[f]
            ok = f.result()
            if not ok:
                sc.visual.kind = "text-only"
