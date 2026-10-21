# Segmentação da pessoa quadro a quadro (MediaPipe selfie_multiclass_256x256) na gravação original, 30 fps CFR.
# Grava src/mascara.mkv (cinza, FFV1 sem perdas, 576x1008: 255 = pessoa) e tools/rastreio.json
# ({"fps":30,"w":464,"h":832,"f":[[cx_cabeça, cy_cabeça, largura_rosto] | null, ...]} em pixels da fonte).
# Uso: python3 -I tools/segmentar.py src/original.mov /home/user/modelos/selfie_multiclass.tflite
import sys, json, subprocess, numpy as np, cv2
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions

src, modelo = sys.argv[1], sys.argv[2]
W, H = 576, 1008
seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=BaseOptions(model_asset_path=modelo), running_mode=vision.RunningMode.VIDEO,
    output_confidence_masks=True, output_category_mask=False))
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-vf", "fps=30", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "gray", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
                        "-c:v", "ffv1", "src/mascara.mkv"], stdin=subprocess.PIPE)
trk, n = [], 0
while True:
    b = dec.stdout.read(W * H * 3)
    if len(b) < W * H * 3: break
    im = np.frombuffer(b, np.uint8).reshape(H, W, 3)
    r = seg.segment_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(im)), int(n * 1000 / 30))
    cm = [np.squeeze(m.numpy_view()) for m in r.confidence_masks]   # 0 fundo, 1 cabelo, 2 pele corpo, 3 pele rosto, 4 roupa, 5 outros
    pessoa = np.clip(1.0 - cm[0], 0, 1)
    enc.stdin.write((pessoa * 255 + 0.5).astype(np.uint8).tobytes())
    rosto = cm[3] > 0.5
    ys, xs = np.nonzero(rosto)
    if len(xs) > 200:
        x0, x1 = np.percentile(xs, [3, 97]); y0, y1 = np.percentile(ys, [3, 97])
        trk.append([round((x0 + x1) / 2, 1), round((y0 + y1) / 2, 1), round(x1 - x0, 1)])
    else:
        trk.append(None)
    n += 1
enc.stdin.close(); enc.wait()
json.dump({"fps": 30, "w": W, "h": H, "f": trk}, open("tools/rastreio.json", "w"))
print("quadros", n, "com rosto", sum(1 for f in trk if f))
for i in range(0, n, 60): print(i / 30, trk[i])
