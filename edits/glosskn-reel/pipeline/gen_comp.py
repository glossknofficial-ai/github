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
# Purple is reserved for the highlight words; other big serif words stay white
HILITE = [(0.25, 0.87), (4.18, 4.76), (16.73, 17.12), (22.46, 23.26), (37.47, 37.78), (37.92, 38.59),
          (44.84, 45.25), (50.41, 50.95), (51.48, 51.91)]
STRIKE = [(2.495, 3.24)]  # "makeup remover" gets struck through
# Source windows where designed graphics replace the running captions
NO_CAPS = [(20.58, 20.95), (47.57, 47.95), (5.60, 9.62), (24.42, 29.30), (30.29, 34.12), (38.59, 40.05), (40.05, 41.98), (48.70, 49.32)]

in_any = lambda t, rngs: any(a <= t < b - 0.005 for a, b in rngs)
cues = []  # (sfx, out_time, gain)
extra_cues = []  # added after the sparse filter
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

# Reference-style text: small white words placed around her + one big purple serif word per beat.
# layout: "lock" = small / BIG / small lines, "stack" = one word per line (small caps) building down,
# "line" = a short small line. align: L / C / R (all in the chest band, clear of her face).
LAYOUT = {0.07: ("lock", "C"), 1.46: ("stack", "L"), 2.32: ("line", "C"), 3.25: ("line", "R"), 4.08: ("lock", "C"),
          11.03: ("line", "C"), 12.59: ("lock", "R"), 13.93: ("line", "L"), 14.98: ("line", "C"), 16.19: ("lock", "L"),
          17.12: ("lock", "R"), 18.17: ("lock", "C"), 19.72: ("line", "L"), 20.95: ("line", "C"), 21.59: ("line", "R"),
          22.47: ("lock", "C"), 23.51: ("line", "L"), 29.96: ("line", "C"), 34.29: ("lock", "L"), 35.56: ("lock", "R"),
          36.91: ("lock", "L"), 37.78: ("lock", "R"), 42.28: ("stack", "L"), 43.38: ("line", "C"), 44.85: ("lock", "C"),
          45.25: ("lock", "L"), 47.05: ("line", "C"), 48.16: ("line", "C"), 49.33: ("line", "C"), 50.42: ("lock", "C"),
          51.49: ("lock", "C")}

els, tl = [], []
for pi, ph in enumerate(phrases):
    start = max(0.0, ph[0]["start"] - 0.04)
    nxt_start = phrases[pi + 1][0]["start"] - 0.04 if pi + 1 < len(phrases) else DUR
    end = min(ph[-1]["end"] + 0.35, nxt_start)
    kind, align = next((v for k, v in LAYOUT.items() if abs(k - ph[0]["src"]) < 0.02), ("line", "C"))
    words_html = []
    for wi, w in enumerate(ph):
        txt = html.escape("I" if w["text"].rstrip(",.:") == "i" else w["text"].rstrip(",.:"))
        em = in_any(w["src"], EMPH)
        cls = ("w em hl" if in_any(w["src"], HILITE) else "w em") if em else ("w stk" if kind == "stack" else "w")
        if in_any(w["src"], STRIKE): cls += " strike"
        words_html.append((em, f'<span class="{cls}" id="p{pi}w{wi}">{txt}</span>'))
        sel = f"#p{pi}w{wi}"
        if em:
            tl.append(f'tl.fromTo("{sel}",{{opacity:0,scale:0.5,rotation:-7,y:40}},{{opacity:1,scale:1,rotation:0,y:0,duration:0.26,ease:"back.out(2.2)"}},{w["start"]:.3f});')
        else:
            tl.append(f'tl.fromTo("{sel}",{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.14,ease:"power2.out"}},{w["start"]:.3f});')
        if "strike" in cls:
            tl.append(f'tl.fromTo("{sel}",{{"--s":0}},{{"--s":1,duration:0.25,ease:"power2.inOut",immediateRender:false}},{w["end"]:.3f});')
    lines = []
    if kind == "stack":
        lines = [([h], em) for em, h in words_html]
    elif kind == "lock":
        for em, h in words_html:
            if lines and lines[-1][1] == em:
                lines[-1][0].append(h)
            else:
                lines.append(([h], em))
    else:
        lines = [([h for _, h in words_html], False)]
    body = "".join(f'<div class="ln{" big" if big else ""}">{" ".join(hs)}</div>' for hs, big in lines)
    els.append(f'<div class="clip cap" data-start="{start:.3f}" data-duration="{end - start:.3f}" data-track-index="5">'
               f'<div class="lay {align}">{body}</div></div>')

# ------------------------------------------------------------------ designed graphics
def clip(cid, a, b, inner, cls="", track=6):
    els.append(f'<div id="{cid}" class="clip {cls}" data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="{track}">{inner}</div>')


# Whip-blur transitions on scene changes; a soft punch on B-roll entries
for si in range(1, len(SHOTS)):
    t = SHOT_STARTS[si]; dx = 160 if si % 2 else -160
    tl.append(f'tl.fromTo("#vwrap",{{x:{dx},scale:1.18,filter:"blur(26px)"}},{{x:0,scale:1,filter:"blur(0px)",duration:0.32,ease:"power3.out",immediateRender:false}},{t:.3f});')
for t in [o(34.29), o(42.26)]:
    tl.append(f'tl.fromTo("#vwrap",{{scale:1.09}},{{scale:1,duration:0.42,ease:"power3.out",immediateRender:false}},{t:.3f});')

# Stickers (drawn here, no stock art): hearts for friends & family, sparkles for the gentle moments
HEART = ('<svg viewBox="0 0 100 92"><path d="M50 88 C20 66 4 50 4 28 C4 13 16 3 30 3 C40 3 46 9 50 16 C54 9 60 3 70 3 '
         'C84 3 96 13 96 28 C96 50 80 66 50 88 Z" fill="#d7b6e2" stroke="#fff" stroke-width="6"/></svg>')
SPARK = '<svg viewBox="0 0 100 100"><path d="M50 0 C54 34 66 46 100 50 C66 54 54 66 50 100 C46 66 34 54 0 50 C34 46 46 34 50 0 Z" fill="#fff"/></svg>'
sticker_cues = []
def stickers(sid, t0, t1, items, svg, sfx):
    inner = "".join(f'<div class="stk-i" id="{sid}{k}" style="left:{x}px;top:{y}px;width:{w}px;height:{w}px">{svg}</div>' for k, (x, y, w) in enumerate(items))
    clip(sid, t0, t1, inner, "stickers", track=8)
    for k, (x, y, w) in enumerate(items):
        tk = t0 + 0.09 * k
        tl.append(f'tl.fromTo("#{sid}{k}",{{opacity:0,scale:0.2,rotation:-25}},{{opacity:1,scale:1,rotation:{(-1) ** k * 10},duration:0.3,ease:"back.out(2.6)"}},{tk:.3f});')
        tl.append(f'tl.to("#{sid}{k}",{{y:-90,rotation:{(-1) ** k * -6},duration:{max(0.3, t1 - tk - 0.5):.3f},ease:"sine.inOut"}},{tk + 0.3:.3f});')
    sticker_cues.append((sfx, round(t0, 3)))

stickers("hearts1", o(37.48), o(37.78), [(1480, 1880, 230), (1760, 2080, 170), (1560, 2300, 130)], HEART, "heartpop")
stickers("hearts2", o(37.93), o(38.59), [(260, 1860, 230), (520, 2120, 170), (300, 2330, 130)], HEART, "heartpop")
stickers("spark1", o(16.74), o(17.12), [(1260, 2160, 150), (1450, 2380, 90)], SPARK, "sparkle")
stickers("spark2", o(22.47), o(23.30), [(300, 1980, 170), (1690, 2120, 130), (1820, 2420, 90)], SPARK, "sparkle")
stickers("spark3", o(44.85), o(45.25), [(560, 2000, 150), (1480, 2260, 110)], SPARK, "sparkle")

# Freeze-frame sticker: the picture pauses on "I'm Jaspreet", she pops out as a white-outlined sticker,
# her name sits big behind her and the roles pop in as she says them (voice keeps running)
fa, fb = o(6.25), o(9.62)
roles = [("Makeup Artist", 7.09), ("Educator", 7.78), ("Founder, GLOSSKN", 8.54)]
chips = "".join(f'<div class="chip" id="role{i}"><span class="dot"></span>{html.escape(r)}</div>' for i, (r, _) in enumerate(roles))
clip("freeze", fa, fb, '<div class="fz-bg" id="fz-bg"></div><div class="fz-tint" id="fz-tint"></div>'
     '<div class="fz-hi" id="fz-hi">Hi, I&#8217;m</div><div class="fz-name" id="fz-name">Jaspreet</div>'
     '<img class="fz-st" id="fz-st" src="media/freeze/sticker4k.png" />'
     f'<div class="fz-chips">{chips}</div>', track=7)
tl.append(f'tl.fromTo("#fz-bg",{{scale:1,filter:"blur(0px)"}},{{scale:1.08,filter:"blur(26px)",duration:0.45,ease:"power2.out"}},{fa:.3f});')
tl.append(f'tl.fromTo("#fz-tint",{{opacity:0}},{{opacity:1,duration:0.4}},{fa:.3f});')
tl.append(f'tl.fromTo("#fz-st",{{opacity:0,scale:0.86,rotation:4,y:120}},{{opacity:1,scale:1,rotation:-2,y:0,duration:0.5,ease:"back.out(1.7)"}},{fa + 0.05:.3f});')
tl.append(f'tl.fromTo("#fz-st",{{scale:1}},{{scale:1.035,duration:{fb - fa - 0.8:.3f},ease:"sine.inOut",immediateRender:false}},{fa + 0.55:.3f});')
tl.append(f'tl.fromTo("#fz-hi",{{opacity:0,x:-80}},{{opacity:1,x:0,duration:0.3,ease:"power3.out"}},{fa + 0.1:.3f});')
tl.append(f'tl.fromTo("#fz-name",{{opacity:0,scale:0.7,y:80}},{{opacity:1,scale:1,y:0,duration:0.45,ease:"back.out(1.8)"}},{o(6.31):.3f});')
for i, (r, t) in enumerate(roles):
    tl.append(f'tl.fromTo("#role{i}",{{opacity:0,scale:0.4,y:30,rotation:-6}},{{opacity:1,scale:1,y:0,rotation:0,duration:0.28,ease:"back.out(2.6)"}},{o(t):.3f});')
tl.append(f'tl.to("#freeze .fz-hi, #freeze .fz-name, #freeze .fz-chips",{{opacity:0,y:-60,duration:0.2,ease:"power2.in"}},{fb - 0.22:.3f});')
tl.append(f'tl.to("#fz-st",{{opacity:0,scale:1.12,duration:0.22,ease:"power2.in"}},{fb - 0.22:.3f});')

# Small zoom accents on key beats (feels "cut to the beat")
for t in [o(1.56), o(4.19), o(38.88), o(47.58)]:
    tl.append(f'tl.fromTo("#vwrap",{{scale:1.05}},{{scale:1,duration:0.35,ease:"power2.out",immediateRender:false}},{t:.3f});')

# Portrait photo frames (reference style): real footage pops in over her, tilted, then flies out
PHOTOS = [("pf1", "media/pf_artist.mp4", 0.20, o(2.32), "left: 60px; top: 820px; --w: 600px; --h: 730px;", -5),
          ("pf2", "media/pf_eyes.mp4", o(11.75), o(13.95), "left: 90px; top: 560px;", 5)]
for pid, src, a0, b0, pos, rot in PHOTOS:
    els.append(f'<div class="pf" id="{pid}" style="{pos}"><video id="{pid}-v" class="clip pfv" src="{src}" muted playsinline '
               f'data-start="{a0:.3f}" data-duration="{b0 - a0:.3f}" data-track-index="7"></video></div>')
    tl.append(f'tl.fromTo("#{pid}",{{opacity:0,scale:0.6,rotation:{rot * 3},y:120}},{{opacity:1,scale:1,rotation:{rot},y:0,duration:0.4,ease:"back.out(1.6)"}},{a0:.3f});')
    tl.append(f'tl.to("#{pid}",{{opacity:0,scale:0.85,y:-80,duration:0.22,ease:"power2.in"}},{b0 - 0.22:.3f});')
    extra_cues.append(("shutter", round(a0, 3), 0.22))

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
    parts = "".join(f'<span class="pt-dot" id="{cid}-p{k}" style="left:{(k * 397) % 1960 + 60}px;top:{2400 + (k * 613) % 1300}px;'
                    f'width:{18 + (k * 7) % 26}px;height:{18 + (k * 7) % 26}px"></span>' for k in range(12))
    clip(cid, a, b, f'<div class="card"><div class="blob b1" id="{cid}-b1"></div><div class="blob b2" id="{cid}-b2"></div>{parts}'
                    f'<div class="grain"></div><div class="cardin" id="{cid}-in">{inner}</div></div>', track=8)
    tl.append(f'tl.fromTo("#{cid}-b1",{{x:-200,y:-100,scale:1}},{{x:260,y:180,scale:1.25,duration:{b - a:.3f},ease:"sine.inOut"}},{a:.3f});')
    tl.append(f'tl.fromTo("#{cid}-b2",{{x:200,y:150,scale:1.2}},{{x:-220,y:-160,scale:0.95,duration:{b - a:.3f},ease:"sine.inOut"}},{a:.3f});')
    tl.append(f'tl.fromTo("#{cid}-in",{{scale:0.96}},{{scale:1.03,duration:{b - a:.3f},ease:"none"}},{a:.3f});')
    for k in range(12):
        tl.append(f'tl.fromTo("#{cid}-p{k}",{{y:0,opacity:0}},{{y:-{900 + (k * 131) % 700},opacity:0.7,duration:{b - a:.3f},ease:"none"}},{a:.3f});')
    tl.append(f'tl.fromTo("#{cid} .card",{{clipPath:"inset(100% 0 0 0)"}},{{clipPath:"inset(0% 0 0 0)",duration:0.22,ease:"power3.out"}},{a:.3f});')
    tl.append(f'tl.to("#{cid} .card",{{clipPath:"inset(0 0 100% 0)",duration:0.18,ease:"power3.in"}},{b - 0.18:.3f});')
    if sfx_in:
        cue(sfx_in, a - 0.2, 0.45)


# Lab card 1: "with multiple labs"
a, b = o(30.29), o(31.43)
card("labs", a, b, '<div class="kick" id="labs-k">we worked with</div><div class="big" id="labs-b">multiple labs.</div>')
tl.append(f'tl.fromTo("#labs-k",{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.2}},{a + 0.08:.3f});')
tl.append(f'tl.fromTo("#labs-b",{{opacity:0,scale:0.8}},{{opacity:1,scale:1,duration:0.3,ease:"back.out(2)"}},{o(30.55):.3f});')
cue("impact", o(30.55), 0.3)

# Animated lab scene (made in code, no stock footage): "and kept testing"
a, b = o(31.43), o(32.66)
levels = [0.55, 0.78, 0.4, 0.66, 0.85]
tubes = "".join(f'<div class="tube"><div class="liq" id="lq{i}"></div>' + "".join(f'<span class="bub" id="bb{i}{k}" style="left:{40 + 45 * k}px"></span>' for k in range(3)) + '</div>' for i in range(5))
dropper = ('<svg class="dropper" viewBox="0 0 120 300"><rect x="35" y="0" width="50" height="90" rx="22" fill="#fff"/>'
           '<path d="M45 90 L75 90 L68 250 Q60 270 52 250 Z" fill="#fff" opacity=".85"/></svg><span class="drop" id="drop"></span>')
card("labscene", a, b, f'<div class="kick" id="ls-k">and kept</div><div class="big" id="ls-b">testing.</div><div class="rack">{dropper}{tubes}</div>', "whoosh")
tl.append(f'tl.fromTo("#ls-k",{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.2}},{a + 0.05:.3f});')
tl.append(f'tl.fromTo("#ls-b",{{opacity:0,scale:0.8}},{{opacity:1,scale:1,duration:0.3,ease:"back.out(2)"}},{o(32.2):.3f});')
for i, lv in enumerate(levels):
    tl.append(f'tl.fromTo("#lq{i}",{{scaleY:0}},{{scaleY:{lv},duration:0.7,ease:"power2.out"}},{a + 0.1 + i * 0.08:.3f});')
    for k in range(3):
        tl.append(f'tl.fromTo("#bb{i}{k}",{{y:0,opacity:0}},{{y:-{int(380 * lv)},opacity:0.9,duration:0.5,ease:"power1.out",repeat:1}},{a + 0.35 + i * 0.07 + k * 0.13:.3f});')
tl.append(f'tl.fromTo("#drop",{{y:0,opacity:1}},{{y:330,opacity:0,duration:0.42,ease:"power2.in",repeat:1}},{a + 0.2:.3f});')

# Lab card 2: "reworking the formula" with a version counter
a, b = o(32.66), o(34.12)
vers = "".join(f'<span class="v" id="v{i}">V{i + 1}</span>' for i in range(5))
card("formula", a, b, f'<div class="kick" id="fm-k">reworking the</div><div class="big" id="fm-b">formula.</div><div class="vers">{vers}<span class="v dots" id="v5">&#8230;</span></div>', None)
tl.append(f'tl.fromTo("#fm-k",{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.2}},{a + 0.05:.3f});')
tl.append(f'tl.fromTo("#fm-b",{{opacity:0,scale:0.8}},{{opacity:1,scale:1,duration:0.3,ease:"back.out(2)"}},{o(33.52):.3f});')
for i in range(6):
    tl.append(f'tl.fromTo("#v{i}",{{opacity:0,y:20}},{{opacity:1,y:0,duration:0.08}},{a + 0.15 + i * 0.17:.3f});')
cue("typing", a + 0.12, 0.5)

# Sting meter (made in code): "If it stung even a little,"
a, b = o(38.59), o(40.05)
gauge = ('<svg class="gauge" viewBox="0 0 1400 780"><path d="M120 700 A580 580 0 0 1 1280 700" fill="none" stroke="rgba(255,255,255,.35)" stroke-width="70" stroke-linecap="round"/>'
         '<path d="M120 700 A580 580 0 0 1 700 120" fill="none" stroke="#fff" stroke-width="70" stroke-linecap="round"/>'
         '<path d="M1080 262 A580 580 0 0 1 1280 700" fill="none" stroke="#5a2f6e" stroke-width="70" stroke-linecap="round"/>'
         '<g id="needle"><rect x="690" y="200" width="20" height="500" rx="10" fill="#fff"/></g><circle cx="700" cy="700" r="56" fill="#fff"/></svg>'
         '<div class="glab gl">gentle</div><div class="glab gr">stings</div><div class="xstamp" id="xst">&#10007;</div>')
card("meter", a, b, f'<div class="kick" id="mt-k">if it stung</div><div class="big" id="mt-b">even a little,</div><div class="gwrap">{gauge}</div>', "whoosh")
tl.append(f'tl.fromTo("#mt-k",{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.2}},{a + 0.05:.3f});')
tl.append(f'tl.fromTo("#mt-b",{{opacity:0,scale:0.8}},{{opacity:1,scale:1,duration:0.3,ease:"back.out(2)"}},{o(39.25):.3f});')
tl.append(f'tl.fromTo("#needle",{{rotation:-80,svgOrigin:"700 700"}},{{rotation:62,svgOrigin:"700 700",duration:0.75,ease:"elastic.out(1,0.45)"}},{a + 0.15:.3f});')
tl.append(f'tl.fromTo("#xst",{{opacity:0,scale:2.4,rotation:-20}},{{opacity:1,scale:1,rotation:-8,duration:0.25,ease:"back.out(2)"}},{a + 0.9:.3f});')

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
clip("title", a, b, '<div class="pt"><div class="ptk" id="pt-k">GLOSSKN</div><div class="ptl" id="pt-l"></div></div>')
tl.append(f'tl.fromTo("#pt-k",{{opacity:0,scale:1.25}},{{opacity:1,scale:1,duration:0.5,ease:"power2.out"}},{a:.3f});')
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
      <div id="vwrap"><video id="base" class="clip" src="media/base.mp4" muted playsinline data-start="0" data-duration="{TOTAL}" data-track-index="0"></video></div>
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
# Sound design: varied, soft, each tied to something on screen (no whoosh spam)
C = [("snap", SHOT_STARTS[i] - 0.02, 0.45) for i in range(1, len(SHOTS))]
C += [(n, t, g) for n, t, g in extra_cues]                                   # photo-frame shutters
C += [("scribble", o(2.82), 0.45), ("shutter", fa, 0.45)]                     # strike-through, freeze
C += [("pop", o(t), 0.35) for t in (7.09, 7.78, 8.54)]                        # name chips
C += [("tick", o(t) + 0.12, 0.45) for t in (24.67, 26.21, 26.95, 28.21)]      # checklist
C += [("swipe", o(30.29) - 0.1, 0.4), ("bubbles", o(31.43) + 0.2, 0.4), ("typing", o(32.66) + 0.12, 0.35),
      ("swipe", o(38.59) - 0.1, 0.4), ("blip", o(38.59) + 0.9, 0.45), ("rewind", o(40.06) - 0.1, 0.4)]
C += [(n, t, 0.45 if n == "heartpop" else 0.4) for n, t in sticker_cues]
C += [("ding", o(48.74), 0.45), ("swipe", TOTAL - 0.15, 0.4), ("sparkle", TOTAL + 0.8, 0.35)]
cues = sorted((n, round(max(0.0, t), 3), g) for n, t, g in C)
json.dump(dict(duration=DUR, cues=cues), open(os.path.join(PROJECT, "media", "cues.json"), "w"), indent=1)
print("phrases", len(phrases), "elements", len(els), "tweens", len(tl), "cues", len(cues), "duration", DUR)
