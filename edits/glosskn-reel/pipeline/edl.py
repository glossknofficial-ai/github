"""Edit decision list for the GlossKN Power Cleanse reel. All times are seconds in the
source clip (After_1.mp4) unless they say `out`. Every cut is snapped to a 30fps frame."""
import json, os

FPS = 30
HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
UPLOADS = "/root/.claude/uploads/9c33fb63-44ba-5032-927b-020ae3867ced/"
MAIN = UPLOADS + "1dd37292-After_1.mp4"
BROLL_FILES = {
    "robe": UPLOADS + "cf0c6cdb-WhatsApp_Video_2026-10-04_at_3.00.39_PM.mp4",
    "floral": UPLOADS + "4e9865cf-WhatsApp_Video_2026-10-04_at_3.02.49_PM.mp4",
    "close": UPLOADS + "024d7f60-WhatsApp_Video_2026-10-04_at_3.01.51_PM.mp4",  # landscape
}

q = lambda x: round(x * FPS) / FPS

# Kept source ranges, grouped by camera setup. Only dead air / long pauses are removed;
# the "After 12 years" opener and the desk turnaround into "Hi, I am Jaspreet" stay whole.
SHOTS = [
    [(0.03, 4.80)],                                              # sofa: After 12 years ... create it
    [(5.20, 9.62)],                                              # desk: turns around, Hi I am Jaspreet ...
    [(11.00, 13.69), (13.91, 19.40)],                            # office: most makeup goes around the eyes ...
    [(19.70, 23.27), (23.50, 29.30)],                            # sofa + bottle: mission ... face wash ...
    [(29.93, 31.43), (31.62, 40.24), (40.58, 41.98), (42.26, 47.97)],  # curtain: labs, testing, friends & family
    [(48.12, 50.07), (50.40, 50.96), (51.17, 52.62)],            # product: power cleanse ... gentle yet effective
]
SHOTS = [[(q(a), q(b)) for a, b in s] for s in SHOTS]

# Framing toggles (punch-in / punch-out) without removing time, on sentence beats.
ZOOM_TOGGLES = [q(t) for t in (1.46, 7.09, 14.98, 21.59, 25.99, 38.59, 46.75, 49.33)]
PUNCH = 1.14

# B-roll replacing the picture (voice continues). (src_a, src_b, clip, clip in-point)
BROLL = [
    (34.29, 36.92, "robe", 0.0),     # "I tried every version on my eyes first"
    (36.92, 37.75, "floral", 0.3),   # "and then with friends"
    (37.75, 38.59, "close", 0.0),    # "and family"
    (42.26, 44.00, "floral", 1.2),   # "We kept refining until"   (she looks down)
    (44.00, 45.60, "close", 0.9),    # "it truly felt gentle"     (she looks down)
    (45.60, 46.40, "robe", 3.2),     # "If it still"              (she looks down)
    (46.40, 47.05, "floral", 2.95),  # "stung,"                   (last downward glance)
]
BROLL = [(q(a), q(b), n, off) for a, b, n, off in BROLL]

# Full-screen designed cards drawn by HyperFrames where she looks away and no footage exists
# yet (lab B-roll slots — swap for stock footage once mixkit.co is reachable).
CARD_SLOTS = [
    (30.55, 31.43, "labs"),       # "multiple labs"
    (33.42, 34.12, "formula"),    # "reworking the formula"
    (40.58, 41.98, "backtolab"),  # "went back to the lab"
]


def pieces():
    out, t = [], 0.0
    for si, shot in enumerate(SHOTS):
        for a, b in shot:
            out.append(dict(a=a, b=b, out=round(t * FPS) / FPS, shot=si))
            t += b - a
    return out


PIECES = pieces()
TOTAL = round(sum(p["b"] - p["a"] for p in PIECES) * FPS) / FPS
SHOT_STARTS = [next(p["out"] for p in PIECES if p["shot"] == s) for s in range(len(SHOTS))]


def to_out(x, snap="next"):
    """Map a source time onto the edited timeline (None if it falls in a removed gap and snap=None)."""
    for p in PIECES:
        if p["a"] - 1e-6 <= x <= p["b"] + 1e-6:
            return p["out"] + x - p["a"]
    if snap is None:
        return None
    return min((p["out"] for p in PIECES if p["a"] >= x), default=TOTAL)


def words():
    ws = json.load(open(os.path.join(PROJECT, "data", "words.json")))
    res = []
    for w in ws:
        s, e = to_out(w["s"], None), to_out(w["e"], None)
        if s is None and e is None:
            continue
        s = s if s is not None else to_out(w["s"])
        e = e if e is not None else s + 0.2
        res.append(dict(text=w["w"].strip(), src=w["s"], start=round(s, 3), end=round(max(e, s + 0.08), 3)))
    return res


if __name__ == "__main__":
    print("total", TOTAL, "shot starts", SHOT_STARTS)
