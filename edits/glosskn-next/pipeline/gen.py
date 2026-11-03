"""GLOSSKN Power Reset explainer: founder talking (untouched), reference-style subtitles (white serif, one lilac word),
and B-roll from earlier GLOSSKN content only where it helps: both products, the face wash, the balm, the power bands."""
import html, json, os, re
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1080, 1920
WORDS = json.load(open(os.path.join(P, "data", "words.json"))); DUR = json.load(open(os.path.join(P, "data", "edit.json")))["duration"]
norm = lambda s: re.sub(r"[^a-z0-9']", "", s.lower()); TOK = [norm(w["w"]) for w in WORDS]
def at(phrase, end=False):
    p = [norm(x) for x in phrase.split()]
    for i in range(len(TOK) - len(p) + 1):
        if TOK[i:i + len(p)] == p: return WORDS[i + len(p) - 1]["e"] if end else WORDS[i]["s"]
    raise ValueError(phrase)
# (mode, start, end, src, extra)  photo: hands holding both products (576x1024); x/y/z = Ken Burns focus
# B-roll from the GLOSSKN journey reel, only where it adds meaning
EV = [("video", at("loves to do") - 0.05, at("but hates"), "media/br/makeup.mp4", {}),          # loves to do makeup
      ("video", at("but hates"), at("then this box") - 0.05, "media/br/remove.mp4", {}),    # hates to remove it
      ("video", at("doesn't burn") - 0.05, at("formula", end=True) + 0.1, "media/br/eyes.mp4", {})]   # no burn, no sting, tear free
els, tl = [], []
els.append(f'<div id="spkw"><video id="spk" class="clip" src="media/founder.mp4" playsinline data-start="0" data-duration="{DUR}" data-track-index="0" data-has-audio="true"></video></div>')
SPLIT_Y = 250
for k, (m, a, b, src, x) in enumerate(EV):
    a, b = round(a, 3), round(b, 3); cid = f"e{k}"
    if m == "video":
        els.append(f'<div class="ev full" id="{cid}"><video id="{cid}-v" class="clip" src="{src}" muted playsinline data-start="{a}" data-duration="{b - a:.3f}" data-track-index="2"></video></div>')
        tl.append(f'tl.set("#{cid}",{{opacity:0}},0);tl.set("#{cid}",{{opacity:1}},{a});tl.set("#{cid}",{{opacity:0}},{b});')
        continue
    cls = "full" if m == "photo" else "split"
    els.append(f'<div class="clip ev {cls}" id="{cid}" data-start="{a}" data-duration="{b - a:.3f}" data-track-index="3">'
               f'<div class="ph" id="{cid}-p" style="background-image:url({src});background-position:{x["fx"]}% {x["fy"]}%;transform-origin:{x["fx"]}% {x["fy"]}%"></div></div>')
    tl.append(f'tl.fromTo("#{cid}-p",{{scale:{x["z0"]}}},{{scale:{x["z1"]},duration:{b - a:.3f},ease:"none"}},{a});')
    if m == "split":
        tl.append(f'tl.fromTo("#{cid}",{{yPercent:-100}},{{yPercent:0,duration:0.35,ease:"power3.out"}},{a});')
        tl.append(f'tl.to("#spkw",{{y:{SPLIT_Y},duration:0.35,ease:"power3.out"}},{a});')
        tl.append(f'tl.to("#{cid}",{{yPercent:-100,duration:0.3,ease:"power3.in"}},{b - 0.3:.3f});')
        tl.append(f'tl.to("#spkw",{{y:0,duration:0.3,ease:"power3.in"}},{b - 0.3:.3f});')
    else:
        tl.append(f'tl.fromTo("#{cid}",{{opacity:0}},{{opacity:1,duration:0.2}},{a});tl.to("#{cid}",{{opacity:0,duration:0.2}},{b - 0.2:.3f});')
# subtitles: 2-4 words, one lilac word, positioned per layout
HL = {"makeup", "remove", "box", "two", "unique", "gentle", "burn", "sting", "tear", "free", "balm", "nongreasy", "soft",
      "best", "power", "bands", "wristbands", "clothes", "wet", "face", "wash"}
chunks, cur = [], []
for i, w in enumerate(WORDS):
    cur.append(w); nxt = WORDS[i + 1] if i + 1 < len(WORDS) else None
    if nxt is None or len(cur) >= 4 or re.search(r"[.,?!]$", w["w"]) or nxt["s"] - w["e"] > 0.35 or (len(cur) >= 3 and sum(len(x["w"]) + 1 for x in cur) > 17):
        chunks.append(cur); cur = []
for k, c in enumerate(chunks):
    a = c[0]["s"] - 0.05
    b = min(c[-1]["e"] + 0.25, chunks[k + 1][0]["s"] - 0.05) if k + 1 < len(chunks) else DUR
    mid = (a + b) / 2; lay = next((m for m, ea, eb, *_ in EV if ea <= mid <= eb), None)
    top = 700 if lay == "split" else 1300
    hl = next((j for j, w in enumerate(c) if norm(w["w"]) in HL), -1)
    txt = " ".join(f'<span class="{"hl" if j == hl else ""}">{html.escape("non-greasy" if norm(w["w"]) == "nongreasy" else w["w"].rstrip(",."))}</span>' for j, w in enumerate(c))
    els.append(f'<div class="clip subc" data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="6"><div class="sub" id="c{k}" style="top:{top}px">{txt}</div></div>')
    tl.append(f'tl.fromTo("#c{k}",{{opacity:0,y:14}},{{opacity:1,y:0,duration:0.18,ease:"power2.out"}},{a:.3f});')
CSS = """
@font-face { font-family: "Playfair Display"; font-weight: 600; src: url(fonts/playfair-display-latin-600-normal.woff2) format("woff2"); }
@font-face { font-family: "Playfair Display"; font-style: italic; font-weight: 600; src: url(fonts/playfair-display-latin-600-italic.woff2) format("woff2"); }
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 1080px; height: 1920px; overflow: hidden; background: #fff; }
#root { position: relative; width: 1080px; height: 1920px; overflow: hidden; background: #fff; }
#spkw { position: absolute; inset: 0; } #spk { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.ev { position: absolute; left: 0; width: 1080px; overflow: hidden; }
.ev.full { top: 0; height: 1920px; } .ev.full video { width: 100%; height: 100%; object-fit: cover; }
.ev.split { top: 0; height: 860px; z-index: 4; border-bottom: 10px solid #fff; box-shadow: 0 10px 30px rgba(40,20,50,.18); }
.ph { position: absolute; inset: 0; background-size: cover; background-repeat: no-repeat; }
.subc { position: absolute; inset: 0; z-index: 20; }
.sub { position: absolute; left: 60px; right: 60px; text-align: center; color: #fff; font: 600 62px/1.15 "Playfair Display", serif;
       letter-spacing: -.3px; text-shadow: 0 2px 4px rgba(20,10,26,.75), 0 4px 18px rgba(20,10,26,.5); }
.sub .hl { color: #d7b6e2; font-style: italic; }
"""
page = f"""<!doctype html><html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width={W}, height={H}" />
<script src="vendor/gsap.min.js"></script><style>{CSS}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="{W}" data-height="{H}">
{chr(10).join(els)}
</div><script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(tl)}
tl.set({{}}, {{}}, {DUR});
window.__timelines["main"] = tl;
</script></body></html>"""
open(os.path.join(P, "index.html"), "w").write(page)
print("events", len(EV), "subs", len(chunks), [(m, round(a, 2), round(b, 2)) for m, a, b, *_ in EV])
