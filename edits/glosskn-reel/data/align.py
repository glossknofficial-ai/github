import re, json, wave, os
from pocketsphinx import Decoder, get_model_path
raw = open('script.txt').read().replace("were'nt", "weren't").replace('facewash', 'face wash').replace('..', '. ')
disp = re.findall(r"[A-Za-z0-9']+[.,:!?]*", raw)          # display tokens (keep punctuation)
norm = [re.sub(r"[^a-z0-9']", '', t.lower()) for t in disp]
norm = ['twelve' if n == '12' else n for n in norm]
mp = get_model_path()
d = Decoder(hmm=os.path.join(mp, 'en-us', 'en-us'), dict=os.path.join(mp, 'en-us', 'cmudict-en-us.dict'), loglevel='FATAL')
d.add_word('jaspreet', 'JH AE S P R IY T', True)
d.add_word('glosskn', 'G L AO S K IH N', True)
missing = [n for n in set(norm) if d.lookup_word(n) is None]
print('missing', missing)
d.set_align_text(' '.join(norm))
w = wave.open('main.wav'); buf = w.readframes(w.getnframes())
d.start_utt(); d.process_raw(buf, full_utt=True); d.end_utt()
segs = [(s.word, s.start_frame / 100, s.end_frame / 100) for s in d.seg() if s.word not in ('<s>', '</s>', '<sil>', '(NULL)')]
print(len(segs), len(norm))
out = []
i = 0
for word, s, e in segs:
    word = re.sub(r'\(\d+\)$', '', word)
    while i < len(norm) and norm[i] != word: i += 1
    if i < len(norm):
        out.append(dict(w=' ' + disp[i], s=s, e=e)); i += 1
json.dump(out, open('words.json', 'w'))
for o in out: print(f"{o['s']:6.2f} {o['e']:6.2f} {o['w']}")
