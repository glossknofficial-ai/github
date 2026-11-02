"""GLOSSKN cart reel, 10 s, 1080x1920. Same idea and product art; brand-styled background, slower product drop,
no zoom. Layers: animated background -> cut-out footage/stills -> small brand motion accents."""
import os, random
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H, DUR = 1080, 1920, 10.0
A_END = 163 / 30            # slowed fly-in (glitch frames removed)
HOLD_END = 6.75             # cart with all products: badge pulse + title shimmer
XF = 0.45                   # crossfade to the cake screen
B_IN = HOLD_END
rnd = random.Random(7)
els, tl = [], []

# --- background: soft brand gradient, drifting light, falling confetti (behind everything) ---
els.append('<div id="bg"></div>')
for i in range(7):
    s = rnd.randint(260, 520); x = rnd.randint(-150, 950); y = rnd.randint(500, 1800)
    col = rnd.choice(["rgba(255,255,255,.55)", "rgba(215,182,226,.45)", "rgba(255,255,255,.4)"])
    els.append(f'<div class="bokeh" id="bk{i}" style="width:{s}px;height:{s}px;left:{x}px;top:{y}px;background:{col}"></div>')
    tl.append(f'tl.fromTo("#bk{i}",{{x:0,y:0}},{{x:{rnd.randint(-90, 90)},y:{rnd.randint(-160, -40)},duration:{DUR},ease:"sine.inOut"}},0);')
COLS = ["#4a2a5a", "#b48ac6", "#d7b6e2", "#d4b06a", "#ffffff", "#8e5fa3"]
for i in range(46):
    w = rnd.randint(10, 18); h = rnd.choice([w, int(w * 1.8)]); x = rnd.randint(0, 1060)
    t0 = rnd.uniform(-6, DUR - 1); fall = rnd.uniform(6.5, 9.5); r = rnd.choice(["50%", "3px"])
    els.append(f'<div class="cf" id="cf{i}" style="left:{x}px;width:{w}px;height:{h}px;border-radius:{r};background:{rnd.choice(COLS)}"></div>')
    tl.append(f'tl.fromTo("#cf{i}",{{y:-60,rotation:{rnd.randint(0, 180)},x:0}},{{y:{H + 60},rotation:{rnd.randint(360, 900)},'
              f'x:{rnd.randint(-120, 120)},duration:{fall:.2f},ease:"none"}},{t0:.2f});')

# --- A: slowed story -> cart animation, then the finished cart ---
els.append(f'<video id="fgA" class="clip full" src="media/fgA.webm" muted playsinline data-start="0" data-duration="{A_END:.3f}" data-track-index="2"></video>')
els.append(f'<div class="clip full" id="hold" data-start="{A_END - 0.04:.3f}" data-duration="{HOLD_END + XF - A_END + 0.04:.3f}" data-track-index="3">'
           '<img class="full" src="media/holdA.png" />'
           '<div id="shine" style="left:40px;top:650px;width:520px;height:350px"></div>'
           '<img id="badge" src="media/badge.png" style="left:655px;top:1286px;width:300px;height:300px" /></div>')
tl.append(f'tl.fromTo("#shine",{{backgroundPosition:"-140% 0"}},{{backgroundPosition:"240% 0",duration:1.1,ease:"power2.inOut"}},{A_END + 0.1:.2f});')
for k, t in enumerate([A_END + 0.05, A_END + 0.75]):
    tl.append(f'tl.fromTo("#badge",{{scale:1}},{{scale:1.12,duration:0.22,ease:"power2.out",yoyo:true,repeat:1}},{t:.2f});')
tl.append(f'tl.to("#hold",{{opacity:0,y:-40,duration:0.28,ease:"power2.in"}},{HOLD_END:.2f});')   # clean hand-off: out first

# --- B: cake screen, new headline in brand type ---
els.append(f'<div class="clip full" id="sceneB" data-start="{B_IN:.3f}" data-duration="{DUR - B_IN:.3f}" data-track-index="4">'
           '<div id="glow"></div><img class="full" src="media/fgB.png" />'
           '<div id="h1">' + "".join(f'<span class="ch">{c if c != " " else "&nbsp;"}</span>' for c in "LAST FEW") + '</div>'
           '<div id="h2"><span>hours left</span></div><div id="h3">Grab your favourites now!!!</div></div>')
tl.append(f'tl.fromTo("#sceneB",{{opacity:0,y:50}},{{opacity:1,y:0,duration:0.4,ease:"power2.out"}},{B_IN + 0.22:.2f});')   # then the cake screen rises in
tl.append(f'tl.fromTo("#h1 .ch",{{y:70,opacity:0,rotation:-6}},{{y:0,opacity:1,rotation:0,duration:0.5,ease:"back.out(2)",stagger:0.05}},{B_IN + 0.35:.2f});')
tl.append(f'tl.fromTo("#h2 span",{{clipPath:"inset(0 100% 0 0)"}},{{clipPath:"inset(0 0% 0 0)",duration:0.7,ease:"power2.inOut"}},{B_IN + 0.95:.2f});')
tl.append(f'tl.fromTo("#h3",{{y:20,opacity:0}},{{y:0,opacity:1,duration:0.5,ease:"power2.out"}},{B_IN + 1.55:.2f});')
tl.append(f'tl.to("#h1",{{scale:1.04,duration:0.35,ease:"power1.inOut",yoyo:true,repeat:3}},{B_IN + 2.0:.2f});')
tl.append(f'tl.fromTo("#glow",{{opacity:0.55,scale:0.92}},{{opacity:0.95,scale:1.08,duration:0.45,ease:"sine.inOut",yoyo:true,repeat:6}},{B_IN:.2f});')

CSS = """
@font-face { font-family: "PF"; src: url(fonts/PlayfairDisplay.ttf); font-weight: 400 900; }
@font-face { font-family: "PFI"; src: url(fonts/PlayfairDisplay-Italic.ttf); font-weight: 400 900; font-style: italic; }
@font-face { font-family: "OS"; src: url(fonts/Oswald.ttf); font-weight: 200 700; }
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 1080px; height: 1920px; overflow: hidden; background: #ece4ed; }
#root { position: relative; width: 1080px; height: 1920px; overflow: hidden; }
#bg { position: absolute; inset: 0; background: radial-gradient(120% 75% at 50% 45%, #f6eff8 0%, #ece4ed 48%, #dcc8e6 100%); }
.bokeh { position: absolute; border-radius: 50%; filter: blur(60px); }
.cf { position: absolute; top: 0; opacity: .85; }
.full { position: absolute; inset: 0; width: 1080px; height: 1920px; }
#hold img, #sceneB img { position: absolute; }
#badge { position: absolute; transform-origin: 50% 50%; }
#shine { position: absolute; -webkit-mask-image: url(media/title_mask.png); -webkit-mask-size: 100% 100%; mask-image: url(media/title_mask.png); mask-size: 100% 100%;
         background: linear-gradient(105deg, transparent 35%, rgba(215,182,226,.95) 47%, rgba(255,255,255,.95) 50%, rgba(215,182,226,.95) 53%, transparent 65%);
         background-size: 60% 100%; background-repeat: no-repeat; }
#glow { position: absolute; left: 470px; top: 980px; width: 140px; height: 180px; border-radius: 50%;
        background: radial-gradient(closest-side, rgba(255,214,140,.85), rgba(255,190,120,.35) 55%, transparent); filter: blur(10px); }
#h1 { position: absolute; left: 0; right: 0; top: 440px; text-align: center; font: 700 168px/1 "OS", sans-serif; letter-spacing: 3px; color: #0d0b0e; }
#h1 .ch { display: inline-block; text-shadow: -1px 1px 0 #d7b6e2, -2px 2px 0 #d7b6e2, -3px 3px 0 #d7b6e2, -4px 4px 0 #d7b6e2, -5px 5px 0 #d7b6e2, -6px 6px 0 #d7b6e2, -7px 7px 0 #d7b6e2; }
#h2 { position: absolute; left: 0; right: 0; top: 615px; text-align: center; font: italic 600 132px/1 "PFI", serif; color: #4a2a5a; }
#h2 span { display: inline-block; padding: 0 20px 18px; }
#h3 { position: absolute; left: 0; right: 0; top: 792px; text-align: center; font: italic 500 50px/1 "PFI", serif; color: #4a2a5a; }
"""
html = f"""<!doctype html>
<html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width={W}, height={H}" />
<script src="vendor/gsap.min.js"></script><style>{CSS}</style></head>
<body><div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="{W}" data-height="{H}">
{chr(10).join(els)}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(tl)}
tl.set({{}}, {{}}, {DUR});
window.__timelines["main"] = tl;
</script></body></html>"""
open(os.path.join(P, "index.html"), "w").write(html)
print("ok", len(els), "elements")
