"""GLOSSKN cart reel v2, modelled on the AJIO reference: each story lifts out of the story bar and drops into the
cart, the cart fills with that product, the remaining stories slide over. Lilac set with soft window-light,
then the 'LAST FEW hours left' cake screen. 10 s, 1080x1920. Product art, labels and logo are the original pixels."""
import os, json, subprocess
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); V = "media/v2"
W, H, DUR, PANEL = 1080, 1920, 10.0, 615
DROPS = [("cleanse", 392, (600, 1060)), ("melt", 655, (470, 1060)), ("reset", 918, (330, 1030))]
T0 = [0.6, 1.95, 3.3]; LIFT, FLY = 0.16, 0.85         # reference-style gravity drop, a touch slower
HOLD_END = 6.75
els, tl, pops, ticks = [], [], [], []
# set: lilac backdrop with drifting window light + soft floor shadow
els.append('<div id="post"><div id="beams"></div><div id="floor"></div></div>')
tl.append(f'tl.fromTo("#beams",{{x:-30}},{{x:40,duration:{DUR},ease:"none"}},0);')
# cart, filling up stage by stage
for k in range(4):
    els.append(f'<img class="cart" id="cart{k}" src="{V}/cart{k}.png" style="top:{PANEL}px" />')
    tl.append(f'tl.set("#cart{k}",{{opacity:{1 if k == 0 else 0}}},0);')
els.append(f'<img id="panel" src="{V}/panel.png" />')
# story circles (exact crops) sitting in the story bar
for i, (name, cx, _) in enumerate(DROPS):
    els.append(f'<div class="story" id="st{i}" style="left:{cx - 125}px;top:180px"><img class="sc" id="st{i}c" src="{V}/circle_{name}.png" />'
               f'<img class="sl" id="st{i}l" src="{V}/label_{name}.png" /></div>')
for i, (name, cx, (tx, ty)) in enumerate(DROPS):
    t = T0[i]; land = t + LIFT + FLY
    # like the reference: label fades, the circle lifts, spins one full turn while it falls with gravity
    tl.append(f'tl.to("#st{i}l",{{opacity:0,duration:0.12}},{t:.2f});')
    tl.append(f'tl.to("#st{i}",{{scale:1.06,y:-10,duration:{LIFT},ease:"power2.out"}},{t:.2f});')
    tl.append(f'tl.to("#st{i}",{{x:{tx - cx},y:{ty - 306},scale:0.82,duration:{FLY},ease:"power2.in"}},{t + LIFT:.2f});')
    tl.append(f'tl.fromTo("#st{i}c",{{rotation:0}},{{rotation:{-360 if i % 2 == 0 else 360},duration:{LIFT + FLY},ease:"power1.inOut"}},{t:.2f});')
    # landing: picture melts into the product while the story ring ripples out and fades, with tiny spark lines
    tl.append(f'tl.to("#st{i}",{{opacity:0,duration:0.16,ease:"none"}},{land - 0.02:.2f});')
    els.append(f'<div class="ring" id="rg{i}" style="left:{tx - 95}px;top:{ty - 95}px"></div>')
    tl.append(f'tl.set("#rg{i}",{{opacity:0}},0);')
    tl.append(f'tl.fromTo("#rg{i}",{{opacity:1,scale:1}},{{opacity:0,scale:1.6,duration:0.42,ease:"power2.out"}},{land - 0.04:.2f});')
    land = land + 0.06
    ticks.append(round(t, 3))
    tl.append(f'tl.to("#cart{i + 1}",{{opacity:1,duration:0.18}},{land - 0.06:.2f});tl.set("#cart{i}",{{opacity:0}},{land + 0.14:.2f});')
    els.append(f'<div class="burst" id="bu{i}" style="left:{tx}px;top:{ty}px">' + "".join(f'<i style="--a:{a}deg"></i>' for a in range(0, 360, 45)) + '</div>')
    tl.append(f'tl.set("#bu{i} i",{{opacity:0}},0);')
    tl.append(f'tl.fromTo("#bu{i} i",{{opacity:1,"--d":"0px",scale:1}},{{opacity:0,"--d":"95px",scale:0.4,duration:0.55,ease:"power2.out"}},{land - 0.04:.2f});')
    pops.append(round(land - 0.05, 3))
    for j in range(i + 1, len(DROPS)):   # the rest slide over to fill the gap
        tl.append(f'tl.to("#st{j}",{{x:"-=263",duration:0.45,ease:"power2.inOut"}},{land - 0.1:.2f});')   # slide over once it has dropped
LAST = T0[-1] + LIFT + FLY
# finished cart: title shimmer + badge pulse
els.append(f'<div id="shine" style="left:40px;top:650px;width:520px;height:350px"></div>')
els.append(f'<img id="badge" src="media/badge.png" style="left:655px;top:1286px;width:300px;height:300px" />')
tl.append(f'tl.set("#badge",{{opacity:0}},0);tl.set("#badge",{{opacity:1}},{LAST + 0.15:.2f});')
tl.append(f'tl.fromTo("#shine",{{backgroundPosition:"-140% 0"}},{{backgroundPosition:"240% 0",duration:1.1,ease:"power2.inOut"}},{LAST + 0.2:.2f});')
for t in (LAST + 0.2, LAST + 0.85):
    tl.append(f'tl.fromTo("#badge",{{scale:1}},{{scale:1.12,duration:0.22,ease:"power2.out",yoyo:true,repeat:1}},{t:.2f});')
# scene A out, cake screen in
tl.append(f'tl.to(["#panel",".cart",".story","#badge","#shine"],{{opacity:0,y:-40,duration:0.28,ease:"power2.in"}},{HOLD_END:.2f});')
B = HOLD_END
els.append('<div id="sceneB"><img class="full" src="media/v2/cake_original.png" /></div>')   # her original design, untouched
tl.append(f'tl.set("#sceneB",{{opacity:0}},0);')
tl.append(f'tl.fromTo("#sceneB",{{opacity:0}},{{opacity:1,duration:0.35,ease:"power1.out"}},{B + 0.18:.2f});')
CSS = open(os.path.join(P, "pipeline", "style2.css")).read()
html = f"""<!doctype html>
<html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width={W}, height={H}" />
<script src="vendor/gsap.min.js"></script><style>{CSS}</style></head>
<body><div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="{W}" data-height="{H}">
<audio id="bed" src="media/v2/sfx.wav" data-start="0" data-duration="{DUR}" data-track-index="1"></audio>
{chr(10).join(els)}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(tl)}
tl.set({{}}, {{}}, {DUR});
window.__timelines["main"] = tl;
</script></body></html>"""
open(os.path.join(P, "index.html"), "w").write(html)
json.dump({"pops": pops, "ticks": ticks, "shine": round(LAST + 0.2, 3), "dur": DUR}, open(os.path.join(P, V, "cues.json"), "w"))
print("ok, pops at", pops)
