# Upscale Real-ESRGAN (realesr-general-x4v3, ONNX) da gravação inteira, 30 fps CFR, saída 1080x1890 (mistura 75% IA + 25% Lanczos).
# Uso: python3 -I tools/upscale.py src/original.mov realesr-general-x4v3.onnx src/original_sr.mp4
import sys, subprocess, numpy as np, cv2, onnxruntime as ort
src, model, dst = sys.argv[1], sys.argv[2], sys.argv[3]
W0, H0, W, H, MIX = 576, 1008, 1080, 1890, 0.75
so = ort.SessionOptions(); so.intra_op_num_threads = 4
sess = ort.InferenceSession(model, so, providers=['CPUExecutionProvider'])
dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', src, '-vf', 'fps=30', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', '30', '-i', '-',
                        '-c:v', 'libx264', '-preset', 'slow', '-crf', '11', '-pix_fmt', 'yuv420p', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', dst], stdin=subprocess.PIPE)
n = 0
while True:
    b = dec.stdout.read(W0 * H0 * 3)
    if len(b) < W0 * H0 * 3: break
    im = np.frombuffer(b, np.uint8).reshape(H0, W0, 3)
    y = sess.run(None, {'x': (im.astype(np.float32) / 255).transpose(2, 0, 1)[None].copy()})[0][0].transpose(1, 2, 0)
    sr = cv2.resize(np.clip(y, 0, 1), (W, H), interpolation=cv2.INTER_AREA)
    lz = cv2.resize(im, (W, H), interpolation=cv2.INTER_LANCZOS4).astype(np.float32) / 255
    out = (np.clip(MIX * sr + (1 - MIX) * lz, 0, 1) * 255 + .5).astype(np.uint8)
    enc.stdin.write(out.tobytes()); n += 1
    if n % 30 == 0: print(n, flush=True)
enc.stdin.close(); enc.wait(); print('fim', n)
