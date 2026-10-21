# Rastreia o rosto quadro a quadro (OpenCV Haar, sem rede) na gravação original, a 30 fps CFR.
# Grava tools/rastreio.json: {"fps":30, "w":480, "h":1068, "f":[[cx,cy,lado] | null, ...]} em pixels da fonte.
# Uso: python3 -I tools/rastrear.py src/convite_original.mp4
import sys, json, subprocess, numpy as np, cv2
src = sys.argv[1]
W, H = 480, 1068
casc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-vf", "fps=30", "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
out, prev = [], None
while True:
    b = p.stdout.read(W * H)
    if len(b) < W * H: break
    g = cv2.equalizeHist(np.frombuffer(b, np.uint8).reshape(H, W))
    fs = casc.detectMultiScale(g, 1.08, 5, minSize=(60, 60))
    if len(fs):
        # o maior rosto; se houver referência anterior, o mais próximo dela
        fs = sorted(fs, key=lambda r: -r[2] * r[3])[:3]
        if prev: fs = sorted(fs, key=lambda r: abs(r[0] + r[2] / 2 - prev[0]) + abs(r[1] + r[3] / 2 - prev[1]))
        x, y, w, h = [int(v) for v in fs[0]]
        prev = [x + w / 2, y + h / 2, w]
        out.append([round(prev[0], 1), round(prev[1], 1), w])
    else:
        out.append(None)
json.dump({"fps": 30, "w": W, "h": H, "f": out}, open("tools/rastreio.json", "w"))
ok = sum(1 for f in out if f)
print("quadros", len(out), "com rosto", ok)
for i in range(0, len(out), 30): print(i / 30, out[i])
