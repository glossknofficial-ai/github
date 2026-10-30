"""AI upscale (Real-ESRGAN realesr-general-x4v3, run with onnxruntime) of the founder video to 1080x1920.
The AI result is blended with a plain Lanczos upscale (AI_MIX) so skin keeps natural texture.
The white logo card at the end needs no AI and is upscaled plainly. Writes media/enhanced.mp4 (with original audio)."""
import os, subprocess, sys, time
import numpy as np, onnxruntime as ort
from PIL import Image
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); M = os.path.join(P, "media")
SRC, OUT = os.path.join(M, "voice_only.mp4"), os.path.join(M, "enhanced.mp4")
W0, H0, W, H, FPS, AI_MIX, LOGO_AT = 576, 1024, 1080, 1920, 30, 0.65, 20.65
so = ort.SessionOptions(); so.intra_op_num_threads = os.cpu_count()
sess = ort.InferenceSession(os.path.join(M, "realesr-general-x4v3.onnx"), so, providers=["CPUExecutionProvider"])
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-i", SRC, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "10", "-preset", "slow", "-pix_fmt", "yuv420p",
                        "-c:a", "copy", "-shortest", OUT], stdin=subprocess.PIPE)
n, t0 = 0, time.time()
while True:
    buf = dec.stdout.read(W0 * H0 * 3)
    if len(buf) < W0 * H0 * 3: break
    fr = np.frombuffer(buf, np.uint8).reshape(H0, W0, 3)
    plain = np.asarray(Image.fromarray(fr).resize((W, H), Image.LANCZOS), np.float32)
    if n / FPS < LOGO_AT:
        y = sess.run(None, {"input": (fr.astype(np.float32) / 255).transpose(2, 0, 1)[None]})[0][0].transpose(1, 2, 0)
        ai = np.asarray(Image.fromarray((np.clip(y, 0, 1) * 255).round().astype(np.uint8)).resize((W, H), Image.LANCZOS), np.float32)
        out = ai * AI_MIX + plain * (1 - AI_MIX)
    else:
        out = plain
    enc.stdin.write(np.clip(out, 0, 255).round().astype(np.uint8).tobytes()); n += 1
    if n % 30 == 0: print(f"frame {n}  {time.time() - t0:.0f}s", flush=True)
enc.stdin.close(); enc.wait(); print("done", n, "frames", f"{time.time() - t0:.0f}s")
