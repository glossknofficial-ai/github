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


SPLIT_Y, POL_Y = 250, 220
SPLITB_Y = 330   # how far she moves up when the picture takes the lower half   # how far she slides down for a half-frame / for polaroids above her head
# (mode, start, end, source, extra)   modes: polrow | polaroid | logo | full | split   (images or videos)
Z2 = "media/zip2/Birthday video files/"
EV = [
    ("polrow", 1.55, at("such little time", end=True) + 0.15, None,
     {"items": [(Z2 + "a.jpeg", 28, 42, -6, 0.0), (Z2 + "b.jpeg", 375, 18, 3, 0.45), (Z2 + "c.jpeg", 722, 48, 7, 0.9)], "w": 330}),
    ("polaroid", at("one was the little") - 0.05, at("the other one") - 0.05, Z2 + "d.jpeg", {"x": 715, "y": 520, "rot": 6, "w": 340}),
    # four photos one by one in a rounded clip card
    ("box", at("there were days") - 0.05, at("when I felt") - 0.02, Z2 + "e.jpeg", {"still": True, "w": 860, "ar": 0.75}),
    ("box", at("when I felt") - 0.02, at("I was doing") - 0.02, Z2 + "f.jpeg", {"still": True, "w": 860, "ar": 0.75}),
    ("box", at("I was doing") - 0.02, at("in my capacity") - 0.02, Z2 + "g.jpeg", {"still": True, "w": 860, "ar": 0.75}),
    ("box", at("in my capacity") - 0.02, at("but the needle"), Z2 + "h.jpeg", {"still": True, "w": 860, "ar": 0.75}),
    ("split", at("there were setbacks") - 0.04, at("there were mistakes") - 0.04, Z2 + "i.jpeg", {}),
    ("split", at("there were mistakes") - 0.04, at("and the days") + 0.05, Z2 + "j.jpeg", {}),
    ("split", at("between being") - 0.1, at("managing") - 0.05, Z2 + "k.jpeg", {}),
    ("split", at("managing") - 0.05, at("building a brand") - 0.05, Z2 + "l.jpeg", {}),
    ("split", at("building a brand") - 0.05, at("things hardly") - 0.1, Z2 + "m.mp4", {"ss": 0.5}),
    ("full", at("my baby's first") - 0.05, at("our first launch") - 0.02, Z2 + "n.mp4", {"ss": 0.4}),
    ("full", at("our first launch") - 0.02, at("our first order") - 0.04, Z2 + "o.mp4", {"ss": 12.2}),
    ("split", at("our first order") - 0.04, at("someone who") - 0.03, Z2 + "p.jpeg", {}),
    ("full", at("someone who") - 0.03, at("believed in") - 0.02, Z2 + "q.mp4", {"ss": 3.6}),
    ("full", at("believed in") - 0.02, at("what we had") - 0.02, Z2 + "s.jpeg", {}),
    ("full", at("what we had") - 0.02, at("and suddenly") - 0.05, Z2 + "r.mp4", {"ss": 1.7}),
    # "all those little things started adding up": cards pile up on the page
    ("stack", at("and suddenly") - 0.05, at("adding up", end=True) + 0.25, None,
     {"items": [(Z2 + "t.jpeg", 0.0, -5, 620, 0.75, -120, -80, {}), (Z2 + "u.jpeg", 0.7, 4, 620, 0.75, 130, -20, {}),
                (Z2 + "v.mp4", 1.45, -3, 560, 0.5625, -90, 40, {"ss": 1.2}), (Z2 + "w.mp4", 2.2, 5, 580, 0.5625, 100, 10, {"ss": 3.0})]}),
    ("polrow", at("sleepless") - 0.12, at("everyone") - 0.05, None,
     {"items": [(Z2 + "x.jpeg", 90, 22, -5, 0.0), (Z2 + "y.jpeg", 620, 40, 5, at("the tears") - at("sleepless") + 0.05)], "w": 360}),
    ("splitb", at("everyone") - 0.05, at("thank you") - 0.05, Z2 + "z.jpeg", {}),
    ("splitb", at("thank you") - 0.05, at("one year of") - 0.06, Z2 + "za.jpeg", {}),
]
COVER = ("full", "split", "splitb", "box", "stack")      # layouts that take over the frame (fully or the top half)
# subtle push-ins on the plain founder shots (none on "am I doing any of this right?")
ZOOMS_UNUSED = [(at("I was literally") - 0.1, at("one was the little") - 0.05), (at("and honestly"), at("there were days") - 0.05),
         (at("things hardly") - 0.1, at("my baby's first") - 0.05), (at("one year of") - 0.06, SPK_END)]

os.makedirs(os.path.join(PROJECT, "media", "ev3"), exist_ok=True)
def fit(k, src, d, ss=0.0, speed=None, blur=0, mblur=0):
    """Cut a clip to its slot: optional speed-up, else gentle slow-mo (<=2x) then hold the last frame."""
    out = f"media/ev3/e{k}.mp4"; path = os.path.join(PROJECT, out)
    sd = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                               os.path.join(PROJECT, src)], capture_output=True, text=True).stdout) - ss
    f = 1 / speed if speed else min(2.0, max(1.0, d / sd))
    key = f"{src}|{d:.3f}|{ss}|{f:.3f}|{blur}|{mblur}"
    if not (os.path.exists(path) and os.path.exists(path + ".key") and open(path + ".key").read() == key):
        mi = ",minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1" if f > 1.15 else ",fps=30"
        subprocess.run(["ffmpeg", "-nostdin", "-y", "-v", "error", "-ss", str(ss), "-i", os.path.join(PROJECT, src), "-an", "-vf",
                        f"{f'tmix=frames={mblur},' if mblur else ''}setpts={f:.4f}*(PTS-STARTPTS){mi},hqdn3d=1.5:1.5:3:3,eq=saturation=1.04,{f'gblur=sigma={blur},' if blur else ''}"
                        f"tpad=stop_mode=clone:stop_duration={d + 1:.2f}", "-t", f"{d + 0.2:.3f}",
                        "-c:v", "libx264", "-crf", "14", "-preset", "fast", path], check=True)
        open(path + ".key", "w").write(key)
    return out

is_vid = lambda s: s and s.endswith(".mp4")
# stills never linger: at most 2 s on screen
EV = [(m, a, min(b, a + 2.0) if (m in COVER and s and not is_vid(s)) else b, s, x) for m, a, b, s, x in EV]
# never flash the base video for a split second: close short gaps between consecutive cover layouts
for k in range(len(EV) - 1):
    m, a, b, s, x = EV[k]; n = EV[k + 1]
    if m in COVER and n[0] in COVER and 0 < n[1] - b < 0.7: EV[k] = (m, a, n[1], s, x)
EV = [(m, round(a, 3), round(b, 3), fit(k, s, b - a, x.get("ss", 0.0), x.get("speed"), x.get("blur", 0), x.get("mblur", 0)) if is_vid(s) else s, x)
      for k, (m, a, b, s, x) in enumerate(EV)]
for k, (m, a, b, s_, x) in enumerate(EV):
    if m == "stack":
        x["items"] = [(fit(f"{k}_{j}", src, b - a - dl, o.get("ss", 0.0)) if is_vid(src) else src, dl, rot, w, ar, dx, dy, o)
                      for j, (src, dl, rot, w, ar, dx, dy, o) in enumerate(x["items"])]
els, tl, cues = [], [], []
cue = lambda n, t, g: cues.append((n, round(max(0.0, t), 3), g))
media = lambda cid, src, a, b, pos="50% 50%": (
    f'<video id="{cid}-v" class="clip" src="{src}" muted playsinline data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="2" style="object-position:{pos}"></video>'
    if is_vid(src) else f'<img id="{cid}-v" src="{src}" style="object-position:{pos}" />')

els.append(f'<div id="spkw"><video id="spk" class="clip" src="media/v3/founder_baked.mp4" playsinline data-start="0" data-duration="{SPK_END}" data-track-index="0" data-has-audio="true"></video></div>')
tl.append('tl.set("#spk",{scale:1},0);')
for a, b in []:
    tl.append(f'tl.to("#spk",{{scale:1.07,duration:{b - a:.3f},ease:"none"}},{a:.3f});')
    tl.append(f'tl.set("#spk",{{scale:1}},{b:.3f});')

for k, (mode, a, b, src, x) in enumerate(EV):
    cid = f"e{k}"; wrap = f'data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="{3 + k % 2}"'
    if is_vid(src):   # the <video> carries the timing; the wrapper is an untimed container shown only in its slot
        wrap = ""; tl.append(f'tl.set("#{cid}",{{opacity:0}},0);tl.set("#{cid}",{{opacity:1}},{a:.3f});tl.set("#{cid}",{{opacity:0}},{b:.3f});')
    prev = EV[k - 1] if k else None; nxt = EV[k + 1] if k + 1 < len(EV) else None
    from_cover = prev and prev[0] in COVER and abs(prev[2] - a) < 0.05     # cut straight from another layout
    to_cover = nxt and nxt[0] in COVER and abs(nxt[1] - b) < 0.05
    kb = f'tl.fromTo("#{cid}-v",{{scale:1.0}},{{scale:1.07,duration:{b - a:.3f},ease:"none"}},{a:.3f});' if not is_vid(src) else ""
    if mode == "full":   # hard cut in, settle from a slight push
        els.append(f'<div class="{"clip " if wrap else ""}ev full" id="{cid}" {wrap}>{media(cid, src, a, b)}</div>')
        if not x.get("still"):   # stills marked "still" are shown flat: no push or Ken Burns
            tl.append(f'tl.fromTo("#{cid}",{{scale:1.05}},{{scale:1,duration:0.4,ease:"power2.out"}},{a:.3f});'); tl.append(kb)
        if from_cover and prev[0] in ("split", "splitb"): tl.append(f'tl.set("#spkw",{{y:0}},{a:.3f});')
        cue("click", a - 0.01, 0.2)
    elif mode == "box":  # reference-style rounded card on a soft page
        w = x["w"]; h = round(w / x["ar"]); top = (1920 - h) // 2 + (70 if x.get("logo") else -40)
        logo = '<img class="box-logo" id="%s-l" src="media/v3/logo3d.png" />' % cid if x.get("logo") else ""
        els.append(f'<div class="{"clip " if wrap else ""}ev boxp" id="{cid}" {wrap}>{logo}<div class="card" id="{cid}-c" '
                   f'style="left:{(1080 - w) // 2}px;top:{top}px;width:{w}px;height:{h}px">{media(cid, src, a, b)}</div></div>')
        tl.append(f'tl.fromTo("#{cid}-c",{{scale:0.93,y:30}},{{scale:1,y:0,duration:0.45,ease:"power3.out"}},{a:.3f});')
        if not x.get("still"): tl.append(kb)
        if logo: tl.append(f'tl.fromTo("#{cid}-l",{{y:60,scale:0.9,opacity:0}},{{y:0,scale:1,opacity:1,duration:0.6,ease:"back.out(1.5)"}},{a + 0.1:.3f});')
        if from_cover and prev[0] in ("split", "splitb"): tl.append(f'tl.set("#spkw",{{y:0}},{a:.3f});')
        cue("click", a - 0.01, 0.2)
    elif mode == "split":
        els.append(f'<div class="{"clip " if wrap else ""}ev split" id="{cid}" {wrap}>{media(cid, src, a, b, x.get("pos", "50% 50%"))}</div>')
        if from_cover:   # straight cut, no slide (nothing underneath may show)
            tl.append(f'tl.set("#{cid}",{{yPercent:0}},{a:.3f});tl.set("#spkw",{{y:{SPLIT_Y}}},{a:.3f});')
            cue("click", a - 0.01, 0.18)
        else:
            tl.append(f'tl.fromTo("#{cid}",{{yPercent:-100}},{{yPercent:0,duration:0.38,ease:"power3.out"}},{a:.3f});')
            tl.append(f'tl.to("#spkw",{{y:{SPLIT_Y},duration:0.38,ease:"power3.out"}},{a:.3f});'); cue("click", a - 0.01, 0.2)
        if not to_cover:
            tl.append(f'tl.to("#{cid}",{{yPercent:-100,duration:0.3,ease:"power3.in"}},{b - 0.3:.3f});')
            tl.append(f'tl.to("#spkw",{{y:0,duration:0.3,ease:"power3.in"}},{b - 0.3:.3f});')
        tl.append(kb)
    elif mode == "splitb":   # mirror of split: she moves up, picture fills the lower half
        els.append(f'<div class="{"clip " if wrap else ""}ev splitb" id="{cid}" {wrap}>{media(cid, src, a, b, x.get("pos", "50% 50%"))}</div>')
        if from_cover:
            tl.append(f'tl.set("#{cid}",{{yPercent:0}},{a:.3f});tl.set("#spkw",{{y:{-SPLITB_Y}}},{a:.3f});'); cue("click", a - 0.01, 0.18)
        else:
            tl.append(f'tl.fromTo("#{cid}",{{yPercent:100}},{{yPercent:0,duration:0.38,ease:"power3.out"}},{a:.3f});')
            tl.append(f'tl.to("#spkw",{{y:{-SPLITB_Y},duration:0.38,ease:"power3.out"}},{a:.3f});'); cue("click", a - 0.01, 0.2)
        if not to_cover:
            tl.append(f'tl.to("#{cid}",{{yPercent:100,duration:0.3,ease:"power3.in"}},{b - 0.3:.3f});')
            tl.append(f'tl.to("#spkw",{{y:0,duration:0.3,ease:"power3.in"}},{b - 0.3:.3f});')
        tl.append(kb)
    elif mode == "stack":    # cards pile up on the page, one per beat
        parts = []
        for j, (isrc, dl, rot, w, ar, dx, dy, o) in enumerate(x["items"]):
            h = round(w / ar); jid = f"{cid}-s{j}"
            inner = (f'<video id="{jid}-v" class="clip" src="{isrc}" muted playsinline data-start="{a + dl:.3f}" data-duration="{b - a - dl:.3f}" data-track-index="{8 + j}"></video>'
                     if is_vid(isrc) else f'<img id="{jid}-v" src="{isrc}" />')
            parts.append(f'<div class="card scard" id="{jid}" style="left:{(1080 - w) // 2 + dx}px;top:{(1920 - h) // 2 - 120 + dy}px;width:{w}px;height:{h}px;z-index:{j + 1}">{inner}</div>')
            tl.append(f'tl.set("#{jid}",{{opacity:0}},0);')
            tl.append(f'tl.fromTo("#{jid}",{{opacity:1,scale:1.18,rotation:{rot * 2.5},y:40}},{{opacity:1,scale:1,rotation:{rot},y:0,duration:0.42,ease:"power3.out"}},{a + dl:.3f});')
            cue("click", a + dl - 0.01, 0.2)
        els.append(f'<div class="ev boxp" id="{cid}">{"".join(parts)}</div>')   # untimed container: its videos carry the timing
        tl.append(f'tl.set("#{cid}",{{opacity:0}},0);tl.set("#{cid}",{{opacity:1}},{a:.3f});tl.set("#{cid}",{{opacity:0}},{b:.3f});')
        if from_cover and prev[0] in ("split", "splitb"): tl.append(f'tl.set("#spkw",{{y:0}},{a:.3f});')
    elif mode in ("polrow", "polaroid"):
        items = x["items"] if mode == "polrow" else [(src, x["x"], x["y"], x["rot"], 0.0)]
        w = x.get("w", 360); parts = []
        for j, (img, px, py, rot, dl) in enumerate(items):
            parts.append(f'<div class="pol" id="{cid}-p{j}" style="left:{px}px;top:{py}px;width:{w}px"><div class="pol-img" style="background-image:url(\'{img}\')"></div></div>')
            tl.append(f'tl.fromTo("#{cid}-p{j}",{{opacity:0,scale:0.55,rotation:{rot * 3},y:70}},{{opacity:1,scale:1,rotation:{rot},y:0,duration:0.5,ease:"back.out(1.6)"}},{a + dl:.3f});')
            tl.append(f'tl.to("#{cid}-p{j}",{{opacity:0,y:-60,duration:0.24,ease:"power2.in"}},{b - 0.24 - 0.05 * (len(items) - 1 - j):.3f});')
            if not x.get("silent"): cue("shutter", a + dl, 0.3)
        els.append(f'<div class="clip ev" id="{cid}" {wrap}>{"".join(parts)}</div>')
    elif mode == "logo":
        els.append(f'<div class="clip ev" id="{cid}" {wrap}><img class="logo" id="{cid}-l" src="{src}" /></div>')
        tl.append(f'tl.fromTo("#{cid}-l",{{opacity:0,y:-30,scale:0.85}},{{opacity:1,y:0,scale:1,duration:0.55,ease:"back.out(1.6)"}},{a:.3f});')
        tl.append(f'tl.to("#{cid}-l",{{opacity:0,duration:0.25}},{b - 0.25:.3f});')
        cue("tick", a, 0.3)

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
# plum subtitles where they sit on the light box page (below the card); white over footage
DARK = [(a, b) for m, a, b, src, x in EV if m == "stack"] + [(a, b) for m, a, b, src, x in EV if m == "box" and (1920 - round(x["w"] / x["ar"])) // 2 + (70 if x.get("logo") else -40) + round(x["w"] / x["ar"]) < 1560]
for k, c in enumerate(chunks):
    a = c[0]["s"] - 0.05
    b = min(c[-1]["e"] + 0.25, chunks[k + 1][0]["s"] - 0.05) if k + 1 < len(chunks) else SPK_END - 0.1
    hl = next((j for j, w in enumerate(c) if norm(w["w"]) in HL), -1)
    ov = lambda ea, eb: max(0.0, min(b, eb) - max(a, ea))          # how much of this line plays over a layout
    cand = [(ov(ea, eb), m) for m, ea, eb, *_ in EV if m in COVER and ov(ea, eb) > 0.35 * (b - a)]
    lay = max(cand)[1] if cand else None
    dark = any(ov(da, db) > 0.35 * (b - a) for da, db in DARK)
    # reference-style placement: on the B-roll just above the seam in a half frame, under the card on a box page,
    # and a little below centre (clear of Instagram's caption area) on full-frame shots
    top = 700 if lay == "split" else 1040 if lay == "splitb" else 1570 if dark else 1300
    txt = " ".join(f'<span class="{"hl" if j == hl else ""}">{html.escape("I" if w["w"] == "i" else w["w"].rstrip(",."))}</span>' for j, w in enumerate(c))
    els.append(f'<div class="clip subc" data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="6"><div class="sub{" dark" if dark else ""}" id="c{k}" style="top:{top}px">{txt}</div></div>')
    tl.append(f'tl.fromTo("#c{k}",{{opacity:0,y:14}},{{opacity:1,y:0,duration:0.18,ease:"power2.out"}},{a:.3f});')

a = SPK_END - 0.15   # plain white end slide, left blank on purpose (brand content added later)
els.append(f'<div class="clip" id="end" data-start="{a:.3f}" data-duration="{DUR - a:.3f}" data-track-index="7"><div class="end"></div></div>')
tl.append(f'tl.fromTo("#end .end",{{opacity:0}},{{opacity:1,duration:0.35}},{a:.3f});')
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
json.dump(dict(duration=DUR, end_at=SPK_END, music_gain=1.0, cues=sorted(cues, key=lambda c: c[1])), open(os.path.join(PROJECT, "media", "cues.json"), "w"), indent=1)
print("events", len(EV), "subs", len(chunks), "cues", len(cues), "dur", DUR)
