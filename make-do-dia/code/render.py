# Renderiza o reel 9:16 1080x1920 30fps a partir da EDL, com rastreio facial e tratamento de cor.
import cv2, numpy as np, subprocess, sys, os
from edl import EDL
D = os.path.dirname(os.path.abspath(__file__)) + '/..'
SRC = {'A': f'{D}/src/A.mp4', 'B': f'{D}/src/B.mp4'}
TRK = {k: np.load(f'{D}/track{k}.npy') for k in SRC}
OW, OH, FPS = 1080, 1920, 30
SW, SH = 464, 832
BEAT = 0.5
# zoom relativo ao quadro inteiro da fonte e posição-alvo do ponto de interesse no quadro de saída
FR = {'w':   (1.10, 'nose',  0.36),
      'm':   (1.38, 'nose',  0.40),
      'eye': (1.85, 'eyes',  0.46),
      'lip': (1.85, 'mouth', 0.50)}
scale = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
ow, oh = int(OW * scale) // 2 * 2, int(OH * scale) // 2 * 2

def anchor(src, t, kind):
    tr = TRK[src]; m = (np.abs(tr[:, 0] - t) <= 0.45) & (tr[:, 1] > 0)
    if not m.any(): return None
    r = tr[m]
    if kind == 'nose':  p = r[:, [10, 11]]
    elif kind == 'eyes': p = (r[:, [6, 7]] + r[:, [8, 9]]) / 2
    else: p = (r[:, [12, 13]] + r[:, [14, 15]]) / 2
    return np.median(p, 0)

def clip_frames(src, t0, n):
    cmd = ['ffmpeg', '-v', 'error', '-ss', f'{t0:.3f}', '-i', SRC[src], '-frames:v', str(n),
           '-vf', f'fps={FPS}', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-']
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, SH, SW, 3)
    return fr

def grade(img):
    x = img.astype(np.float32) / 255
    # nitidez leve (compensa o upscale da fonte em baixa resolução)
    x = x + 0.35 * (x - cv2.GaussianBlur(x, (0, 0), 2.0 * scale + 0.5))
    lum = x[..., 0] * 0.114 + x[..., 1] * 0.587 + x[..., 2] * 0.299
    # luminosidade natural: leve gama, toque de saturação, neutraliza um pouco o laranja da madeira
    x = np.clip(x, 0, 1) ** 0.93
    x = lum[..., None] + (x - lum[..., None]) * 1.04
    x[..., 2] *= 0.985; x[..., 0] *= 1.015
    # glow: realces difusos (efeito pele iluminada)
    hl = np.clip((lum - 0.52) / 0.48, 0, 1)[..., None] * x
    small = cv2.resize(hl, (x.shape[1] // 4, x.shape[0] // 4), interpolation=cv2.INTER_AREA)
    blur = cv2.resize(cv2.GaussianBlur(small, (0, 0), 6), (x.shape[1], x.shape[0]))
    x = 1 - (1 - np.clip(x, 0, 1)) * (1 - 0.30 * blur)
    return (np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8)

out = sys.argv[1]
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24',
    '-s', f'{ow}x{oh}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '17',
    '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
log = []
for ci, (src, t0, beats, fr_kind, label) in enumerate(EDL):
    n = int(round(beats * BEAT * FPS))
    frames = clip_frames(src, t0, n)
    assert len(frames) == n, (ci, len(frames), n)
    z, kind, ty = FR[fr_kind]
    cw = SW / z; ch = cw * 16 / 9
    if ch > SH: ch = SH; cw = ch * 9 / 16
    # trajetória do ponto de interesse, suavizada
    pts = []
    for k in range(n):
        a = anchor(src, t0 + k / FPS, kind); pts.append(a)
    valid = [p for p in pts if p is not None]
    fb = np.median(valid, 0) if valid else np.array([SW / 2, SH * 0.3])
    P = np.array([p if p is not None else fb for p in pts], np.float64)
    sig = 6.0  # ~0,2 s
    ker = np.exp(-0.5 * (np.arange(-15, 16) / sig) ** 2); ker /= ker.sum()
    Ppad = np.pad(P, ((15, 15), (0, 0)), mode='edge')
    P = np.stack([np.convolve(Ppad[:, j], ker, 'valid') for j in range(2)], 1)
    # final: leve push-in contínuo nas tomadas longas
    for k in range(n):
        zz = 1.0 + (0.04 * k / n if label.startswith('final') or ci == 0 else 0.0)
        cwk, chk = cw / zz, ch / zz
        x0 = np.clip(P[k, 0] - cwk / 2, 0, SW - cwk); y0 = np.clip(P[k, 1] - chk * ty, 0, SH - chk)
        M = np.array([[ow / cwk, 0, -x0 * ow / cwk], [0, oh / chk, -y0 * oh / chk]])
        img = cv2.warpAffine(frames[k], M, (ow, oh), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
        enc.stdin.write(grade(img).tobytes())
    log.append(f'{ci+1:02d} {src} {t0:6.1f}s {beats*BEAT:.1f}s {fr_kind:4s} {label}')
    print(log[-1], flush=True)
enc.stdin.close(); enc.wait()
