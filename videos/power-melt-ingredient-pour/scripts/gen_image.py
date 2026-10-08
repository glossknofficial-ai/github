"""Generate an image with Gemini (key is injected by the environment's network secret).

    python3 scripts/gen_image.py OUT.png "prompt" [aspect] [model]
"""
import base64
import json
import sys
import urllib.request

out, prompt = sys.argv[1], sys.argv[2]
aspect = sys.argv[3] if len(sys.argv) > 3 else "1:1"
model = sys.argv[4] if len(sys.argv) > 4 else "gemini-3-pro-image"

body = {
    "contents": [{"parts": [{"text": prompt}]}],
    "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": aspect}},
}
req = urllib.request.Request(
    f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
    data=json.dumps(body).encode(), headers={"Content-Type": "application/json"},
)
with urllib.request.urlopen(req, timeout=300) as r:
    d = json.load(r)
for cand in d.get("candidates", []):
    for part in cand.get("content", {}).get("parts", []):
        if "inlineData" in part:
            open(out, "wb").write(base64.b64decode(part["inlineData"]["data"]))
            print("wrote", out)
            sys.exit(0)
print("no image returned:", json.dumps(d)[:600])
sys.exit(1)
