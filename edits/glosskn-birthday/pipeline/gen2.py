"""GLOSSKN 1st-birthday reel v2: built on the founder's real take (data/words.json word timings).
Layouts like the reference: full-screen B-roll, split (B-roll top half, founder slides to bottom half),
pop-in elements (polaroids, logo) and white collage pages. White brand background, purple accents."""
import html, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__)); PROJECT = os.path.dirname(HERE)
W, H = 1080, 1920
SPK_END = 94.6
END_CARD = 3.0
DUR = round(SPK_END + END_CARD, 3)
WORDS = json.load(open(os.path.join(PROJECT, "data", "words.json")))
WORDS = [w for w in WORDS if w["s"] < SPK_END - 0.1]
norm = lambda s: re.sub(r"[^a-z0-9']", "", s.lower())
TOK = [norm(w["w"]) for w in WORDS]


def at(phrase, after=0.0, end=False):
    """start (or end) time of the first occurrence of `phrase` starting after `after` seconds"""
    p = [norm(x) for x in phrase.split()]
    for i in range(len(TOK) - len(p) + 1):
        if WORDS[i]["s"] >= after and TOK[i:i + len(p)] == p:
            return WORDS[i + len(p) - 1]["e"] if end else WORDS[i]["s"]
    raise ValueError(phrase)


B = lambda n: f"media/br/seg{n}.mp4"
# (mode, start, end, source, extra)  modes: full | split | page | polaroid | logo
EV = [
    ("split", at("raising") - 0.15, at("children", end=True) + 0.2, "media/br/seg1.mp4", {}),          # pregnant photo
    ("page", at("one was the little") - 0.05, at("the other one") - 0.05, B(2), {}),                     # baby polaroids w/ hearts
    ("logo", at("the other one") , at("nothing could") + 0.4, "media/logo_dark.png", {}),                # GLOSSKN above her head
    ("split", at("there were days") - 0.1, at("still not moving", end=True) + 0.1, B(3), {}),           # baby + laptop
    ("page", at("i was starting") - 0.05, at("scratch", end=True) + 0.25, B(0), {}),                     # early-days polaroids
    ("full", at("of course") - 0.05, at("mistakes", end=True) + 0.15, B(4), {}),                        # team / book collage
    ("split", at("between") - 0.1, at("everyday life", end=True), B(6), {}),                           # home + shoot
    ("split", at("building a brand") - 0.05, at("working on") - 0.05, B(5), {}),                        # production
    ("full", at("things hardly") - 0.05, at("plan", after=30, end=True) + 0.2, B(14), {}),             # boxes chaos
    ("polaroid", at("my little one grow") , at("taught me") + 0.2, "media/child.jpg", {"cap": "my little one", "x": 600, "y": 210, "rot": 5}),
    ("full", at("they just learn") - 0.1, at("they learn again", end=True) + 0.25, B(15), {}),        # child on the slide
    ("split", at("my baby's first") - 0.1, at("our first launch") - 0.02, B(2), {}),
    ("full", at("our first launch") - 0.02, at("our first order") - 0.02, B(8), {}),                   # booth
    ("split", at("our first order") - 0.02, at("someone who") - 0.02, "media/shopify.mp4", {}),
    ("full", at("someone who") - 0.02, at("created", end=True) + 0.1, B(20), {}),                      # review
    ("full", at("all those little") - 0.1, at("adding up", end=True) + 0.3, B(19), {}),                # power reset box
    ("polaroid", at("raising a child", after=70) - 0.05, at("building a business", after=70) + 0.1, "media/child.jpg", {"cap": "", "x": 90, "y": 230, "rot": -6}),
    ("split", at("building a business", after=70) - 0.05, at("you don't really", after=70) + 0.3, B(9), {}),
    ("split", at("sleepless") - 0.15, at("the tears") - 0.02, B(3), {}),
    ("full", at("the laughter") - 0.1, at("everyone") - 0.02, B(13), {}),                              # vogue event
    ("full", at("everyone") - 0.02, at("journey", end=True) + 0.15, B(17), {}),                        # handwriting a name
    ("logo", at("one year of") - 0.05, SPK_END, "media/logo_dark.png", {}),
]

# Fit every video B-roll to its slot: gentle slow-motion (up to 2x) then hold the last frame if still short
import subprocess
os.makedirs(os.path.join(PROJECT, "media", "ev"), exist_ok=True)
def fit(k, src, d):
    out = f"media/ev/e{k}.mp4"; path = os.path.join(PROJECT, out)
    sd = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                               os.path.join(PROJECT, src)], capture_output=True, text=True).stdout)
    slow = min(2.0, max(1.0, d / sd))
    key = f"{src}|{d:.3f}|{slow:.3f}"
    if not (os.path.exists(path) and os.path.exists(path + ".key") and open(path + ".key").read() == key):
        subprocess.run(["ffmpeg", "-nostdin", "-y", "-v", "error", "-i", os.path.join(PROJECT, src), "-an", "-vf",
                        f"setpts={slow:.4f}*PTS,fps=30,tpad=stop_mode=clone:stop_duration={d + 1:.2f}", "-t", f"{d + 0.2:.3f}",
                        "-c:v", "libx264", "-crf", "16", "-preset", "fast", path], check=True)
        open(path + ".key", "w").write(key)
    return out
EV = [(m, a, b, fit(k, s, b - a) if m in ("full", "page", "split") else s, x) for k, (m, a, b, s, x) in enumerate(EV)]

els, tl, cues = [], [], []
cue = lambda n, t, g: cues.append((n, round(max(0.0, t), 3), g))

# founder footage (her own audio stays exactly as recorded)
els.append(f'<div id="spkw"><video id="spk" class="clip" src="media/founder.mp4" playsinline data-start="0" data-duration="{SPK_END}" data-track-index="0" data-has-audio="true"></video></div>')

for k, (mode, a, b, src, x) in enumerate(EV):
    a, b = round(a, 3), round(b, 3); cid = f"e{k}"
    if mode in ("full", "page"):
        els.append(f'<div class="ev full" id="{cid}"><video id="{cid}-v" class="clip" src="{src}" muted playsinline data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="2"></video></div>')
        tl.append(f'tl.fromTo("#{cid}",{{opacity:0,scale:1.04}},{{opacity:1,scale:1,duration:0.28,ease:"power2.out"}},{a:.3f});')
        tl.append(f'tl.to("#{cid}",{{opacity:0,duration:0.18}},{b - 0.18:.3f});')
        cue("swipe" if mode == "page" else "snap", a - 0.05, 0.32)
    elif mode == "split":
        els.append(f'<div class="ev split" id="{cid}"><video id="{cid}-v" class="clip" src="{src}" muted playsinline data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="2"></video></div>')
        tl.append(f'tl.fromTo("#{cid}",{{yPercent:-100}},{{yPercent:0,duration:0.35,ease:"power3.out"}},{a:.3f});')
        tl.append(f'tl.to("#{cid}",{{yPercent:-100,duration:0.3,ease:"power3.in"}},{b - 0.3:.3f});')
        tl.append(f'tl.to("#spkw",{{y:600,duration:0.35,ease:"power3.out"}},{a:.3f});')
        tl.append(f'tl.to("#spkw",{{y:0,duration:0.3,ease:"power3.in"}},{b - 0.3:.3f});')
        cue("swipe", a - 0.05, 0.3)
    elif mode == "polaroid":
        cap = f'<div class="pol-cap">{html.escape(x["cap"])}</div>' if x["cap"] else ""
        els.append(f'<div class="clip ev" id="{cid}" data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="3">'
                   f'<div class="pol" id="{cid}-p" style="left:{x["x"]}px;top:{x["y"]}px"><div class="pol-img" style="background-image:url({src})"></div>{cap}</div></div>')
        tl.append(f'tl.fromTo("#{cid}-p",{{opacity:0,scale:0.6,rotation:{x["rot"] * 3},y:60}},{{opacity:1,scale:1,rotation:{x["rot"]},y:0,duration:0.45,ease:"back.out(1.7)"}},{a:.3f});')
        tl.append(f'tl.to("#{cid}-p",{{opacity:0,y:-50,duration:0.22,ease:"power2.in"}},{b - 0.22:.3f});')
        cue("shutter", a, 0.3)
    elif mode == "logo":
        els.append(f'<div class="clip ev" id="{cid}" data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="3"><img class="logo" id="{cid}-l" src="{src}" /></div>')
        tl.append(f'tl.fromTo("#{cid}-l",{{opacity:0,y:-30,scale:0.85}},{{opacity:1,y:0,scale:1,duration:0.55,ease:"back.out(1.6)"}},{a:.3f});')
        tl.append(f'tl.to("#{cid}-l",{{opacity:0,duration:0.25}},{b - 0.25:.3f});')
        cue("pop", a, 0.35)

# subtitles (reference style): small serif, 2-4 words, one purple word; dark text when a white page is up
PAGES = [(round(a, 3), round(b, 3)) for m, a, b, s, x in EV if m == "page"]
HL = {"two", "children", "little", "glosskn", "nothing", "everything", "moving", "scratch", "setbacks", "mistakes", "right",
      "mother", "brand", "health", "plan", "beautiful", "walk", "fall", "again", "okay", "pace", "moments", "first", "launch",
      "order", "believed", "adding", "grown", "sleepless", "tears", "laughter", "journey", "year", "started"}
chunks, cur = [], []
for i, w in enumerate(WORDS):
    cur.append(w)
    nxt = WORDS[i + 1] if i + 1 < len(WORDS) else None
    if (nxt is None or len(cur) >= 4 or re.search(r"[.,?!]$", w["w"]) or nxt["s"] - w["e"] > 0.35
            or (len(cur) >= 3 and sum(len(x["w"]) + 1 for x in cur) > 17)):
        chunks.append(cur); cur = []
for k, c in enumerate(chunks):
    a = c[0]["s"] - 0.05
    b = min(c[-1]["e"] + 0.25, chunks[k + 1][0]["s"] - 0.05) if k + 1 < len(chunks) else SPK_END
    dark = any(pa - 0.05 <= (a + b) / 2 <= pb for pa, pb in PAGES)
    hl = next((j for j, w in enumerate(c) if norm(w["w"]) in HL), -1)
    txt = " ".join(f'<span class="{"hl" if j == hl else ""}">{html.escape("I" if w["w"] == "i" else w["w"].rstrip(",."))}</span>' for j, w in enumerate(c))
    els.append(f'<div class="clip subc" data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="6"><div class="sub{" dark" if dark else ""}" id="c{k}">{txt}</div></div>')
    tl.append(f'tl.fromTo("#c{k}",{{opacity:0,y:14}},{{opacity:1,y:0,duration:0.18,ease:"power2.out"}},{a:.3f});')

# end card: white, logo + "1 year"
a = SPK_END - 0.15
els.append(f'<div class="clip" id="end" data-start="{a:.3f}" data-duration="{DUR - a:.3f}" data-track-index="7"><div class="end">'
           '<div class="end-k" id="end-k">happy first birthday</div><div class="end-n" id="end-n">1</div>'
           '<div class="end-s" id="end-s">year &amp; just getting started</div><img class="end-logo" id="end-logo" src="media/logo_dark.png" /></div></div>')
tl.append(f'tl.fromTo("#end .end",{{opacity:0}},{{opacity:1,duration:0.4}},{a:.3f});')
for i, (sel, d) in enumerate([("#end-k", 0.1), ("#end-n", 0.3), ("#end-s", 0.6), ("#end-logo", 0.9)]):
    tl.append(f'tl.fromTo("{sel}",{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.5,ease:"power2.out"}},{a + d:.3f});')
cue("ding", a + 0.3, 0.35)

CSS = open(os.path.join(HERE, "style2.css")).read()
page = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="vendor/gsap.min.js"></script>
    <style>
{CSS}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="{W}" data-height="{H}">
      <audio id="bed" src="media/bed.wav" data-start="0" data-duration="{DUR}" data-track-index="1"></audio>
      {chr(10).join('      ' + e for e in els).strip()}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      {chr(10).join('      ' + x for x in tl).strip()}
      tl.set({{}}, {{}}, {DUR});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
open(os.path.join(PROJECT, "index.html"), "w").write(page)
json.dump(dict(duration=DUR, end_at=SPK_END, cues=sorted(cues, key=lambda c: c[1])), open(os.path.join(PROJECT, "media", "cues.json"), "w"), indent=1)
print("events", len(EV), "subtitle chunks", len(chunks), "cues", len(cues), "duration", DUR)
