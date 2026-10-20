"""Prepara os recursos do reel "Culto Hero" a partir dos arquivos ORIGINAIS enviados (sem redesenho).

1. Recorte da dupla do flyer (fundo removido com `hyperframes remove-background`) -> limpeza da base.
2. Contornos vetoriais do "H" gótico da logomarca HERO (região branca do glifo, com os furos dos
   traços internos) -> extrusão 3D no Three.js.
3. Silhueta externa da logomarca HERO -> "adesivo" 3D com espessura, face frontal com a própria arte.
4. Logo Lagoinha Patrocínio aparado.

Uso: python3 -I tools/preparar_assets.py
"""
import json

import cv2
import numpy as np
from PIL import Image, ImageFilter

BR = "assets/brand"
FO = "assets/fotos"


def contornos(mask, eps, min_area):
    """Contornos externos + furos (RETR_CCOMP), simplificados. Coordenadas em pixels."""
    cs, hier = cv2.findContours(mask.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    formas = []
    if hier is None:
        return formas
    hier = hier[0]
    for i, c in enumerate(cs):
        if hier[i][3] != -1 or cv2.contourArea(c) < min_area:
            continue
        ext = cv2.approxPolyDP(c, eps, True)[:, 0, :].tolist()
        furos = []
        j = hier[i][2]
        while j != -1:
            if cv2.contourArea(cs[j]) >= min_area * 0.05:
                furos.append(cv2.approxPolyDP(cs[j], eps, True)[:, 0, :].tolist())
            j = hier[j][0]
        formas.append({"ext": ext, "furos": furos})
    return formas


def normalizar(formas, cx, cy, esc):
    f = lambda p: [round((p[0] - cx) / esc, 4), round(-(p[1] - cy) / esc, 4)]
    return [{"ext": [f(p) for p in s["ext"]], "furos": [[f(p) for p in h] for h in s["furos"]]} for s in formas]


# ------------------------------------------------------------------ 1. dupla do flyer
im = Image.open(f"{FO}/duo_recorte_raw.png").convert("RGBA")
a = np.array(im).astype(np.float64)
h, w = a.shape[:2]
yy = np.arange(h)[:, None] * np.ones((1, w))
xx = np.ones((h, 1)) * np.arange(w)[None, :]
fade = np.clip((660 - yy) / 120, 0, 1)                 # base some suavemente (púlpito e restos da arte do flyer)
canto = np.clip((yy - 0.62 * xx - 470) / -40, 0, 1)    # canto inferior esquerdo (vidro do púlpito)
a[..., 3] *= fade * np.maximum(canto, (xx > 300))
# contração leve do alfa para tirar o halo amarelo do flyer
alpha = Image.fromarray(a[..., 3].astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.7))
a[..., 3] = np.minimum(a[..., 3], np.array(alpha))
Image.fromarray(a.astype(np.uint8), "RGBA").save(f"{FO}/duo_recorte.png", optimize=True)

# ------------------------------------------------------------------ 2/3. logomarca HERO
lg = np.array(Image.open(f"{BR}/logo_hero_original.png").convert("RGBA")).astype(int)
al = lg[..., 3]
lum = lg[..., :3].mean(-1)
branco = (al > 128) & (lum > 128)
# "H" = componentes brancos 1 e 2 da caixa do glifo (haste + floreio superior)
x0, y0, x1, y1 = 120, 440, 470, 760
sub = branco[y0:y1, x0:x1].astype(np.uint8)
n, lab, st, _ = cv2.connectedComponentsWithStats(sub, 8)
mH = np.zeros_like(sub)
for i in range(1, n):
    if st[i, 4] > 1000 and st[i, 0] < 280:
        mH |= (lab == i).astype(np.uint8)
mH = cv2.morphologyEx(mH, cv2.MORPH_CLOSE, np.ones((2, 2), np.uint8))
ys, xs = np.nonzero(mH)
cxH, cyH = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
escH = (ys.max() - ys.min()) / 2  # meia-altura = 1 unidade
formasH = normalizar(contornos(mH, 0.8, 30), cxH, cyH, escH)

# silhueta externa da logomarca inteira (contorno preto incluído) para o "adesivo"
silh = (al > 100).astype(np.uint8)
silh = cv2.morphologyEx(silh, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
ys, xs = np.nonzero(silh)
bx0, bx1, by0, by1 = xs.min(), xs.max(), ys.min(), ys.max()
cxL, cyL = (bx0 + bx1) / 2, (by0 + by1) / 2
escL = (bx1 - bx0) / 2  # meia-largura = 1 unidade
formasL = [{"ext": s["ext"], "furos": []} for s in contornos(silh, 1.2, 400)]
formasL = normalizar(formasL, cxL, cyL, escL)
# arte frontal: recorte exato da caixa da silhueta (para mapear UV)
Image.fromarray(lg[by0:by1 + 1, bx0:bx1 + 1].astype(np.uint8), "RGBA").save(f"{BR}/logo_hero_face.png", optimize=True)

json.dump({
    "H": {"formas": formasH, "aspecto": round(float(mH.shape[1]) / mH.shape[0], 4)},
    "logo": {"formas": formasL, "w": int(bx1 - bx0 + 1), "h": int(by1 - by0 + 1)},
}, open("assets/formas_3d.json", "w"))
with open("assets/formas_3d.js", "w") as fh:
    fh.write("window.FORMAS3D = " + open("assets/formas_3d.json").read() + ";\n")
print("H:", len(formasH), "formas,", sum(len(s["furos"]) for s in formasH), "furos;",
      "logo:", len(formasL), "formas; face", bx1 - bx0 + 1, "x", by1 - by0 + 1)

# ------------------------------------------------------------------ 4. Lagoinha (aparado)
lag = Image.open(f"{BR}/logo_lagoinha_patrocinio_original.png").convert("RGBA")
lag.crop(lag.getbbox()).save(f"{BR}/logo_lagoinha_patrocinio.png", optimize=True)
