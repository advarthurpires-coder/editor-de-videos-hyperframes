# Monta o vídeo-base 1080x1920 (30 fps, sem áudio) e o recorte da pessoa com transparência, quadro a quadro iguais:
#   assets/media/base.mp4     — só os trechos com fala (roteiro.CORTES), zoom alternado a cada corte, punch-ins,
#                               enquadramento que acompanha a cabeça, cor (pessoa em destaque, fundo mais escuro)
#   assets/media/pessoa.webm  — VP9 com alfa: a mesma imagem, só a pessoa (para as palavras-chave ficarem atrás dela)
#   tools/linha_tempo.json    — cabeça em coordenadas de saída, por quadro (posiciona palavras e 3D)
# Fonte: src/original_sr.mp4 (upscale Real-ESRGAN 1080x1890, 30 fps); sem ele, gravação ampliada com Lanczos (prévia).
# Máscara: src/mascara.mkv (tools/segmentar.py), refinada com filtro guiado pela imagem ampliada.
# Uso: python3 -I tools/montar_video.py   (PREVIA=1 força a prévia sem upscale)
import json, os, subprocess, sys
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from roteiro import SEGS, FPS, FIM_FALA  # noqa: E402

D = os.path.dirname(os.path.abspath(__file__)) + "/.."
OW, OH = 1080, 1920
W0, H0 = 576, 1008
SW, SH = 1080, 1890
K = SW / W0
SRC = f"{D}/src/original_sr.mp4"
PREVIA = not os.path.exists(SRC) or os.environ.get("PREVIA") == "1"
EXTRA = 0.6                  # último quadro congelado sob a transição para a cartela

# zoom por trecho (início, fim) — vizinhos sempre com enquadramentos bem diferentes
ZOOM = [
    (1.02, 1.06),   # 1 Meus irmãos, tudo bem?
    (1.16, 1.20),   # 2 Estou passando aqui neste momento para te convidar
    (1.02, 1.05),   # 3 que nesse sábado, dia 24 de outubro, às 7 e meia, será promovido (calendário e relógio dos lados)
    (1.10, 1.16),   # 4 o nosso primeiro culto Hero... (tela dividida com o flyer)
    (1.25, 1.28),   # 5 venha,
    (1.04, 1.08),   # 6 traga mais um (clone ao lado), que será tremendo (punch), a unção de Deus
    (1.02, 1.06),   # 7 momento de adoração e comunhão com os irmãos (carrossel de fotos)
    (1.18, 1.22),   # 8 Venha, não fica fora dessa, não
    (1.08, 1.12),   # 9 tá bom?
]
# (tempo da gravação, zoom alvo, duração da rampa)
PUNCH = [(16.62, 1.22, 0.08), (17.50, 1.07, 0.35)]
ALTURA_CABECA = 0.36         # centro do rosto a 36% da altura do quadro (selfie bem fechada)

TRK = json.load(open(f"{D}/tools/rastreio.json"))["f"]


def rosto(ts):
    """centro do rosto e largura (pixels da fonte ampliada), com o vizinho conhecido nos quadros sem detecção."""
    i = min(len(TRK) - 1, max(0, int(round(ts * FPS))))
    for d in range(0, 40):
        for j in (i - d, i + d):
            if 0 <= j < len(TRK) and TRK[j]:
                return np.array(TRK[j]) * K
    return np.array([SW * 0.5, SH * 0.3, 330])


def smooth(t):
    t = min(1.0, max(0.0, t))
    return t * t * t * (t * (6 * t - 15) + 10)


quadros = []   # (índice do quadro na fonte, x0, y0, cw, ch, zoom)
for k, s in enumerate(SEGS):
    a, n = s["src"], s["n"]
    ts = np.array([a + j / FPS for j in range(n)])
    P = np.array([rosto(t) for t in ts])
    ker = np.exp(-0.5 * (np.arange(-24, 25) / 8.0) ** 2); ker /= ker.sum()
    Pp = np.pad(P, ((24, 24), (0, 0)), mode="edge")
    P = np.stack([np.convolve(Pp[:, c], ker, "valid") for c in range(3)], 1)
    z0, z1 = ZOOM[k]
    for j in range(n):
        z = z0 + (z1 - z0) * smooth(j / max(1, n - 1))
        for tp, zp, dr in PUNCH:
            if a <= tp <= s["fim_src"] and ts[j] >= tp:
                z = z + (zp - z) * smooth((ts[j] - tp) / dr)
        cw, ch = OW / z, OH / z
        x0 = float(np.clip(P[j, 0] - cw * 0.5, 0, SW - cw))
        y0 = float(np.clip(P[j, 1] - ch * ALTURA_CABECA, 0, SH - ch))
        quadros.append((int(round(ts[j] * FPS)), x0, y0, cw, ch, z, P[j]))
for _ in range(int(round(EXTRA * FPS))):
    quadros.append(quadros[-1])


def caixa(x, r):
    return cv2.blur(x, (2 * r + 1, 2 * r + 1))


def guiado(I, p, r=6, eps=1e-3):
    """filtro guiado (He et al.) com guia em luminância: borda da máscara segue a borda real da imagem"""
    mI, mp = caixa(I, r), caixa(p, r)
    a = (caixa(I * p, r) - mI * mp) / (caixa(I * I, r) - mI * mI + eps)
    b = mp - a * mI
    return caixa(a, r) * I + caixa(b, r)


def grade(x, alfa):
    """cor: pessoa com contraste e pele quente; fundo (parede clara) um pouco mais baixo e menos saturado."""
    x = x.astype(np.float32) / 255
    ycc = cv2.cvtColor(x, cv2.COLOR_BGR2YCrCb); Y = ycc[..., 0]
    mid = Y - cv2.GaussianBlur(Y, (0, 0), 2.0)
    clar = Y - cv2.GaussianBlur(Y, (0, 0), 16)
    Y = np.clip(Y + 0.20 * mid + 0.16 * clar, 0, 1)
    Y = Y + 0.09 * np.sin(np.pi * (Y - 0.5)) * (1 - Y) * 1.2
    Y = np.where(Y > 0.80, 0.80 + (Y - 0.80) * 0.65, Y)          # postes e vitrines não estouram
    ycc[..., 0] = np.clip(Y, 0, 1)
    x = cv2.cvtColor(ycc, cv2.COLOR_YCrCb2BGR)
    x[..., 2] *= 1.04; x[..., 1] *= 1.0; x[..., 0] *= 0.94          # quente (paleta preto/amarelo do HERO)
    lum = (x[..., 0] * 0.114 + x[..., 1] * 0.587 + x[..., 2] * 0.299)[..., None]
    pessoa = lum + (x - lum) * 1.08
    fundo = lum + (x - lum) * 0.78
    fundo = fundo * 0.84 + np.array([0.006, 0.004, 0.0], np.float32)  # luz do dia: fundo só um pouco abaixo
    a = alfa[..., None]
    out = pessoa * a + fundo * (1 - a)
    # vinheta suave
    yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float32)
    return np.clip(out, 0, 1)


_yy, _xx = np.mgrid[0:OH, 0:OW].astype(np.float32)
VINHETA = (1 - 0.30 * np.clip(((_xx - OW / 2) / (OW * 0.62)) ** 2 + ((_yy - OH * 0.42) / (OH * 0.62)) ** 2, 0, 1) ** 1.3)[..., None].astype(np.float32)


class Fonte:
    """Leitor sequencial (pedidos crescentes, com saltos para frente nos cortes)."""
    def __init__(self, path, gray=False):
        self.cap = cv2.VideoCapture(path); self.i = -1; self.f = None; self.gray = gray
    def get(self, idx):
        if idx < self.i: self.cap.set(cv2.CAP_PROP_POS_FRAMES, idx); self.i = idx - 1
        while self.i < idx:
            ok, f = self.cap.read()
            if not ok: break
            self.i += 1; self.f = f
        return self.f[..., 0] if self.gray else self.f


if __name__ == "__main__":
    os.makedirs(f"{D}/assets/media", exist_ok=True); os.makedirs(f"{D}/renders", exist_ok=True)
    if PREVIA:
        tmp = f"{D}/renders/orig30.mp4"
        if not os.path.exists(tmp):
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{D}/src/original.mov", "-vf", f"fps=30,scale={SW}:{SH}:flags=lanczos",
                            "-c:v", "libx264", "-crf", "14", "-preset", "fast", tmp], check=True)
        fonte = Fonte(tmp)
    else:
        fonte = Fonte(SRC)
    masc = Fonte(f"{D}/src/mascara.mkv", gray=True)
    base = f"{D}/assets/media/base.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "slow", "-crf", "13", "-pix_fmt", "yuv420p", "-g", "15", "-keyint_min", "15",
                            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-movflags", "+faststart", base], stdin=subprocess.PIPE)
    enc_a = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-crf", "14", "-b:v", "0", "-row-mt", "1", "-cpu-used", "4",
                              "-g", "15", "-auto-alt-ref", "0", f"{D}/assets/media/pessoa.webm"], stdin=subprocess.PIPE)
    mapa, prev_m, prev_idx = [], None, None
    for q, (idx, x0, y0, cw, ch, z, P) in enumerate(quadros):
        f = fonte.get(idx)
        M = np.array([[OW / cw, 0, -x0 * OW / cw], [0, OH / ch, -y0 * OH / ch]])
        img = cv2.warpAffine(f, M, (OW, OH), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
        # máscara: fonte 464x832 -> geometria ampliada -> mesmo recorte
        m = masc.get(idx).astype(np.float32) / 255
        m = cv2.resize(m, (SW, SH), interpolation=cv2.INTER_CUBIC)
        m = cv2.warpAffine(m, M, (OW, OH), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        if prev_m is not None and idx == prev_idx + 1:
            m = 0.7 * m + 0.3 * prev_m                                    # estabilidade temporal leve
        prev_m, prev_idx = m, idx
        cru = m
        m = np.clip((m - 0.30) / 0.45, 0, 1)                              # corta o "véu" do fundo
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
        lumi = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
        mg = np.clip(guiado(lumi, m, 5, 2e-3), 0, 1)
        mg = np.clip((mg - 0.06) / 0.88, 0, 1)
        out = grade(img, mg) * VINHETA
        bgr = (out * 255 + 0.5).astype(np.uint8)
        enc.stdin.write(bgr.tobytes())
        a8 = (mg * 255 + 0.5).astype(np.uint8)
        enc_a.stdin.write(np.dstack([bgr, a8]).tobytes())
        mapa.append([round((P[0] - x0) * OW / cw), round((P[1] - y0) * OH / ch), round(P[2] * OW / cw), round(z, 3)])
        if q % 60 == 0: print(q, "/", len(quadros), flush=True)
    enc.stdin.close(); enc_a.stdin.close(); enc.wait(); enc_a.wait()
    json.dump({"fps": FPS, "fim_fala": FIM_FALA, "segs": SEGS, "rosto": mapa}, open(f"{D}/tools/linha_tempo.json", "w"), separators=(",", ":"))
    with open(f"{D}/assets/linha_tempo.js", "w") as fh:
        fh.write("window.ROSTO = " + json.dumps(mapa, separators=(",", ":")) + ";\n")
    print("base.mp4 + pessoa.webm", len(quadros), "quadros,", round(len(quadros) / FPS, 2), "s", "(PRÉVIA, sem upscale)" if PREVIA else "")
