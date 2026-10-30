"""Force-align data/script_actual.txt to the founder audio -> data/words.json (pocketsphinx, offline)."""
import json, os, re, sys, wave
from pocketsphinx import Decoder, get_model_path
HERE = os.path.dirname(os.path.abspath(__file__)); PROJECT = os.path.dirname(HERE)
wav = sys.argv[1]
SCRIPT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(PROJECT, "data", "script_actual.txt")
OUT = sys.argv[3] if len(sys.argv) > 3 else os.path.join(PROJECT, "data", "words.json")
raw = open(SCRIPT).read() + ("" if len(sys.argv) > 2 else " i was literally")
disp = re.findall(r"[A-Za-z0-9']+[.,:!?]*", raw)
norm = [re.sub(r"[^a-z0-9']", "", t.lower()) for t in disp]
mp = get_model_path()
d = Decoder(hmm=os.path.join(mp, "en-us", "en-us"), dict=os.path.join(mp, "en-us", "cmudict-en-us.dict"), loglevel="FATAL")
d.add_word("glosskn", "G L AO S K IH N", True)
missing = sorted({n for n in norm if d.lookup_word(n) is None}); print("missing", missing)
d.set_align_text(" ".join(norm))
w = wave.open(wav); buf = w.readframes(w.getnframes())
d.start_utt(); d.process_raw(buf, full_utt=True); d.end_utt()
segs = [(re.sub(r"\(\d+\)$", "", s.word), s.start_frame / 100, s.end_frame / 100) for s in d.seg() if s.word not in ("<s>", "</s>", "<sil>", "(NULL)")]
out, i = [], 0
for word, s, e in segs:
    while i < len(norm) and norm[i] != word: i += 1
    if i < len(norm):
        out.append(dict(w=disp[i], s=s, e=e)); i += 1
json.dump(out, open(OUT, "w"))
print(len(out), "of", len(norm), "aligned; last:", out[-6:])
