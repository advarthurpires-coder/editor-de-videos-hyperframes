# Pipeline de nitidez v2: limpa blocos de compressão na fonte, upscale Lanczos,
# nitidez fina só na luminância + "clarity" (contraste local), glow bem discreto.
import cv2, numpy as np

def clean_source(f):
    # remove blocos/ruído de compressão do WhatsApp sem apagar textura (h baixo)
    return cv2.fastNlMeansDenoisingColored(f, None, 3, 3, 5, 15)

def grade2(img, scale=1.0):
    x = img.astype(np.float32) / 255
    ycc = cv2.cvtColor(x, cv2.COLOR_BGR2YCrCb)
    Y = ycc[..., 0]
    # nitidez fina (detalhe de cílios, sobrancelha, fios) + clarity (volume do rosto)
    fine = Y - cv2.GaussianBlur(Y, (0, 0), 1.1 * scale + 0.2)
    mid = Y - cv2.GaussianBlur(Y, (0, 0), 3.0 * scale + 0.5)
    clar = Y - cv2.GaussianBlur(Y, (0, 0), 14 * scale + 1)
    Y = Y + 0.90 * fine + 0.35 * mid + 0.18 * clar
    ycc[..., 0] = np.clip(Y, 0, 1)
    x = cv2.cvtColor(ycc, cv2.COLOR_YCrCb2BGR)
    lum = x[..., 0] * 0.114 + x[..., 1] * 0.587 + x[..., 2] * 0.299
    x = np.clip(x, 0, 1) ** 0.95
    x = lum[..., None] + (x - lum[..., None]) * 1.05
    x[..., 2] *= 0.985; x[..., 0] *= 1.015
    # glow discreto e só nos realces mais altos (não lava a imagem)
    hl = np.clip((lum - 0.68) / 0.32, 0, 1)[..., None] * x
    small = cv2.resize(hl, (x.shape[1] // 4, x.shape[0] // 4), interpolation=cv2.INTER_AREA)
    blur = cv2.resize(cv2.GaussianBlur(small, (0, 0), 4), (x.shape[1], x.shape[0]))
    x = 1 - (1 - np.clip(x, 0, 1)) * (1 - 0.10 * blur)
    return (np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8)
