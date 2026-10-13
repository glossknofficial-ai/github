# Google Flow (Veo 3.1): GLOSSKN Power Melt ingredient reel

## Setup in Flow

- Mode: **Frames to Video**
- First frame: `start-frame.png` (empty clear tube)
- Last frame: `end-frame.png` (the real labelled tube)
- Model: Veo 3.1 (Quality, not Fast)
- Aspect ratio: 9:16 (portrait)
- Duration: 8 seconds
- Outputs: 4. Pick the best take.

## Prompt (paste everything between the lines)

---
Locked-off static camera, vertical 9:16 premium skincare commercial, photorealistic macro product cinematography. A single cosmetic tube stands upright and perfectly still in the centre of a seamless soft lavender studio set (colour #d1b8e3) with a matte tabletop and a soft shadow falling to the right. The tube starts completely clear and empty, like glass. Four natural ingredients appear one after another from the top of the frame, release their contents into the open top of the tube, then leave. Each ingredient adds a visible layer inside the clear tube, so the tube fills from the bottom up.

0–2 s, MORINGA: a fresh sprig of moringa leaves (small bright-green oval leaflets on thin pale stems) drifts down from the top edge and hovers just above the tube. The leaves gently crumble and dissolve into a fine, vivid green moringa powder that sifts down in a soft dusty stream into the tube, settling as a golden-green layer at the bottom. The empty sprig floats up and out of the top of frame.

2–4 s, JOJOBA: a glossy brown jojoba seed, cracked open to show its pale kernel, descends from the top and pauses above the tube. Plump, pearly, pale-gold drops of jojoba oil fall from the crack one by one, landing with a soft glossy splash and forming a pale-gold layer above the green. The seed rises out of frame.

4–6 s, PLUM KERNEL: a ripe purple plum cut in half, showing its amber flesh and brown kernel stone, lowers into view. A silky, continuous ribbon of deep-amber plum kernel oil pours from the kernel into the tube, with tiny bubbles, forming an amber layer. The plum half lifts away out of frame.

6–7 s, SQUALANE: with no ingredient object, an ultra-thin, crystal-clear, glassy thread of squalane falls straight from the top of frame into the tube, catching tiny sparkles of light, and forms a clear glossy top layer.

7–8 s, REVEAL: the layers settle and the tube smoothly becomes the finished opaque white GLOSSKN Power Melt tube shown in the final frame, with its label crisp, unchanged and perfectly legible.

Style: soft diffused key light from the upper left, gentle rim light, shallow depth of field on falling particles, slow graceful motion like slow-motion macro footage, rich natural colours for the ingredients, clean high-end beauty aesthetic.

Audio: close-mic ASMR only, with no music and no voice: dry powder sifting and soft hiss for moringa, thick wet plops for jojoba, a slow viscous pour with faint bubbles for plum oil, a fine glassy trickle for squalane, and a soft airy shimmer at the reveal.

Avoid: hands, people, extra products, extra bottles or jars, on-screen text, captions, subtitles, logos other than the one on the final tube, camera movement, zoom, cuts, the tube moving or tilting, distorted or changed label text, mess or spills outside the tube, colour changes to the background.
---

## If one 8-second clip feels too rushed

Generate it as four shots with **Extend** (or Scene Builder), using the same style, audio and avoid lines in each:

1. Frames to Video. First frame `start-frame.png`. Prompt: just the MORINGA paragraph, stretched to the full 8 seconds.
2. Extend. JOJOBA paragraph.
3. Extend. PLUM KERNEL paragraph.
4. Extend with the last frame set to `end-frame.png`. SQUALANE and REVEAL paragraphs.

## After you download

Send the clip back. Veo may redraw small label text slightly wrong, so I'll lay the real packshot over the final second so the label is pixel-perfect. Then I'll trim it to length and balance the ASMR audio.
