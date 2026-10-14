# Monta o vídeo-base 1080x1920 (30 fps, sem áudio) do reel "A visita do CRAS vai virar regra":
#   1) tela dividida (0 a INTRO s): TikTok em cima, Arthur reagindo embaixo (faixa do título fica para o HTML);
#   2) Arthur em tela cheia, só os trechos com fala (tools/cortes.json), com zoom/punch-in e enquadramento
#      que segue o rosto; 3) congela o último quadro para a cartela final.
# Também grava tools/linha_tempo.json (mapa saída -> fonte, recorte por quadro, rosto/mãos em coordenadas de saída).
# Uso: python3 -I tools/montar_video.py [escala]   (escala 0.5 = prévia rápida)
import json, os, subprocess, sys
import numpy as np, cv2
from multiprocessing import Pool

D = os.path.dirname(os.path.abspath(__file__)) + "/.."
FPS, OW, OH = 30, 1080, 1920
SW, SH = 576, 1024
SO_MAPA = len(sys.argv) > 1 and sys.argv[1] == "mapa"
ESC = float(sys.argv[1]) if len(sys.argv) > 1 and not SO_MAPA else 1.0
ow, oh = int(OW * ESC) // 2 * 2, int(OH * ESC) // 2 * 2

INTRO = 14.30            # duração da tela dividida (TikTok 0 -> 14,30 s)
REACAO_FIM = 13.20       # reação do Arthur 0 -> 13,20 s, levemente desacelerada para durar INTRO
CARTELA = 3.20           # quadro congelado sob a cartela final
FAIXA = 250              # faixa do título (topo), desenhada no HTML
TK_Y0, TK_H = 300, 405   # janela do TikTok (fonte) -> painel 1080x760
AR_Y0, AR_H = 70, 485    # janela do Arthur (fonte) -> painel 1080x910

CORTES = json.load(open(f"{D}/tools/cortes.json"))
TRK = json.load(open(f"{D}/tools/rastreio.json"))
TF = TRK["f"]; TFPS = TRK["fps"]

# ------------------------------------------------------------------ plano de zoom (tempo da fonte)
# zoom relativo ao quadro inteiro (1.0 = quadro todo). Trechos com elemento gráfico junto às mãos/mesa ficam abertos.
FIXO = {   # início do trecho (s, fonte) -> (zoom no início, zoom no fim); vizinhos sempre com enquadramentos diferentes
    14.99: (1.16, 1.24),   # "...realidade a partir de julho do ano que vem, de 2027"
    19.60: (1.00, 1.03),
    25.57: (1.24, 1.26),
    28.26: (1.00, 1.00),   # "o único residente no imóvel é você" (casa na mão)
    31.19: (1.12, 1.14),
    32.24: (1.22, 1.24),
    33.98: (1.00, 1.03),   # Bolsa Família / BPC (cartões)
    36.83: (1.00, 1.07),   # pente-fino
    42.40: (1.16, 1.20),
    44.53: (1.00, 1.00),
    45.70: (1.08, 1.11),   # cafezinho (vapor ancorado na xícara)
    51.70: (1.00, 1.00),   # porta de vidro
    56.36: (1.10, 1.12),   # duas situações (V com os dedos)
    58.65: (1.00, 1.00),   # 1ª situação (lista)
    68.37: (1.24, 1.26),   # "Mas se você mora sozinho..."
    70.58: (1.00, 1.03),
    72.25: (1.13, 1.15),
    72.99: (1.00, 1.00),   # 2ª situação
    75.71: (1.10, 1.12),
    76.93: (1.22, 1.24),
    77.93: (1.00, 1.00),   # punches internos abaixo
    85.02: (1.26, 1.29),   # "Tome muito cuidado."
    86.33: (1.00, 1.03),
    98.39: (1.00, 1.00),   # INSS / Justiça
    101.82: (1.12, 1.18),
    104.13: (1.00, 1.00),  # avião de papel sai da mão
    106.30: (1.10, 1.16),
}
# punch-in dentro do trecho: (tempo da fonte, zoom alvo), transição de 0,18 s
# boca da xícara sobre a mesa (fonte), para o vapor do "cafezinho"
XICARA = [418, 738]
PUNCH = [(78.20, 1.22), (79.25, 1.08), (82.52, 1.27)]

def fixo(a):
    """regra de zoom do trecho que começa em a (tolerância de 60 ms, os cortes têm 3 casas decimais)"""
    for t, z in FIXO.items():
        if abs(t - a) < 0.06: return z
    return None

def plano():
    zs, prev = [], None
    for k, (a, b) in enumerate(CORTES):
        if fixo(a): z0, z1 = fixo(a)
        else:
            base = 1.0 if (prev is None or prev > 1.06) else 1.13
            z0, z1 = base, base + 0.03
        if prev is not None and abs(z0 - prev) < 0.07 and not fixo(a):
            z0 = 1.13 if prev < 1.06 else 1.0; z1 = z0 + 0.03
        zs.append((z0, z1)); prev = z1
    return zs

ZS = plano()

def smooth(t):
    return t * t * t * (t * (6 * t - 15) + 10)

def zoom_em(k, ts, frac):
    z0, z1 = ZS[k]; z = z0 + (z1 - z0) * frac
    a, b = CORTES[k]
    for tp, zp in PUNCH:
        if a <= tp <= b and ts >= tp:
            z = z + (zp - z) * smooth(min(1.0, (ts - tp) / 0.18))
    return z

def rosto(ts):
    i = min(len(TF) - 1, max(0, int(round(ts * TFPS))))
    return TF[i].get("nariz", [SW / 2, SH * 0.26])

# ------------------------------------------------------------------ linha do tempo, quadro a quadro
quadros = []   # (tipo, dados)
n_intro = int(round(INTRO * FPS))
for i in range(n_intro):
    t = i / FPS
    quadros.append(("intro", {"tk": t, "ar": t * REACAO_FIM / INTRO, "push": 1.0 + 0.04 * t / INTRO}))
t_out = INTRO
segs = []
for k, (a, b) in enumerate(CORTES):
    if k == len(CORTES) - 1: b = TF[-1]["t"]
    n = int(round((b - a) * FPS))
    segs.append({"k": k, "out": round(len(quadros) / FPS, 4), "src": a, "fim_src": round(a + n / FPS, 4), "z": ZS[k]})
    # centro do rosto suavizado no trecho
    ts = [a + j / FPS for j in range(n)]
    P = np.array([rosto(x) for x in ts], np.float64)
    sig = 14.0
    ker = np.exp(-0.5 * (np.arange(-40, 41) / sig) ** 2); ker /= ker.sum()
    Pp = np.pad(P, ((40, 40), (0, 0)), mode="edge")
    P = np.stack([np.convolve(Pp[:, c], ker, "valid") for c in range(2)], 1)
    for j in range(n):
        z = zoom_em(k, ts[j], j / max(1, n - 1))
        cw, ch = SW / z, SH / z
        x0 = float(np.clip(P[j, 0] - cw / 2, 0, SW - cw))
        y0 = float(np.clip(P[j, 1] - ch * 0.34, 0, SH - ch))
        quadros.append(("fala", {"ar": ts[j], "x0": x0, "y0": y0, "cw": cw, "ch": ch, "k": k}))
ultimo = quadros[-1][1]
for i in range(int(round(CARTELA * FPS))):
    quadros.append(("fala", dict(ultimo, congelado=True)))
TOTAL = len(quadros) / FPS

# ------------------------------------------------------------------ render
def ler(src, idx):
    cap = cv2.VideoCapture(src); cap.set(cv2.CAP_PROP_POS_FRAMES, idx); ok, f = cap.read(); cap.release(); return f

def limpar(f):
    return cv2.fastNlMeansDenoisingColored(f, None, 3, 3, 5, 15)

# fonte do Arthur: original do iPhone convertido para SDR (src/arthur_hq.mp4, 1080x1920) se existir;
# senão a cópia do WhatsApp (576x1024). Coordenadas de rastreio/recorte ficam na escala 576 e são multiplicadas por K.
AR_SRC = f"{D}/src/arthur_hq.mp4" if os.path.exists(f"{D}/src/arthur_hq.mp4") else f"{D}/src/arthur.mp4"
_c = cv2.VideoCapture(AR_SRC); K = _c.get(3) / SW; _c.release()
HQ = K > 1.5
# nitidez: forte para a cópia comprimida do WhatsApp, leve para o original em 1080p
NIT = (0.32, 0.18, 0.12, 1.07) if HQ else (0.80, 0.32, 0.16, 1.04)

def grade(img, scale=1.0, nit=None):
    fn, md, cl, sat = nit or NIT
    x = img.astype(np.float32) / 255
    ycc = cv2.cvtColor(x, cv2.COLOR_BGR2YCrCb); Y = ycc[..., 0]
    fine = Y - cv2.GaussianBlur(Y, (0, 0), 1.1 * scale + 0.2)
    mid = Y - cv2.GaussianBlur(Y, (0, 0), 3.0 * scale + 0.5)
    clar = Y - cv2.GaussianBlur(Y, (0, 0), 14 * scale + 1)
    Y = Y + fn * fine + md * mid + cl * clar
    ycc[..., 0] = np.clip(Y, 0, 1)
    x = cv2.cvtColor(ycc, cv2.COLOR_YCrCb2BGR)
    lum = x[..., 0] * 0.114 + x[..., 1] * 0.587 + x[..., 2] * 0.299
    x = np.clip(x, 0, 1) ** 0.96
    x = lum[..., None] + (x - lum[..., None]) * sat
    return (np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8)

def warp(f, x0, y0, cw, ch, W, H):
    M = np.array([[W / cw, 0, -x0 * W / cw], [0, H / ch, -y0 * H / ch]])
    return cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)

class Fonte:
    """Leitor sequencial com cache dos quadros já decodificados (os pedidos são quase sempre crescentes)."""
    def __init__(self, path, limpa=True):
        self.cap = cv2.VideoCapture(path); self.i = -1; self.f = None; self.cache = {}; self.limpa = limpa
    def get(self, idx):
        if idx in self.cache: return self.cache[idx]
        if idx < self.i or idx > self.i + 90:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, idx); self.i = idx - 1
        while self.i < idx:
            ok, f = self.cap.read()
            if not ok: break
            self.i += 1; self.f = f
        out = limpar(self.f) if self.limpa else self.f
        self.cache = {idx: out}
        return out

def render_lote(args):
    ini, fim, arq = args
    tk, ar = Fonte(f"{D}/src/tiktok.mp4"), Fonte(AR_SRC, limpa=not HQ)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{ow}x{oh}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "15",
                            "-pix_fmt", "yuv420p", "-g", "30", "-keyint_min", "30", arq], stdin=subprocess.PIPE)
    s = ESC
    for q in range(ini, fim):
        tipo, d = quadros[q]
        if tipo == "intro":
            img = np.zeros((oh, ow, 3), np.uint8); img[:] = (48, 22, 10)
            p = d["push"]
            ftk = tk.get(min(653, int(round(d["tk"] * 30))))
            cw = SW / p; ch = TK_H / p
            a = warp(ftk, (SW - cw) / 2, TK_Y0 + (TK_H - ch) / 2, cw, ch, ow, int(760 * s))
            far = ar.get(int(round(d["ar"] * TFPS)))
            ch2 = AR_H / p
            b = warp(far, K * (SW - cw) / 2, K * (AR_Y0 + (AR_H - ch2) * 0.3), K * cw, K * ch2, ow, oh - int((FAIXA + 760) * s))
            img[int(FAIXA * s):int(FAIXA * s) + a.shape[0]] = a
            img[int((FAIXA + 760) * s):] = b
            tk_h = int((FAIXA + 760) * s)
            img[:tk_h] = grade(img[:tk_h], s, (0.80, 0.32, 0.16, 1.04))   # TikTok (comprimido)
            img[tk_h:] = grade(img[tk_h:], s)
        else:
            far = ar.get(int(round(d["ar"] * TFPS)))
            img = grade(warp(far, K * d["x0"], K * d["y0"], K * d["cw"], K * d["ch"], ow, oh), s)
        enc.stdin.write(img.tobytes())
    enc.stdin.close(); enc.wait()
    return arq

if __name__ == "__main__":
    out = f"{D}/assets/media/base.mp4" if ESC == 1.0 else f"{D}/renders/base_previa.mp4"
    tmp = f"{D}/renders/lotes"; os.makedirs(tmp, exist_ok=True)
    N = len(quadros); L = 4
    cortes_lote = [round(N * i / L) for i in range(L + 1)]
    lotes = [(cortes_lote[i], cortes_lote[i + 1], f"{tmp}/lote{i}.mp4") for i in range(L)]
    if not SO_MAPA:
      with Pool(L) as pool:
        arqs = pool.map(render_lote, lotes)
      with open(f"{tmp}/lista.txt", "w") as fh:
        for a in arqs: fh.write(f"file '{a}'\n")
      subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{tmp}/lista.txt", "-c", "copy",
                    "-movflags", "+faststart", out], check=True)
    # mapa para o HTML/mixagem: rosto e mãos em coordenadas de saída (1080x1920), por quadro
    mapa = []
    for tipo, d in quadros:
        if tipo == "intro": mapa.append(None); continue
        f = TF[min(len(TF) - 1, int(round(d["ar"] * TFPS)))]
        sx, sy = OW / d["cw"], OH / d["ch"]
        conv = lambda p: [round((p[0] - d["x0"]) * sx), round((p[1] - d["y0"]) * sy)]
        mapa.append({"z": round(SW / d["cw"], 3), "nariz": conv(f.get("nariz", [288, 260])), "xicara": conv(XICARA),
                     "maos": [{"palma": conv(h["palma"]), "ind": conv(h["indicador"]), "dedos": h["dedos"]} for h in f["maos"]]})
    json.dump({"fps": FPS, "intro": INTRO, "total": round(TOTAL, 3), "cartela": CARTELA, "segs": segs, "quadros": mapa},
              open(f"{D}/tools/linha_tempo.json", "w"), separators=(",", ":"))
    print("total", round(TOTAL, 2), "s;", N, "quadros ->", out)
