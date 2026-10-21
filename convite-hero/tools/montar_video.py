# Monta o vídeo-base 1080x1920 (30 fps, sem áudio): só os trechos com fala (roteiro.CORTES), com zoom alternado
# a cada corte, punch-ins nas palavras fortes, enquadramento que acompanha o rosto e correção de cor.
# Fonte: src/convite_sr.mp4 (upscale Real-ESRGAN 1080x2404, mesma linha do tempo da gravação, 30 fps CFR);
# sem ele, usa a gravação original ampliada com Lanczos (prévia).
# Grava assets/media/base.mp4 e tools/linha_tempo.json (rosto em coordenadas de saída, por quadro).
# Uso: python3 -I tools/montar_video.py
import json, os, subprocess, sys
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from roteiro import CORTES, SEGS, FPS, FIM_FALA  # noqa: E402

D = os.path.dirname(os.path.abspath(__file__)) + "/.."
OW, OH = 1080, 1920
SW, SH = 1080, 2404          # geometria do upscale (fonte 480x1068 x 2,25)
K = SW / 480
SRC = f"{D}/src/convite_sr.mp4"
PREVIA = not os.path.exists(SRC)
EXTRA = 0.5                  # quadro final congelado sob a transição para o flyer

# zoom por trecho (início, fim) — vizinhos sempre com enquadramentos bem diferentes
ZOOM = [
    (1.02, 1.08),   # Fala, meus irmãos, graça e paz
    (1.20, 1.24),   # Que Deus abençoe vocês
    (1.00, 1.06),   # Irmãos, venho aqui fazer um convite... (punch em "homens")
    (1.17, 1.21),   # Vai acontecer aqui em Patrocínio
    (1.00, 1.03),   # na Batista Lagoinha (fundo desfocado no HTML)
    (1.12, 1.16),   # o nosso primeiro culto do HERO (punch em "HERO")
    (1.00, 1.06),   # Eu quero fazer um convite muito especial
    (1.10, 1.12),   # Dia 24 de outubro (vídeo vira cartão no HTML)
    (1.26, 1.34),   # Vem!
]
# punch-in dentro do trecho: (tempo da gravação, zoom alvo); entra em 0,10 s
PUNCH = [(9.92, 1.24), (17.78, 1.32), (25.66, 1.40)]

TRK = json.load(open(f"{D}/tools/rastreio.json"))["f"]


def rosto(ts):
    """centro do rosto (pixels do upscale), com o último valor conhecido nos quadros sem detecção."""
    i = min(len(TRK) - 1, max(0, int(round(ts * FPS))))
    for d in range(0, 40):
        for j in (i - d, i + d):
            if 0 <= j < len(TRK) and TRK[j]:
                return np.array(TRK[j][:2]) * K
    return np.array([SW * 0.38, SH * 0.43])


def smooth(t):
    t = min(1.0, max(0.0, t))
    return t * t * t * (t * (6 * t - 15) + 10)


quadros = []   # (índice do quadro na fonte, x0, y0, cw, ch, zoom)
for k, s in enumerate(SEGS):
    a, n = s["src"], s["n"]
    ts = np.array([a + j / FPS for j in range(n)])
    P = np.array([rosto(t) for t in ts])
    ker = np.exp(-0.5 * (np.arange(-30, 31) / 10.0) ** 2); ker /= ker.sum()
    Pp = np.pad(P, ((30, 30), (0, 0)), mode="edge")
    P = np.stack([np.convolve(Pp[:, c], ker, "valid") for c in range(2)], 1)
    z0, z1 = ZOOM[k]
    for j in range(n):
        z = z0 + (z1 - z0) * smooth(j / max(1, n - 1))
        for tp, zp in PUNCH:
            if a <= tp <= s["fim_src"] and ts[j] >= tp:
                z = z + (zp - z) * smooth((ts[j] - tp) / 0.10)
        cw, ch = OW / z, OH / z
        x0 = float(np.clip(P[j, 0] - cw * 0.44, 0, SW - cw))
        y0 = float(np.clip(P[j, 1] - ch * 0.42, 0, SH - ch))
        quadros.append((int(round(ts[j] * FPS)), x0, y0, cw, ch, z))
for _ in range(int(round(EXTRA * FPS))):
    quadros.append(quadros[-1])


def grade(img):
    """cor: quente e com contraste (paleta amarela do HERO), realces contidos (parede branca), nitidez média."""
    x = img.astype(np.float32) / 255
    ycc = cv2.cvtColor(x, cv2.COLOR_BGR2YCrCb); Y = ycc[..., 0]
    mid = Y - cv2.GaussianBlur(Y, (0, 0), 2.2)
    clar = Y - cv2.GaussianBlur(Y, (0, 0), 18)
    Y = Y + 0.22 * mid + 0.18 * clar
    # curva S suave + compressão de realces
    Y = np.clip(Y, 0, 1)
    Y = Y + 0.10 * np.sin(np.pi * (Y - 0.5)) * (1 - Y) * 1.2
    Y = np.where(Y > 0.82, 0.82 + (Y - 0.82) * 0.72, Y)
    ycc[..., 0] = np.clip(Y, 0, 1)
    x = cv2.cvtColor(ycc, cv2.COLOR_YCrCb2BGR)
    # balanço quente: tira o azulado da parede/luz fria
    x[..., 2] *= 1.035; x[..., 1] *= 1.005; x[..., 0] *= 0.93
    lum = x[..., 0] * 0.114 + x[..., 1] * 0.587 + x[..., 2] * 0.299
    x = lum[..., None] + (x - lum[..., None]) * 1.10
    return (np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8)


class Fonte:
    """Leitor sequencial (os pedidos são crescentes, com saltos para frente nos cortes)."""
    def __init__(self, path):
        self.cap = cv2.VideoCapture(path); self.i = -1; self.f = None
    def get(self, idx):
        if idx < self.i: self.cap.set(cv2.CAP_PROP_POS_FRAMES, idx); self.i = idx - 1
        while self.i < idx:
            ok, f = self.cap.read()
            if not ok: break
            self.i += 1; self.f = f
        return self.f


if __name__ == "__main__":
    os.makedirs(f"{D}/assets/media", exist_ok=True)
    if PREVIA:
        tmp = f"{D}/renders/orig30.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{D}/src/convite_original.mp4", "-vf", f"fps=30,scale={SW}:{SH}:flags=lanczos",
                        "-c:v", "libx264", "-crf", "14", "-preset", "fast", tmp], check=True)
        fonte = Fonte(tmp)
    else:
        fonte = Fonte(SRC)
    out = f"{D}/assets/media/base.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-pix_fmt", "yuv420p", "-g", "15", "-keyint_min", "15",
                            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    mapa = []
    for q, (idx, x0, y0, cw, ch, z) in enumerate(quadros):
        f = fonte.get(idx)
        M = np.array([[OW / cw, 0, -x0 * OW / cw], [0, OH / ch, -y0 * OH / ch]])
        img = cv2.warpAffine(f, M, (OW, OH), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
        enc.stdin.write(grade(img).tobytes())
        r = rosto(idx / FPS)
        mapa.append([round((r[0] - x0) * OW / cw), round((r[1] - y0) * OH / ch), round(z, 3)])
    enc.stdin.close(); enc.wait()
    json.dump({"fps": FPS, "fim_fala": FIM_FALA, "segs": SEGS, "rosto": mapa}, open(f"{D}/tools/linha_tempo.json", "w"), separators=(",", ":"))
    print("base.mp4", len(quadros), "quadros,", round(len(quadros) / FPS, 2), "s", "(PRÉVIA, sem upscale)" if PREVIA else "")
