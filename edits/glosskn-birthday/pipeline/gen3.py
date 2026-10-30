"""GLOSSKN 1st-birthday reel v3 — new founder take (media/founder_v3.mp4) + numbered assets from the zip.
Placement exactly as briefed: polaroids above her head, the little one's polaroid beside her, logo above her head,
half-frame (split) and full-overlay B-roll, plain founder shots with a subtle zoom elsewhere. White brand theme."""
import html, json, os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__)); PROJECT = os.path.dirname(HERE)
W, H = 1080, 1920
SPK_END = 51.2; END_CARD = 3.0; DUR = round(SPK_END + END_CARD, 3)
WORDS = json.load(open(os.path.join(PROJECT, "data", "words_v3.json")))
norm = lambda s: re.sub(r"[^a-z0-9']", "", s.lower())
TOK = [norm(w["w"]) for w in WORDS]
Z = "media/zip_in/Birthday video files/"


def at(phrase, after=0.0, end=False):
    p = [norm(x) for x in phrase.split()]
    for i in range(len(TOK) - len(p) + 1):
        if WORDS[i]["s"] >= after and TOK[i:i + len(p)] == p:
            return WORDS[i + len(p) - 1]["e"] if end else WORDS[i]["s"]
    raise ValueError(phrase)


SPLIT_Y, POL_Y = 250, 220   # how far she slides down for a half-frame / for polaroids above her head
# (mode, start, end, source, extra)   modes: polrow | polaroid | logo | full | split   (images or videos)
EV = [
    ("polrow", 1.55, at("such little time", end=True) + 0.15, None,
     {"items": [(Z + "1.jpeg", 40, 170, -6, 0.0), (Z + "2.jpeg", 385, 125, 3, 0.45), (Z + "3.jpeg", 730, 175, 7, 0.9)], "w": 310}),
    ("polaroid", at("one was the little") - 0.05, at("the other one") - 0.05, Z + "4.jpeg", {"x": 715, "y": 520, "rot": 6, "w": 340}),
    ("logo", at("the other one"), at("nothing could") - 0.1, "media/logo_dark.png", {}),
    ("full", at("there were days") - 0.05, at("but the needle"), Z + "6.jpeg", {}),
    ("full", at("but the needle"), at("there were setbacks") - 0.04, Z + "7.jpeg", {}),
    ("split", at("there were setbacks") - 0.04, at("there were mistakes") - 0.04, Z + "8.jpeg", {}),
    ("split", at("there were mistakes") - 0.04, at("and the days") + 0.05, Z + "9.mp4", {"ss": 0.0}),
    ("split", at("between being") - 0.1, at("building a brand") - 0.05, "media/v3/10.jpg", {}),
    ("split", at("building a brand") - 0.05, at("things hardly") - 0.1, Z + "11.jpeg", {}),
    ("full", at("my baby's first") - 0.05, at("our first launch") - 0.02, Z + "12.mp4", {"ss": 7.0, "speed": 1.8}),
    ("full", at("our first launch") - 0.02, at("our first order") - 0.04, Z + "13.mp4", {"ss": 1.2}),
    ("split", at("our first order") - 0.04, at("someone who") - 0.03, Z + "14.mp4", {"ss": 2.0, "pos": "30% 50%"}),
    ("full", at("someone who") - 0.03, at("and suddenly") - 0.05, Z + "15.mp4", {"ss": 1.8}),
    ("full", at("and suddenly") - 0.05, at("adding up", end=True) + 0.2, Z + "16.mp4", {"ss": 0.0}),
    ("polrow", at("sleepless") - 0.12, at("everyone") - 0.05, None,
     {"items": [(Z + "17.jpeg", 80, 150, -5, 0.0), (Z + "18.jpeg", 590, 175, 5, at("the tears") - at("sleepless") + 0.05)], "w": 410}),
    ("full", at("everyone") - 0.05, at("one year of") - 0.06, Z + "19.mp4", {"ss": 1.4}),
    ("logo", at("one year of") + 0.05, SPK_END - 0.1, "media/logo_dark.png", {}),
]
# subtle push-ins on the plain founder shots (none on "am I doing any of this right?")
ZOOMS = [(at("I was literally") - 0.1, at("one was the little") - 0.05), (at("and honestly"), at("there were days") - 0.05),
         (at("things hardly") - 0.1, at("my baby's first") - 0.05), (at("one year of") - 0.06, SPK_END)]

os.makedirs(os.path.join(PROJECT, "media", "ev3"), exist_ok=True)
def fit(k, src, d, ss=0.0, speed=None):
    """Cut a clip to its slot: optional speed-up, else gentle slow-mo (<=2x) then hold the last frame."""
    out = f"media/ev3/e{k}.mp4"; path = os.path.join(PROJECT, out)
    sd = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                               os.path.join(PROJECT, src)], capture_output=True, text=True).stdout) - ss
    f = 1 / speed if speed else min(2.0, max(1.0, d / sd))
    key = f"{src}|{d:.3f}|{ss}|{f:.3f}"
    if not (os.path.exists(path) and os.path.exists(path + ".key") and open(path + ".key").read() == key):
        mi = ",minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1" if f > 1.15 else ",fps=30"
        subprocess.run(["ffmpeg", "-nostdin", "-y", "-v", "error", "-ss", str(ss), "-i", os.path.join(PROJECT, src), "-an", "-vf",
                        f"setpts={f:.4f}*(PTS-STARTPTS){mi},hqdn3d=1.5:1.5:3:3,eq=saturation=1.04,"
                        f"tpad=stop_mode=clone:stop_duration={d + 1:.2f}", "-t", f"{d + 0.2:.3f}",
                        "-c:v", "libx264", "-crf", "14", "-preset", "fast", path], check=True)
        open(path + ".key", "w").write(key)
    return out

is_vid = lambda s: s and s.endswith(".mp4")
EV = [(m, round(a, 3), round(b, 3), fit(k, s, b - a, x.get("ss", 0.0), x.get("speed")) if is_vid(s) else s, x)
      for k, (m, a, b, s, x) in enumerate(EV)]
els, tl, cues = [], [], []
cue = lambda n, t, g: cues.append((n, round(max(0.0, t), 3), g))
media = lambda cid, src, a, b, pos="50% 50%": (
    f'<video id="{cid}-v" class="clip" src="{src}" muted playsinline data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="2" style="object-position:{pos}"></video>'
    if is_vid(src) else f'<img id="{cid}-v" src="{src}" style="object-position:{pos}" />')

els.append(f'<div id="spkw"><video id="spk" class="clip" src="media/v3/founder.mp4" playsinline data-start="0" data-duration="{SPK_END}" data-track-index="0" data-has-audio="true"></video></div>')
tl.append('tl.set("#spk",{scale:1},0);')
for a, b in ZOOMS:
    tl.append(f'tl.to("#spk",{{scale:1.07,duration:{b - a:.3f},ease:"none"}},{a:.3f});')
    tl.append(f'tl.set("#spk",{{scale:1}},{b:.3f});')

for k, (mode, a, b, src, x) in enumerate(EV):
    cid = f"e{k}"; wrap = f'data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="{3 + k % 2}"'
    if is_vid(src):   # the <video> carries the timing; the wrapper is an untimed container shown only in its slot
        wrap = ""; tl.append(f'tl.set("#{cid}",{{opacity:0}},0);tl.set("#{cid}",{{opacity:1}},{a:.3f});tl.set("#{cid}",{{opacity:0}},{b:.3f});')
    prev = EV[k - 1] if k else None; nxt = EV[k + 1] if k + 1 < len(EV) else None
    if mode == "full":
        els.append(f'<div class="{"clip " if wrap else ""}ev full" id="{cid}" {wrap}>{media(cid, src, a, b)}</div>')
        tl.append(f'tl.fromTo("#{cid}",{{opacity:0,scale:1.06}},{{opacity:1,scale:1,duration:0.3,ease:"power2.out"}},{a:.3f});')
        if not is_vid(src):  # Ken Burns on stills
            tl.append(f'tl.fromTo("#{cid}-v",{{scale:1}},{{scale:1.08,duration:{b - a:.3f},ease:"none"}},{a:.3f});')
        cue("whoosh" if k % 2 else "swish", a - 0.08, 0.22)
    elif mode == "split":
        chain_in = prev and prev[0] == "split" and abs(prev[2] - a) < 0.15
        chain_out = nxt and nxt[0] == "split" and abs(nxt[1] - b) < 0.15
        els.append(f'<div class="{"clip " if wrap else ""}ev split" id="{cid}" {wrap}>{media(cid, src, a, b, x.get("pos", "50% 50%"))}</div>')
        if chain_in:
            tl.append(f'tl.fromTo("#{cid}",{{opacity:0}},{{opacity:1,duration:0.15}},{a:.3f});'); cue("snap", a - 0.03, 0.25)
        else:
            tl.append(f'tl.fromTo("#{cid}",{{yPercent:-100}},{{yPercent:0,duration:0.38,ease:"power3.out"}},{a:.3f});')
            tl.append(f'tl.to("#spkw",{{y:{SPLIT_Y},duration:0.38,ease:"power3.out"}},{a:.3f});'); cue("swipe", a - 0.05, 0.3)
        if not chain_out:
            tl.append(f'tl.to("#{cid}",{{yPercent:-100,duration:0.3,ease:"power3.in"}},{b - 0.3:.3f});')
            tl.append(f'tl.to("#spkw",{{y:0,duration:0.3,ease:"power3.in"}},{b - 0.3:.3f});')
        if not is_vid(src):
            tl.append(f'tl.fromTo("#{cid}-v",{{scale:1.02}},{{scale:1.09,duration:{b - a:.3f},ease:"none"}},{a:.3f});')
    elif mode in ("polrow", "polaroid"):
        items = x["items"] if mode == "polrow" else [(src, x["x"], x["y"], x["rot"], 0.0)]
        w = x.get("w", 360); parts = []
        for j, (img, px, py, rot, dl) in enumerate(items):
            parts.append(f'<div class="pol" id="{cid}-p{j}" style="left:{px}px;top:{py}px;width:{w}px"><div class="pol-img" style="background-image:url(\'{img}\')"></div></div>')
            tl.append(f'tl.fromTo("#{cid}-p{j}",{{opacity:0,scale:0.55,rotation:{rot * 3},y:70}},{{opacity:1,scale:1,rotation:{rot},y:0,duration:0.5,ease:"back.out(1.6)"}},{a + dl:.3f});')
            tl.append(f'tl.to("#{cid}-p{j}",{{opacity:0,y:-60,duration:0.24,ease:"power2.in"}},{b - 0.24 - 0.05 * (len(items) - 1 - j):.3f});')
            cue("shutter", a + dl, 0.3)
        els.append(f'<div class="clip ev" id="{cid}" {wrap}>{"".join(parts)}</div>')
        if mode == "polrow":   # she slides down so the photos sit above her head
            tl.append(f'tl.to("#spkw",{{y:{POL_Y},duration:0.45,ease:"power3.out"}},{a - 0.1:.3f});')
            tl.append(f'tl.to("#spkw",{{y:0,duration:0.35,ease:"power3.inOut"}},{b - 0.3:.3f});')
    elif mode == "logo":
        els.append(f'<div class="clip ev" id="{cid}" {wrap}><img class="logo" id="{cid}-l" src="{src}" /></div>')
        tl.append(f'tl.fromTo("#{cid}-l",{{opacity:0,y:-30,scale:0.85}},{{opacity:1,y:0,scale:1,duration:0.55,ease:"back.out(1.6)"}},{a:.3f});')
        tl.append(f'tl.to("#{cid}-l",{{opacity:0,duration:0.25}},{b - 0.25:.3f});')
        cue("pop", a, 0.35)

# subtitles (reference style): small serif, 2-4 words, one purple word
HL = {"pictures", "little", "two", "children", "glosskn", "nothing", "everything", "moving", "setbacks", "mistakes", "right",
      "mother", "life", "brand", "health", "plan", "moments", "first", "launch", "order", "believed", "adding", "sleepless",
      "tears", "laughter", "journey", "thank", "year", "started"}
chunks, cur = [], []
for i, w in enumerate(WORDS):
    cur.append(w); nxt = WORDS[i + 1] if i + 1 < len(WORDS) else None
    if (nxt is None or len(cur) >= 4 or re.search(r"[.,?!]$", w["w"]) or nxt["s"] - w["e"] > 0.35
            or (len(cur) >= 3 and sum(len(x["w"]) + 1 for x in cur) > 17)):
        chunks.append(cur); cur = []
for k, c in enumerate(chunks):
    a = c[0]["s"] - 0.05
    b = min(c[-1]["e"] + 0.25, chunks[k + 1][0]["s"] - 0.05) if k + 1 < len(chunks) else SPK_END - 0.1
    hl = next((j for j, w in enumerate(c) if norm(w["w"]) in HL), -1)
    txt = " ".join(f'<span class="{"hl" if j == hl else ""}">{html.escape("I" if w["w"] == "i" else w["w"].rstrip(",."))}</span>' for j, w in enumerate(c))
    els.append(f'<div class="clip subc" data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="6"><div class="sub" id="c{k}">{txt}</div></div>')
    tl.append(f'tl.fromTo("#c{k}",{{opacity:0,y:14}},{{opacity:1,y:0,duration:0.18,ease:"power2.out"}},{a:.3f});')

a = SPK_END - 0.15
els.append(f'<div class="clip" id="end" data-start="{a:.3f}" data-duration="{DUR - a:.3f}" data-track-index="7"><div class="end">'
           '<div class="end-k" id="end-k">happy first birthday</div><div class="end-n" id="end-n">1</div>'
           '<div class="end-s" id="end-s">year &amp; just getting started</div><img class="end-logo" id="end-logo" src="media/logo_dark.png" /></div></div>')
tl.append(f'tl.fromTo("#end .end",{{opacity:0}},{{opacity:1,duration:0.4}},{a:.3f});')
for i, (sel, d) in enumerate([("#end-k", 0.1), ("#end-n", 0.3), ("#end-s", 0.6), ("#end-logo", 0.9)]):
    tl.append(f'tl.fromTo("{sel}",{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.5,ease:"power2.out"}},{a + d:.3f});')
cue("sparkle", a + 0.25, 0.3); cue("ding", a + 0.35, 0.3)

CSS = open(os.path.join(HERE, "style3.css")).read()
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
print("events", len(EV), "subs", len(chunks), "cues", len(cues), "dur", DUR)
