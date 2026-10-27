"""GLOSSKN 1st-birthday reel: draft composition. Founder footage + voiceover come later, so every line is timed
at a natural emotional pace and the founder slots are labelled placeholders. Writes index.html + timeline.json."""
import html, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__)); PROJECT = os.path.dirname(HERE)
W, H = 1080, 1920
WPS, BREATH = 2.3, 0.55  # words per second, pause after each line

# (line, visual) — visual keys are handled below; None = founder speaking full screen
SCRIPT = [
    ("Looking back at pictures from the last year, I sometimes wonder… how did so much happen in such little time?", "photos123"),
    ("Somewhere along the way, I found myself raising two babies.", None),
    ("One was my little one… and the other was GLOSSKN.", "child_logo"),
    ("And honestly, nothing could have prepared me for this year.", None),
    ("There were days when I felt like I was doing everything, and somehow, still not doing enough.", None),
    ("Between being a mother, managing everyday life, and building a brand, things rarely went according to plan.", "delivery"),
    ("But GLOSSKN gave me something that was truly my own.", "name"),
    ("A dream to nurture, ideas to explore, and a part of myself I didn't want to lose along the way.", None),
    ("After years of working in the beauty industry, there were things I wanted to do differently.", None),
    ("And GLOSSKN was my chance to turn those thoughts into something real.", "package"),
    ("Of course, there were mistakes, setbacks, moments of doubt… and so much learning.", "samples"),
    ("But one thing this year has taught me is how important it is to remember your why.", None),
    ("Why you started. What you believe in. And what you want to stand for.", "why_stack"),
    ("Because when things get difficult, that purpose is what brings you back.", None),
    ("And strangely, watching my little one grow reminded me of something I had forgotten.", "child2"),
    ("Children don't wait to have everything figured out. They fall, get up, and try again.", None),
    ("And that's exactly what this year has been for me.", None),
    ("Somewhere between raising a child and building a dream, I didn't just watch them grow… I grew too.", None),
    ("So here's to the little wins,", "shopify"),
    ("the lessons, the people who believed in us,", "review"),
    ("and everything that's still to come.", None),
    ("Happy first birthday, GLOSSKN.", "endcard"),
]
HIGHLIGHT = {"pictures", "two", "babies", "little", "one", "glosskn", "nothing", "enough", "plan", "own", "dream",
             "differently", "real", "learning", "why", "started", "believe", "stand", "purpose", "forgotten", "try",
             "again", "grew", "too", "wins", "believed", "come", "birthday"}

# ------------------------------------------------------------------ timing
t, lines = 0.6, []
for i, (text, vis) in enumerate(SCRIPT):
    words = text.split()
    d = len(words) / WPS + text.count("…") * 0.45
    lines.append(dict(i=i, text=text, vis=vis, a=round(t, 3), b=round(t + d, 3), words=words))
    t += d + BREATH
END_CARD = 3.2
lines[-1]["b"] = round(lines[-1]["a"] + END_CARD, 3)
DUR = round(lines[-1]["b"] + 0.4, 3)

els, tl = [], []


def clip(cid, a, b, inner, cls="", track=3, style=""):
    els.append(f'<div id="{cid}" class="clip {cls}" style="{style}" data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="{track}">{inner}</div>')


# ------------------------------------------------------------------ founder placeholders (one per line)
for L in lines[:-1]:
    clip(f"ph{L['i']}", L["a"] - 0.25 if L["i"] else 0, (lines[L["i"] + 1]["a"] - 0.25), f'<div class="ph"><div class="ph-box">'
         f'<div class="ph-k">FOUNDER FOOTAGE</div><div class="ph-n">line {L["i"] + 1}</div></div></div>', "phc", track=0)

# ------------------------------------------------------------------ subtitles: 2–4 word chunks, one purple word
def chunks(words):
    out, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= 4 or re.search(r"[.,?…]$", w) or (len(cur) >= 3 and len(" ".join(cur)) > 16):
            out.append(cur); cur = []
    if cur: out.append(cur)
    return out


for L in lines[:-1]:
    if L["vis"] == "why_stack":
        continue
    cs = chunks(L["words"]); per = (L["b"] - L["a"]) / len(L["words"]); t0 = L["a"]
    for k, c in enumerate(cs):
        a, b = t0, t0 + per * len(c) + (0.2 if k == len(cs) - 1 else 0)
        hl = next((j for j, w in enumerate(c) if re.sub(r"\W", "", w.lower()) in HIGHLIGHT), -1)
        spans = " ".join(f'<span class="{"hl" if j == hl else ""}">{html.escape(w)}</span>' for j, w in enumerate(c))
        cid = f"s{L['i']}_{k}"
        clip(cid, a, b, f'<div class="sub" id="{cid}-t">{spans}</div>', "subc", track=6)
        tl.append(f'tl.fromTo("#{cid}-t",{{opacity:0,y:18}},{{opacity:1,y:0,duration:0.22,ease:"power2.out"}},{a:.3f});')
        t0 = b if k < len(cs) - 1 else t0


def at(L, word_idx):
    return L["a"] + (L["b"] - L["a"]) * word_idx / len(L["words"])


# ------------------------------------------------------------------ visuals
def polaroid(pid, src, a, b, x, y, w, rot, caption=""):
    cap = f'<div class="pol-cap">{caption}</div>' if caption else ""
    clip(pid, a, b, f'<div class="pol" id="{pid}-p" style="left:{x}px;top:{y}px;width:{w}px">'
                    f'<div class="pol-img" style="background-image:url({src})"></div>{cap}</div>', "polc", track=4)
    tl.append(f'tl.fromTo("#{pid}-p",{{opacity:0,scale:0.7,rotation:{rot * 3},y:90}},{{opacity:1,scale:1,rotation:{rot},y:0,duration:0.55,ease:"back.out(1.5)"}},{a:.3f});')
    tl.append(f'tl.fromTo("#{pid}-p",{{x:0}},{{x:{-rot * 4},duration:{max(0.5, b - a - 0.9):.3f},ease:"sine.inOut",immediateRender:false}},{a + 0.55:.3f});')
    tl.append(f'tl.to("#{pid}-p",{{opacity:0,y:-60,duration:0.3,ease:"power2.in"}},{b - 0.3:.3f});')


def broll(bid, src, a, b, mode="full"):
    if mode == "panel":
        inner = f'<div class="panel" id="{bid}-w"><video id="{bid}-v" class="clip" src="{src}" muted playsinline data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="2"></video></div>'
        els.append(f'<div class="brw" id="{bid}">{inner}</div>')
        tl.append(f'tl.fromTo("#{bid}-w",{{opacity:0,scale:0.85,y:80}},{{opacity:1,scale:1,y:0,duration:0.5,ease:"power3.out"}},{a:.3f});')
        tl.append(f'tl.to("#{bid}-w",{{opacity:0,scale:0.95,duration:0.3}},{b - 0.3:.3f});')
    else:
        els.append(f'<div class="brw full" id="{bid}"><video id="{bid}-v" class="clip" src="{src}" muted playsinline data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="2"></video></div>')
        tl.append(f'tl.fromTo("#{bid}",{{opacity:0,scale:1.06}},{{opacity:1,scale:1,duration:0.45,ease:"power2.out"}},{a:.3f});')
        tl.append(f'tl.fromTo("#{bid}",{{scale:1}},{{scale:1.05,duration:{max(0.5, b - a - 0.75):.3f},ease:"none",immediateRender:false}},{a + 0.45:.3f});')
        tl.append(f'tl.to("#{bid}",{{opacity:0,duration:0.3}},{b - 0.3:.3f});')


for L in lines:
    a, b, v = L["a"], L["b"], L["vis"]
    nxt = lines[L["i"] + 1]["a"] - 0.25 if L["i"] + 1 < len(lines) else DUR
    if v == "photos123":  # one by one on "pictures ... last year ... wonder"
        for k, (src, x, y, rot) in enumerate([("media/photo1.jpg", 70, 280, -7), ("media/photo2.jpg", 430, 360, 6),
                                              ("media/photo3.jpg", 250, 560, -3)]):
            polaroid(f"p{k + 1}", src, at(L, [3, 7, 10][k]), b + 0.2, x, y, 500, rot)
    elif v == "child_logo":
        polaroid("pchild", "media/child.jpg", at(L, 1), at(L, 5) + 0.35, 260, 300, 560, -4, "my little one")
        clip("logo1", at(L, 6), nxt, '<img class="logo-big" id="logo1-i" src="media/logo_white.png" />', "logoc", track=5)
        tl.append(f'tl.fromTo("#logo1-i",{{opacity:0,scale:0.8,y:40}},{{opacity:1,scale:1,y:0,duration:0.6,ease:"power3.out"}},{at(L, 6):.3f});')
    elif v in ("delivery", "name", "package", "review"):
        broll(f"b_{v}", f"media/{v}.mp4", a - 0.1, nxt)
    elif v == "shopify":
        broll("b_shopify", "media/shopify.mp4", a - 0.1, nxt, "panel")
    elif v == "samples":
        polaroid("psamples", "media/samples.jpg", at(L, 2), nxt, 250, 320, 580, 5, "the first samples")
    elif v == "child2":
        polaroid("pchild2", "media/child.jpg", at(L, 4), nxt, 270, 330, 540, 4)
    elif v == "why_stack":
        parts = ["Why you started.", "What you believe in.", "What you want to stand for."]
        inner = "".join(f'<div class="why" id="why{k}">{html.escape(p)}</div>' for k, p in enumerate(parts))
        clip("whystack", a, nxt, f'<div class="whys">{inner}</div>', track=5)
        offs = [0, 4, 8]
        for k in range(3):
            tl.append(f'tl.fromTo("#why{k}",{{opacity:0,y:40,filter:"blur(8px)"}},{{opacity:1,y:0,filter:"blur(0px)",duration:0.6,ease:"power2.out"}},{at(L, offs[k]):.3f});')
    elif v == "endcard":
        clip("end", a - 0.2, DUR, '<div class="end"><div class="end-glow"></div><div class="end-1" id="end-1">Happy first birthday</div>'
             '<div class="end-n" id="end-n">1</div><div class="end-s" id="end-s">year of GLOSSKN</div>'
             '<img class="end-logo" id="end-logo" src="media/logo_white.png" /></div>', track=7)
        tl.append(f'tl.fromTo("#end",{{opacity:0}},{{opacity:1,duration:0.6}},{a - 0.2:.3f});')
        tl.append(f'tl.fromTo("#end-n",{{opacity:0,scale:0.6}},{{opacity:1,scale:1,duration:0.8,ease:"back.out(1.6)"}},{a + 0.2:.3f});')
        tl.append(f'tl.fromTo("#end-1",{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.6}},{a:.3f});')
        tl.append(f'tl.fromTo("#end-s",{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.6}},{a + 0.5:.3f});')
        tl.append(f'tl.fromTo("#end-logo",{{opacity:0,y:-30}},{{opacity:1,y:0,duration:0.6}},{a + 0.8:.3f});')

CSS = open(os.path.join(HERE, "style.css")).read()
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
      <audio id="music" src="media/music.wav" data-start="0" data-duration="{DUR}" data-track-index="1"></audio>
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
json.dump(dict(duration=DUR, lines=[{k: L[k] for k in ("i", "text", "vis", "a", "b")} for L in lines]),
          open(os.path.join(PROJECT, "timeline.json"), "w"), indent=1)
print("lines", len(lines), "duration", DUR)
