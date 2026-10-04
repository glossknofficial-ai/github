"""Generate index.html (HyperFrames overlay composition) + media/cues.json (SFX cue sheet)."""
import html, json, os, re
from edl import *

W, H = 2160, 3840
END_CARD = 2.2
DUR = round(TOTAL + END_CARD, 3)
PURPLE = "#d7b6e2"
o = lambda src: round(to_out(src), 3)  # source time -> output time

WORDS = words()

# Emphasis: source-time windows whose words switch to the purple italic serif
EMPH = [(0.25, 0.87), (1.55, 2.02), (4.18, 4.76), (13.36, 13.68), (16.73, 17.12), (17.74, 18.17),
        (18.38, 18.89), (20.58, 20.95), (22.46, 23.26), (34.62, 35.56), (36.09, 36.46), (37.47, 37.78),
        (37.92, 38.59), (38.87, 39.25), (42.80, 43.38), (44.84, 45.25), (46.52, 47.05), (47.57, 47.95),
        (50.41, 50.95), (51.48, 51.91)]
STRIKE = [(2.495, 3.24)]  # "makeup remover" gets struck through
# Source windows where designed graphics replace the running captions
NO_CAPS = [(5.60, 9.62), (24.42, 29.30), (30.29, 31.43), (32.66, 34.12), (40.05, 41.98), (48.70, 49.32)]

in_any = lambda t, rngs: any(a <= t < b - 0.005 for a, b in rngs)
cues = []  # (sfx, out_time, gain)
cue = lambda n, t, g=1.0: cues.append((n, round(max(0.0, t), 3), g))

# ------------------------------------------------------------------ caption phrases
# Hand-set phrase breaks (source start of each phrase) on natural speech beats
PHRASE_STARTS = [0.07, 1.46, 2.32, 3.25, 4.08, 11.03, 12.59, 13.93, 14.98, 16.19, 17.12, 18.17, 19.72, 20.95,
                 21.59, 22.47, 23.51, 29.96, 31.64, 34.29, 35.56, 36.91, 37.78, 38.59, 39.25, 42.28, 43.38, 44.85,
                 45.25, 47.05, 48.16, 49.33, 50.42, 51.49]
is_start = lambda t: any(abs(t - x) < 0.006 for x in PHRASE_STARTS)
phrases, cur = [], []
for i, w in enumerate(WORDS):
    if in_any(w["src"], NO_CAPS):
        if cur: phrases.append(cur); cur = []
        continue
    if cur and is_start(w["src"]):
        phrases.append(cur); cur = []
    cur.append(w)
if cur: phrases.append(cur)

els, tl = [], []
for pi, ph in enumerate(phrases):
    start = max(0.0, ph[0]["start"] - 0.04)
    nxt_start = phrases[pi + 1][0]["start"] - 0.04 if pi + 1 < len(phrases) else DUR
    end = min(ph[-1]["end"] + 0.35, nxt_start)
    spans = []
    for wi, w in enumerate(ph):
        txt = html.escape("I" if w["text"].rstrip(",.:") == "i" else w["text"].rstrip(",.:"))
        cls = "w em" if in_any(w["src"], EMPH) else "w"
        if in_any(w["src"], STRIKE): cls += " strike"
        spans.append(f'<span class="{cls}" id="p{pi}w{wi}">{txt}</span>')
        sel = f"#p{pi}w{wi}"
        if "em" in cls:
            tl.append(f'tl.fromTo("{sel}",{{opacity:0,scale:0.6,rotation:-4,y:30}},{{opacity:1,scale:1,rotation:0,y:0,duration:0.22,ease:"back.out(2.4)"}},{w["start"]:.3f});')
        else:
            tl.append(f'tl.fromTo("{sel}",{{opacity:0,y:36}},{{opacity:1,y:0,duration:0.14,ease:"power2.out"}},{w["start"]:.3f});')
        if "strike" in cls:
            tl.append(f'tl.fromTo("{sel}",{{"--s":0}},{{"--s":1,duration:0.25,ease:"power2.inOut",immediateRender:false}},{w["end"]:.3f});')
    els.append(f'<div class="clip cap" data-start="{start:.3f}" data-duration="{end - start:.3f}" data-track-index="5">'
               f'<div class="capin">{" ".join(spans)}</div></div>')

# ------------------------------------------------------------------ designed graphics
def clip(cid, a, b, inner, cls="", track=6):
    els.append(f'<div id="{cid}" class="clip {cls}" data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="{track}">{inner}</div>')


# Hook impact on "12 years", strike-through tick, sparkle on "create it"
cue("impact", o(0.26) - 0.02, 0.55); cue("swish", o(2.83), 0.35); cue("sparkle", o(4.19), 0.5)

# Shot changes: soft white flash + whoosh; B-roll entries: swish
for si in range(1, len(SHOTS)):
    t = SHOT_STARTS[si]
    clip(f"flash{si}", t - 0.02, t + 0.22, '<div class="flash"></div>', track=9)
    tl.append(f'tl.fromTo("#flash{si} .flash",{{opacity:0.0}},{{opacity:0.38,duration:0.05,ease:"none"}},{t - 0.02:.3f}).to("#flash{si} .flash",{{opacity:0,duration:0.17,ease:"power2.out"}},{t + 0.03:.3f});')
    cue("whoosh", t - 0.3, 0.45)
for ba, bb, n, off in BROLL:
    cue("swish" if ba not in (34.29,) else "whoosh_fast", o(ba) - 0.12, 0.4)  # filtered below

# Name card: turnaround -> "Hi, I am Jaspreet" + role chips popping as she says them
a, b = o(5.66), o(9.62)
roles = [("Makeup Artist", 7.09), ("Educator", 7.78), ("Founder, GLOSSKN", 8.54)]
chips = "".join(f'<div class="chip" id="role{i}"><span class="dot"></span>{html.escape(r)}</div>' for i, (r, _) in enumerate(roles))
clip("namecard", a, b, f'<div class="nc"><div class="hi" id="nc-hi">Hi, I&#8217;m</div><div class="name" id="nc-name">Jaspreet</div><div class="chips">{chips}</div></div>')
tl.append(f'tl.fromTo("#nc-hi",{{opacity:0,x:-60}},{{opacity:1,x:0,duration:0.25,ease:"power3.out"}},{o(5.68):.3f});')
tl.append(f'tl.fromTo("#nc-name",{{opacity:0,y:60,scale:0.9}},{{opacity:1,y:0,scale:1,duration:0.35,ease:"back.out(1.8)"}},{o(6.31):.3f});')
cue("shutter", o(5.68), 0.5); cue("whoosh_fast", o(6.25), 0.35)
for i, (r, t) in enumerate(roles):
    tl.append(f'tl.fromTo("#role{i}",{{opacity:0,scale:0.5,y:20}},{{opacity:1,scale:1,y:0,duration:0.24,ease:"back.out(2.6)"}},{o(t):.3f});')
    cue("pop", o(t), 0.55)
tl.append(f'tl.to("#namecard .nc",{{opacity:0,x:-80,duration:0.2,ease:"power2.in"}},{b - 0.2:.3f});')

# Eye line-icon next to "eyes"
eye_svg = ('<svg viewBox="0 0 120 70" class="eye"><path d="M5 35 Q60 -12 115 35 Q60 82 5 35 Z" fill="none" stroke="#fff" stroke-width="6" stroke-linejoin="round"/>'
           f'<circle cx="60" cy="35" r="15" fill="{PURPLE}"/><circle cx="60" cy="35" r="6" fill="#fff"/></svg>')
clip("eyeicon", o(13.37), o(13.37) + 1.6, eye_svg)
tl.append(f'tl.fromTo("#eyeicon .eye",{{opacity:0,scale:0.3,rotation:-20}},{{opacity:1,scale:1,rotation:0,duration:0.3,ease:"back.out(2.2)"}},{o(13.37):.3f}).to("#eyeicon .eye",{{opacity:0,scale:0.8,duration:0.2}},{o(13.37) + 1.35:.3f});')
cue("pop", o(13.37), 0.45)
cue("click", o(16.74), 0.4); cue("click", o(17.75), 0.4)

# Mission: riser into it, shimmer on "one of a kind"
cue("riser", o(20.59) - 1.3, 0.35); cue("shimmer", o(22.47), 0.5)

# Checklist: removes makeup / sting free / tear free / comfortable on the eyes
items = [("Removes makeup", 24.67), ("Sting free", 26.21), ("Tear free", 26.95), ("Comfortable on the eyes", 28.21)]
a, b = o(24.42), o(29.30)
rows = "".join(f'<div class="ck" id="ck{i}"><span class="tick"><svg viewBox="0 0 40 40"><path d="M10 21 L17 28 L30 13" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg></span>{html.escape(t)}</div>' for i, (t, _) in enumerate(items))
clip("checklist", a, b, f'<div class="cl"><div class="cltitle" id="cl-title">a face wash that could&#8230;</div>{rows}</div>')
tl.append(f'tl.fromTo("#cl-title",{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.2}},{a:.3f});')
for i, (t, s) in enumerate(items):
    tl.append(f'tl.fromTo("#ck{i}",{{opacity:0,x:-120}},{{opacity:1,x:0,duration:0.26,ease:"back.out(1.7)"}},{o(s):.3f});')
    tl.append(f'tl.fromTo("#ck{i} .tick",{{scale:0}},{{scale:1,duration:0.2,ease:"back.out(3)"}},{o(s) + 0.12:.3f});')
    cue("click", o(s) + 0.12, 0.6); cue("swish", o(s) - 0.05, 0.22)
tl.append(f'tl.to("#checklist .cl",{{opacity:0,y:-40,duration:0.2}},{b - 0.2:.3f});')


def card(cid, a, b, inner, sfx_in="whoosh"):
    clip(cid, a, b, f'<div class="card"><div class="grain"></div><div class="cardin">{inner}</div></div>', track=8)
    tl.append(f'tl.fromTo("#{cid} .card",{{clipPath:"inset(100% 0 0 0)"}},{{clipPath:"inset(0% 0 0 0)",duration:0.22,ease:"power3.out"}},{a:.3f});')
    tl.append(f'tl.to("#{cid} .card",{{clipPath:"inset(0 0 100% 0)",duration:0.18,ease:"power3.in"}},{b - 0.18:.3f});')
    cue(sfx_in, a - 0.2, 0.45)


# Lab card 1: "with multiple labs"
a, b = o(30.29), o(31.43)
card("labs", a, b, '<div class="kick" id="labs-k">we worked with</div><div class="big" id="labs-b">multiple labs.</div>')
tl.append(f'tl.fromTo("#labs-k",{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.2}},{a + 0.08:.3f});')
tl.append(f'tl.fromTo("#labs-b",{{opacity:0,scale:0.8}},{{opacity:1,scale:1,duration:0.3,ease:"back.out(2)"}},{o(30.55):.3f});')
cue("impact", o(30.55), 0.3)

# Lab card 2: "reworking the formula" with a version counter
a, b = o(32.66), o(34.12)
vers = "".join(f'<span class="v" id="v{i}">V{i + 1}</span>' for i in range(5))
card("formula", a, b, f'<div class="kick" id="fm-k">reworking the</div><div class="big" id="fm-b">formula.</div><div class="vers">{vers}<span class="v dots" id="v5">&#8230;</span></div>', "swish")
tl.append(f'tl.fromTo("#fm-k",{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.2}},{a + 0.05:.3f});')
tl.append(f'tl.fromTo("#fm-b",{{opacity:0,scale:0.8}},{{opacity:1,scale:1,duration:0.3,ease:"back.out(2)"}},{o(33.52):.3f});')
for i in range(6):
    tl.append(f'tl.fromTo("#v{i}",{{opacity:0,y:20}},{{opacity:1,y:0,duration:0.08}},{a + 0.15 + i * 0.17:.3f});')
cue("typing", a + 0.12, 0.5)

# Back to the lab: rewind
a, b = o(40.06), o(41.98)
card("backlab", a, b, f'<div class="rew" id="rew"><svg viewBox="0 0 100 100"><path d="M78 50 A28 28 0 1 1 64 25.8" fill="none" stroke="#fff" stroke-width="8" stroke-linecap="round"/><path d="M58 12 L68 27 L51 31" fill="none" stroke="#fff" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/></svg></div><div class="kick" id="bl-k">so we went</div><div class="big" id="bl-b">back to the lab.</div>', "rewind")
tl.append(f'tl.fromTo("#rew",{{rotation:0}},{{rotation:-360,duration:1.1,ease:"power2.inOut"}},{a + 0.05:.3f});')
tl.append(f'tl.fromTo("#bl-k",{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.2}},{a + 0.1:.3f});')
tl.append(f'tl.fromTo("#bl-b",{{opacity:0,scale:0.8}},{{opacity:1,scale:1,duration:0.3,ease:"back.out(2)"}},{o(40.95):.3f});')

# Stung / gentle / done accents
cue("click", o(38.88), 0.45); cue("sparkle", o(44.85), 0.45); cue("impact", o(47.58), 0.45)

# Product title: Power Cleanse by GLOSSKN
a, b = o(48.70), TOTAL
clip("title", a, b, '<div class="pt"><div class="ptk" id="pt-k">GLOSSKN</div><div class="ptb" id="pt-b">Power Cleanse</div><div class="ptl" id="pt-l"></div></div>')
tl.append(f'tl.fromTo("#pt-k",{{opacity:0,scale:1.25}},{{opacity:1,scale:1,duration:0.5,ease:"power2.out"}},{a:.3f});')
tl.append(f'tl.fromTo("#pt-b",{{opacity:0,y:50,scale:0.9}},{{opacity:1,y:0,scale:1,duration:0.4,ease:"back.out(1.8)"}},{o(48.74):.3f});')
tl.append(f'tl.fromTo("#pt-l",{{scaleX:0}},{{scaleX:1,duration:0.4,ease:"power2.out"}},{o(49.0):.3f});')
cue("ding", o(48.74), 0.5); cue("shimmer", o(50.42), 0.35)

# End card
a, b = TOTAL, DUR
clip("endcard", a, b, '<div class="card end"><div class="grain"></div><div class="cardin"><div class="ek" id="ec-k">GLOSSKN</div><div class="eb" id="ec-b">Power Cleanse</div><div class="es" id="ec-s">Gentle yet effective cleansing.</div></div></div>', track=8)
tl.append(f'tl.fromTo("#endcard .card",{{clipPath:"circle(0% at 50% 55%)"}},{{clipPath:"circle(150% at 50% 55%)",duration:0.45,ease:"power3.inOut"}},{a:.3f});')
tl.append(f'tl.fromTo("#ec-k",{{opacity:0,y:-30}},{{opacity:1,y:0,duration:0.35}},{a + 0.3:.3f});')
tl.append(f'tl.fromTo("#ec-b",{{opacity:0,scale:0.85}},{{opacity:1,scale:1,duration:0.45,ease:"back.out(1.6)"}},{a + 0.45:.3f});')
tl.append(f'tl.fromTo("#ec-s",{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.35}},{a + 0.8:.3f});')
cue("whoosh", a - 0.25, 0.5); cue("impact", a + 0.4, 0.4); cue("sparkle", a + 0.8, 0.4)

# ------------------------------------------------------------------ assemble
CSS = open(os.path.join(HERE, "style.css")).read()
page = f"""<!doctype html>
<html lang="en" data-resolution="portrait-4k">
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
      <video id="base" class="clip" src="media/base.mp4" muted playsinline data-start="0" data-duration="{TOTAL}" data-track-index="0"></video>
      <audio id="mix" src="media/mix.wav" data-start="0" data-duration="{DUR}" data-track-index="1"></audio>
      {chr(10).join('      ' + e for e in els).strip()}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      {chr(10).join('      ' + t for t in tl).strip()}
      tl.set({{}}, {{}}, {DUR});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
open(os.path.join(PROJECT, "index.html"), "w").write(page)
# Keep the sound design sparse, like the references: transition whooshes, one pop for the name, one ding for
# the product title. Everything else stays visual only.
TRANSITIONS = set([round(SHOT_STARTS[i] - 0.3, 3) for i in range(1, len(SHOTS))] + [round(TOTAL - 0.25, 3)])
kept, pop_used = [], False
for n, t, g in cues:
    if n == "whoosh" and (t in TRANSITIONS or g == 0.45):
        kept.append(("whoosh", t, 0.32))
    elif n in ("swish", "rewind") and g == 0.45:          # card wipes
        kept.append(("whoosh", t, 0.28))
    elif n == "whoosh_fast" and abs(t - (o(34.29) - 0.12)) < 0.01:  # into the friends & family B-roll
        kept.append(("whoosh_fast", t, 0.3))
    elif n == "pop" and not pop_used:
        kept.append(("pop", t, 0.35)); pop_used = True
    elif n == "ding":
        kept.append(("ding", t, 0.3))
kept.sort(key=lambda c: c[1])
cues = [c for i, c in enumerate(kept) if i == 0 or c[1] - kept[i - 1][1] > 0.8]
json.dump(dict(duration=DUR, cues=cues), open(os.path.join(PROJECT, "media", "cues.json"), "w"), indent=1)
print("phrases", len(phrases), "elements", len(els), "tweens", len(tl), "cues", len(cues), "duration", DUR)
