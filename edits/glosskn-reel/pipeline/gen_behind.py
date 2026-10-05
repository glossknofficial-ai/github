"""Generate behind.html: big words that sit BEHIND the speaker (composited through the person matte)."""
import os
from edl import *

W, H = 2160, 3840
o = lambda src: round(to_out(src), 3)
# (id, src_in, src_out, text, css) — placed above/around her head so she occludes part of the word
BEHIND = [
    ("bmission", 19.98, 21.30, "mission", "top: 400px; font-size: 420px;"),
    ("bdone", 47.05, 47.97, "done.", "top: 700px; font-size: 380px;"),
    ("bpower", 48.70, 52.62, "Power Cleanse", "top: 400px; font-size: 300px;"),
]
els, tl = [], []
for bid, a, b, text, css in BEHIND:
    ta, tb = o(a), o(b)
    els.append(f'<div id="{bid}" class="clip bt-host" data-start="{ta:.3f}" data-duration="{tb - ta:.3f}" data-track-index="1">'
               f'<div class="bt" id="{bid}-t" style="{css}">{text}</div></div>')
    tl.append(f'tl.fromTo("#{bid}-t",{{opacity:0,scale:0.86,y:60}},{{opacity:1,scale:1,y:0,duration:0.45,ease:"power3.out"}},{ta:.3f});')
    tl.append(f'tl.fromTo("#{bid}-t",{{scale:1}},{{scale:1.04,duration:{max(0.3, tb - ta - 0.65):.3f},ease:"none",immediateRender:false}},{ta + 0.45:.3f});')
    tl.append(f'tl.to("#{bid}-t",{{opacity:0,duration:0.2,ease:"power2.in"}},{tb - 0.2:.3f});')

fonts = open(os.path.join(HERE, "style.css")).read().split(":root")[0]
page = f"""<!doctype html>
<html lang="en" data-resolution="portrait-4k">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="vendor/gsap.min.js"></script>
    <style>
{fonts}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; background: transparent; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; }}
      .bt-host {{ position: absolute; inset: 0; }}
      .bt {{ position: absolute; left: 0; right: 0; text-align: center; color: #d7b6e2;
             font-family: "Playfair Display", serif; font-style: italic; font-weight: 800; line-height: 1; letter-spacing: -8px;
             text-shadow: 0 0 4px rgba(46, 18, 60, .55), 0 14px 70px rgba(46, 18, 60, .55); white-space: nowrap; }}
      .bt .l2 {{ display: block; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="behind" data-start="0" data-duration="{TOTAL + 2.2:.3f}" data-width="{W}" data-height="{H}">
      {chr(10).join('      ' + e for e in els).strip()}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      {chr(10).join('      ' + t for t in tl).strip()}
      tl.set({{}}, {{}}, {TOTAL + 2.2:.3f});
      window.__timelines["behind"] = tl;
    </script>
  </body>
</html>
"""
open(os.path.join(PROJECT, "behind", "index.html"), "w").write(page)
print("behind words", len(BEHIND))
