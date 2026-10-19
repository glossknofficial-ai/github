"""Generate the birthday hero still with Gemini image models, using the real product photos as references.

usage: python3 tools/gen_image.py OUT.png [model] [extra prompt]
"""
import base64
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REFS = [
    ("cake-reference.webp", "STYLE / COMPOSITION REFERENCE (do not copy its products or brand):"),
    ("power-melt.webp", "PRODUCT 1 — GLOSSKN Power Melt cleansing balm tube (reproduce exactly):"),
    ("power-cleanse.webp", "PRODUCT 2 — GLOSSKN Power Cleanse pump bottle (reproduce exactly):"),
    ("power-cleanse-box.webp", "PRODUCT 3 — the Power Cleanse lilac carton box (reproduce exactly, it goes on the table):"),
]

PROMPT = """Create a bright, joyful, high-end studio product photo for a skincare brand's 1st birthday sale.
Vertical 9:16 composition.

Scene, following the style reference: a tall round layer birthday cake on a cake stand, with a
generous wedge sliced out of the front so the soft vanilla sponge layers and cream are visible.
Nestled INSIDE that cut-out of the cake sit exactly two products: the GLOSSKN Power Melt white tube
(standing upright) and the GLOSSKN Power Cleanse white pump bottle (standing upright), side by side,
labels facing the camera and fully readable. The Power Cleanse lilac carton box stands on the table
in front of the cake stand, slightly to one side, front panel facing camera. A cut slice of cake on
a small white plate in the foreground corner.

Styling: vivid, cheerful, not dull — candy pink and lilac buttercream piping with swirls, rainbow
sprinkles, tall thin gold candles lit with warm flames on top of the cake, colourful confetti and
curled paper ribbon scattered on the table, a few soft pastel balloons out of focus in the
background. Seamless saturated pink-to-lilac backdrop, soft diffused studio light with gentle
shadows, crisp focus on the products, magazine-quality, photorealistic.

Critical product rules: keep the GLOSSKN logo, product names ("POWER MELT CLEANSING BALM",
"POWER CLEANSE MAKE-UP REMOVING FACE WASH"), the thin gold label frame, white packaging and
lilac box exactly as in the product references. Do not invent other products, other brands,
extra text, or watermarks. Leave clean space in the top third of the frame for a headline.
"""


def part_for(name):
    data = (ROOT / "refs" / name).read_bytes()
    return {"inline_data": {"mime_type": "image/webp", "data": base64.b64encode(data).decode()}}


def main():
    out = Path(sys.argv[1])
    model = sys.argv[2] if len(sys.argv) > 2 else "gemini-3-pro-image"
    extra = sys.argv[3] if len(sys.argv) > 3 else ""
    parts = []
    for name, label in REFS:
        parts.append({"text": label})
        parts.append(part_for(name))
    parts.append({"text": PROMPT + ("\n" + extra if extra else "")})
    body = {
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {"responseModalities": ["IMAGE", "TEXT"], "imageConfig": {"aspectRatio": "9:16", "imageSize": "2K"}},
    }
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        data=json.dumps(body).encode(), headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=300) as r:
        resp = json.load(r)
    for cand in resp.get("candidates", []):
        for p in cand.get("content", {}).get("parts", []):
            blob = p.get("inline_data") or p.get("inlineData")
            if blob:
                out.write_bytes(base64.b64decode(blob["data"]))
                print("wrote", out, blob.get("mime_type") or blob.get("mimeType"))
                return
            if "text" in p:
                print("text:", p["text"][:400])
    print(json.dumps(resp)[:1500])
    sys.exit(1)


if __name__ == "__main__":
    main()
