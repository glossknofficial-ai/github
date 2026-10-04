"""words.json (source-clip word timings) -> captions.ass on the edited timeline + caption_pops.json"""
import json, os, re, sys

S = os.path.dirname(os.path.abspath(__file__))
W, H = 2160, 3840
PURPLE = "&H00E2B6D7&"  # #d7b6e2 in ASS BGR
WHITE = "&H00FFFFFF&"
EMPHASIS = set(sys.argv[1].lower().split(",")) if len(sys.argv) > 1 else set()

tl = json.load(open(os.path.join(S, "timeline.json")))
words = json.load(open(os.path.join(S, "words.json")))


def to_out(x):
    for p in tl["pieces"]:
        if p["a"] - 0.05 <= x <= p["b"] + 0.05:
            return p["out"] + min(max(x, p["a"]), p["b"]) - p["a"]
    return None


ws = []
for w in words:
    s, e = to_out(w["s"]), to_out(w["e"])
    txt = w["w"].strip()
    if s is None or not txt:
        continue
    if e is None or e <= s:
        e = s + 0.25
    ws.append(dict(t=txt, s=s, e=e))

# Group into short punchy lines: max 3 words / 16 chars, break on punctuation or pauses
groups, cur = [], []
for i, w in enumerate(ws):
    cur.append(w)
    nxt = ws[i + 1] if i + 1 < len(ws) else None
    chars = sum(len(x["t"]) + 1 for x in cur)
    if (not nxt or len(cur) >= 3 or chars >= 16 or re.search(r"[.,!?]$", w["t"])
            or nxt["s"] - w["e"] > 0.35):
        groups.append(cur); cur = []


def ts(x):
    x = max(0, x); h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f"{h}:{m:02d}:{s:05.2f}"


hdr = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Poppins ExtraBold,300,{WHITE},{WHITE},&H50000000&,&H64000000&,0,0,0,0,100,100,2,0,1,9,10,2,120,120,1200,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
ev, pops, last_pop = [], [], -9
for g in groups:
    g0, g1 = g[0]["s"], g[-1]["e"] + 0.12
    for k, w in enumerate(g):  # one event per active word: active word purple + bigger
        a = w["s"] if k else g0
        b = g[k + 1]["s"] if k + 1 < len(g) else g1
        parts = []
        for j, x in enumerate(g):
            word = x["t"].upper().strip(",.")
            if j == k:
                parts.append(r"{\c" + PURPLE + r"\fscx112\fscy112}" + word + r"{\c" + WHITE + r"\fscx100\fscy100}")
            else:
                parts.append(word)
        intro = r"{\blur1.5\fscx80\fscy80\t(0,90,\fscx100\fscy100)}" if k == 0 else r"{\blur1.5}"
        ev.append(f"Dialogue: 0,{ts(a)},{ts(b)},Cap,,0,0,0,,{intro}{' '.join(parts)}")
        key = re.sub(r"\W", "", w["t"].lower())
        if (key in EMPHASIS or (k == 0 and not EMPHASIS)) and w["s"] - last_pop > 2.2:
            pops.append(round(w["s"], 3)); last_pop = w["s"]
open(os.path.join(S, "captions.ass"), "w").write(hdr + "\n".join(ev) + "\n")
json.dump(pops, open(os.path.join(S, "caption_pops.json"), "w"))
print(len(ws), "words", len(groups), "lines", len(pops), "pops")
