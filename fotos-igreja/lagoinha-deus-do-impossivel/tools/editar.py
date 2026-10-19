"""Edição das fotos do culto "Deus do Impossível" (Lagoinha Patrocínio).

Só tratamento global (cor, luz, contraste, grão, vinheta) e composição com máscaras
suaves: nenhum pixel de rosto é redesenhado. Saída em 4:5 (1080x1350).

Uso: python3 tools/editar.py   (rodar a partir da pasta do projeto)
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

RAIZ = Path(__file__).resolve().parent.parent
ORIG = RAIZ / "originais"
OUT_C = RAIZ / "saida" / "carrossel"
OUT_I = RAIZ / "saida" / "individuais"
W, H = 1080, 1350
FONTES = Path("/usr/share/fonts/opentype/inter")
CREME = (244, 239, 228)
TINTA = (24, 26, 28)
rng = np.random.default_rng(7)


def fonte(peso, tam):
    return ImageFont.truetype(str(FONTES / f"InterDisplay-{peso}.otf"), tam)


LOGO = Image.open(RAIZ / "tools" / "logo_lagoinha.png")


# --------------------------------------------------------------------------- base
def abrir(n):
    """Abre a foto e corta fora a faixa inferior onde está o logo antigo (y >= 1396)."""
    im = Image.open(ORIG / f"p{n:02d}.jpg").convert("RGB")
    return im.crop((0, 0, im.width, 1390))


def enquadrar(im, w, h, fx=0.5, fy=0.5, zoom=1.0):
    """Corta im para a proporção w:h (ponto focal fx, fy) e redimensiona."""
    iw, ih = im.size
    alvo = w / h
    if iw / ih > alvo:
        ch, cw = ih, ih * alvo
    else:
        cw, ch = iw, iw / alvo
    cw, ch = cw / zoom, ch / zoom
    x0 = min(max(fx * iw - cw / 2, 0), iw - cw)
    y0 = min(max(fy * ih - ch / 2, 0), ih - ch)
    return im.resize((w, h), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))


def f32(im):
    return np.asarray(im, dtype=np.float32) / 255.0


def u8(a):
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8))


def lum(a):
    return a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114


def curva(x, pontos):
    xs, ys = zip(*pontos)
    return np.interp(x, xs, ys)


def suavizar(im, r=1.2):
    """Ameniza o serrilhado/posterização das fotos (vieram comprimidas)."""
    return Image.blend(im, im.filter(ImageFilter.GaussianBlur(r)), 0.45)


# --------------------------------------------------------------------------- cor
def rgb_hsv(a):
    mx, mn = a.max(-1), a.min(-1)
    d = mx - mn + 1e-6
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    h = np.where(mx == r, (g - b) / d % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    s = np.where(mx > 0, (mx - mn) / (mx + 1e-6), 0)
    return h, s, mx


def hsv_rgb(h, s, v):
    c = v * s
    x = c * (1 - np.abs((h / 60) % 2 - 1))
    m = v - c
    z = np.zeros_like(h)
    i = (h // 60).astype(int) % 6
    r = np.choose(i, [c, x, z, z, x, c])
    g = np.choose(i, [x, c, c, x, z, z])
    b = np.choose(i, [z, z, x, c, c, x])
    return np.stack([r + m, g + m, b + m], -1)


def acertar_luzes(a):
    """Luz de palco azul-royal vira azul-petróleo; roxo/magenta perde saturação.
    Pele (matizes laranja, 0-50°) não é tocada."""
    h, s, v = rgb_hsv(np.clip(a, 0, 1))
    azul = np.clip(1 - np.abs(h - 232) / 45, 0, 1)
    h = h - (h - 196) * 0.65 * azul
    s = s * (1 - 0.35 * azul)
    roxo = np.clip(1 - np.abs(h - 285) / 55, 0, 1)
    s = s * (1 - 0.75 * roxo)
    return hsv_rgb(h % 360, s, v)


def grade_noite(a, sat=0.78, quente=1.0):
    """Paleta-mestra do post: sombras azul-petróleo, luzes creme, pretos foscos."""
    a = acertar_luzes(a)
    L = lum(a)[..., None]
    a = L + (a - L) * sat
    a = curva(a, [(0, 0.035), (0.18, 0.13), (0.5, 0.5), (0.82, 0.86), (1, 0.97)])
    L = lum(a)[..., None]
    sombra = np.clip(1 - L * 2.2, 0, 1)
    luz = np.clip((L - 0.45) * 1.8, 0, 1)
    a = a + sombra * np.array([-0.035, 0.012, 0.03]) * 1.4
    a = a + luz * np.array([0.03, 0.012, -0.03]) * quente
    return a


def grade_mono(a, tom="sepia", contraste=1.0):
    """P&B: 'sepia' (estilo Forjados) ou 'neutro' (fotojornalismo)."""
    L = lum(a)
    L = curva(L, [(0, 0.03), (0.2, 0.12 / contraste), (0.5, 0.5), (0.8, 0.84), (1, 0.98)])
    L = L[..., None]
    if tom == "sepia":
        sombra = np.array([0.0, 0.03, 0.042])
        luz = np.array([0.08, 0.035, -0.05])
        return L + np.clip(1 - L * 2, 0, 1) * sombra + np.clip(L - 0.4, 0, 1) * luz
    return L + np.clip(1 - L * 2, 0, 1) * np.array([0, 0.008, 0.02])


def vinheta(a, forca=0.45, raio=0.85):
    h, w = a.shape[:2]
    y, x = np.mgrid[0:h, 0:w]
    d = np.sqrt(((x - w / 2) / (w / 2)) ** 2 + ((y - h / 2) / (h / 2)) ** 2) / raio
    m = 1 - forca * np.clip(d - 0.55, 0, 1) ** 1.6
    return a * m[..., None]


def grao(a, forca=0.035):
    h, w = a.shape[:2]
    g = rng.normal(0, 1, (h // 2 + 1, w // 2 + 1)).astype(np.float32)
    g = np.asarray(Image.fromarray(g).resize((w, h), Image.BILINEAR))
    L = lum(np.clip(a, 0, 1))
    peso = 0.6 + 0.8 * L * (1 - L) * 2
    return a + (g * forca * peso)[..., None]


def acabamento(a, vin=0.45, g=0.035):
    return grao(vinheta(a, vin), g)


def tratar(im, estilo="noite", **kw):
    a = f32(suavizar(im))
    if estilo == "noite":
        a = grade_noite(a, **kw)
    else:
        a = grade_mono(a, estilo, **kw)
    return a


def gradiente(h, w, inicio, fim, vertical=True):
    """Máscara 0->1 entre as frações inicio e fim (suavizada)."""
    t = np.linspace(0, 1, h if vertical else w)
    m = np.clip((t - inicio) / (fim - inicio), 0, 1)
    m = m * m * (3 - 2 * m)
    return np.repeat(m[:, None], w, 1) if vertical else np.repeat(m[None, :], h, 0)


def cantos(im, r):
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width - 1, im.height - 1), r, fill=255)
    return m


def por_logo(tela, largura=230, margem=44, cor=None, pos=None):
    lg = LOGO.resize((largura, round(LOGO.height * largura / LOGO.width)), Image.LANCZOS)
    if cor:
        tint = Image.new("RGBA", lg.size, cor + (0,))
        tint.putalpha(lg.getchannel("A"))
        lg = tint
    tela.alpha_composite(lg, pos or (W - largura - margem, H - lg.height - margem))


def texto_centro(d, caixa, linhas, fnt, cor, entre=1.02, rastreio=0):
    x0, y0, x1, y1 = caixa
    alt = fnt.size * entre
    total = alt * len(linhas)
    y = (y0 + y1) / 2 - total / 2
    for ln in linhas:
        largura = d.textlength(ln, font=fnt) + rastreio * (len(ln) - 1)
        x = (x0 + x1) / 2 - largura / 2
        if rastreio:
            for c in ln:
                d.text((x, y), c, font=fnt, fill=cor)
                x += d.textlength(c, font=fnt) + rastreio
        else:
            d.text((x, y), ln, font=fnt, fill=cor)
        y += alt


def salvar(tela, nome, pasta=OUT_C):
    pasta.mkdir(parents=True, exist_ok=True)
    tela.convert("RGB").save(pasta / nome, quality=93, subsampling=0)
    print("ok", nome)


# --------------------------------------------------------------------------- slides
def s01_capa():
    """Dupla exposição (Forjados + Aguiar): ministra no alto, culto inteiro embaixo."""
    topo = tratar(enquadrar(abrir(1), W, H, fx=0.4, fy=0.38, zoom=1.12))
    # só a parte de baixo da foto 2 (banda + plateia), sem o telão
    base_h = 640
    base = tratar(enquadrar(abrir(2).crop((0, 720, 1152, 1390)), W, base_h), sat=0.7)
    base_full = np.zeros_like(topo)
    base_full[H - base_h:] = base
    m = gradiente(H, W, 0.57, 0.72)[..., None]
    a = topo * (1 - m) + base_full * m
    a = a * (1 - 0.35 * gradiente(H, W, 0.0, 0.14)[::-1][..., None])  # escurece o topo
    a = a * (1 - 0.62 * gradiente(H, W, 0.66, 0.86)[..., None])  # base escura p/ o título
    tela = u8(acabamento(a, 0.5)).convert("RGBA")
    d = ImageDraw.Draw(tela)
    texto_centro(d, (0, 1085, W, 1165), ["DEUS DO IMPOSSÍVEL"], fonte("SemiBold", 60), CREME, rastreio=8)
    texto_centro(d, (0, 1158, W, 1205), ["NÃO DESISTIU DE MIM"], fonte("Light", 26), CREME, rastreio=11)
    por_logo(tela, 170, pos=((W - 170) // 2, H - 92))
    salvar(tela, "01_capa.jpg")


def s_unica(n, nome, estilo, fx=0.5, fy=0.5, zoom=1.0, vin=0.5, pasta=OUT_C, **kw):
    """Foto única com bastante respiro (fotojornalismo IIR)."""
    a = tratar(enquadrar(abrir(n), W, H, fx, fy, zoom), estilo, **kw)
    tela = u8(acabamento(a, vin)).convert("RGBA")
    por_logo(tela, 170, 40)
    salvar(tela, nome, pasta)


def s_tabuleiro(n, nome, cima, baixo, fx=0.5, fy=0.4, zoom=1.0, ref=None, pasta=OUT_C):
    """Tabuleiro 2x2 (GET Church): frase / foto P&B / foto em cor / resposta."""
    meia_w, meia_h = W // 2, H // 2
    foto = enquadrar(abrir(n), meia_w, meia_h, fx, fy, zoom)
    mono = acabamento(tratar(foto, "sepia"), 0.25, 0.045)
    cor = acabamento(tratar(foto, "noite", sat=0.7), 0.25, 0.045)
    papel = np.ones((meia_h, meia_w, 3), np.float32) * np.array(CREME) / 255
    papel = grao(papel, 0.018)
    tela = Image.new("RGBA", (W, H))
    for img, pos in [(papel, (0, 0)), (mono, (meia_w, 0)), (cor, (0, meia_h)), (papel, (meia_w, meia_h))]:
        tela.paste(u8(img).convert("RGBA"), pos)
    d = ImageDraw.Draw(tela)
    f = fonte("Medium", 62)
    texto_centro(d, (30, 0, meia_w - 30, meia_h), cima, f, TINTA, 1.0, rastreio=-2.2)
    texto_centro(d, (meia_w + 30, meia_h, W - 30, H), baixo, f, TINTA, 1.0, rastreio=-2.2)
    if ref:
        texto_centro(d, (meia_w, meia_h + 440, W, meia_h + 490), [ref], fonte("Light", 26), TINTA, rastreio=6)
    por_logo(tela, 150, 36, cor=TINTA)
    salvar(tela, nome, pasta)


def s04_dois_quadros():
    """Dois quadros empilhados (Aguiar 06): plano geral + palco."""
    alto = H // 2
    a1 = tratar(enquadrar(abrir(6), W, alto, fx=0.45, fy=0.46))
    a2 = tratar(enquadrar(abrir(9), W, alto, fx=0.5, fy=0.48, zoom=1.05))
    a = np.concatenate([a1, a2], 0)
    tela = u8(acabamento(a, 0.35)).convert("RGBA")
    d = ImageDraw.Draw(tela)
    d.rectangle((0, alto - 3, W, alto + 3), fill=(10, 14, 16))
    por_logo(tela, 170, 40)
    salvar(tela, "04_dois_quadros.jpg")


def s06_mosaico():
    """Mosaico editorial em fundo claro (Ceia 02)."""
    tela_a = grao(np.ones((H, W, 3), np.float32) * np.array([236, 233, 225]) / 255, 0.015)
    tela = u8(tela_a).convert("RGBA")
    m, g = 56, 14
    cw = (W - 2 * m - 2 * g) // 3
    topo_h = 300
    celulas = [
        (5, (m, m, cw, topo_h), 0.5, 0.35),
        (12, (m + cw + g, m, cw, topo_h), 0.45, 0.32),
        (4, (m + 2 * (cw + g), m, cw, topo_h), 0.55, 0.3),
    ]
    y2 = m + topo_h + g
    h2 = H - m - y2
    esq_w = cw
    dir_x = m + cw + g
    dir_w = W - m - dir_x
    meio_h = 340
    celulas += [
        (8, (m, y2, esq_w, h2), 0.35, 0.4),
        (16, (dir_x, y2, dir_w, meio_h), 0.5, 0.3),
        (13, (dir_x, y2 + meio_h + g, dir_w, h2 - meio_h - g), 0.45, 0.42),
    ]
    for n, (x, y, w, h), fx, fy in celulas:
        a = acabamento(tratar(enquadrar(abrir(n), w, h, fx, fy)), 0.3, 0.03)
        im = u8(a).convert("RGBA")
        tela.paste(im, (x, y), cantos(im, 22))
    salvar(tela, "06_mosaico.jpg")


def s_halo(n=7, nome="09_halo.jpg", fx=0.45, fy=0.42, zoom=1.08, cx=0.46, cy=0.36, r=360, pasta=OUT_C):
    """Retrato com halo âmbar atrás (Ceia 01), aplicado só nas áreas escuras."""
    a = tratar(enquadrar(abrir(n), W, H, fx=fx, fy=fy, zoom=zoom))
    y, x = np.mgrid[0:H, 0:W]
    cx, cy = W * cx, H * cy
    d = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
    anel = np.exp(-((d - r) / 55) ** 2) + 0.35 * np.exp(-((d - r) / 160) ** 2)
    escuro = np.clip(1 - lum(a) * 2.4, 0, 1)
    brilho = (anel * escuro)[..., None] * np.array([0.85, 0.52, 0.28])
    a = 1 - (1 - a) * (1 - brilho * 0.8)  # screen
    tela = u8(acabamento(a, 0.5)).convert("RGBA")
    por_logo(tela, 170, 40)
    salvar(tela, nome, pasta)


def s10_fim():
    """Encerramento: faixa do culto em P&B + frase."""
    tela = u8(grao(np.ones((H, W, 3), np.float32) * np.array(CREME) / 255, 0.018)).convert("RGBA")
    faixa = acabamento(tratar(enquadrar(abrir(2), W - 112, 560, fx=0.5, fy=0.42), "sepia"), 0.3, 0.04)
    im = u8(faixa).convert("RGBA")
    tela.paste(im, (56, 56), cantos(im, 22))
    d = ImageDraw.Draw(tela)
    texto_centro(d, (60, 650, W - 60, 1080), ["Ele é o Deus", "do impossível.", "E não desistiu", "de você."], fonte("Medium", 84), TINTA, 1.0, rastreio=-2.5)
    por_logo(tela, 240, cor=TINTA, pos=((W - 240) // 2, H - 150))
    salvar(tela, "10_encerramento.jpg")


def individuais():
    """As 16 fotos tratadas sozinhas em 4:5, com o logo reaplicado."""
    mono = {10: "sepia", 11: "neutro"}
    for n in range(1, len(list(ORIG.glob("p*.jpg"))) + 1):
        est = mono.get(n, "noite")
        a = tratar(enquadrar(abrir(n), W, H, 0.5, 0.45), est)
        tela = u8(acabamento(a, 0.42)).convert("RGBA")
        por_logo(tela, 190, 40)
        tela.convert("RGB").save(OUT_I / f"p{n:02d}.jpg", quality=93, subsampling=0)
    print("ok individuais")


if __name__ == "__main__":
    OUT_C.mkdir(parents=True, exist_ok=True)
    OUT_I.mkdir(parents=True, exist_ok=True)
    s01_capa()
    s_unica(11, "02_bracos_abertos.jpg", "neutro", fx=0.55, fy=0.4)
    s_tabuleiro(3, "03_tabuleiro_promessa.jpg", ["“E o que dizes", "sobre mim…”"], ["não pode", "se frustrar."], fx=0.45, fy=0.38, zoom=1.15)
    s04_dois_quadros()
    s_unica(10, "05_oracao.jpg", "sepia", fx=0.5, fy=0.42, vin=0.6)
    s06_mosaico()
    s_tabuleiro(15, "07_tabuleiro_destra.jpg", ["“Sua destra", "me sustenta…”"], ["e me faz", "prevalecer."], fx=0.48, fy=0.33, zoom=1.1)
    s_unica(14, "08_geracoes.jpg", "noite", fx=0.55, fy=0.42)
    s_halo()
    s10_fim()

    # Carrossel 2 (fotos p17-p20), mesma paleta
    C2 = RAIZ / "saida" / "carrossel_2"
    s_unica(17, "01_intercessao.jpg", "noite", fx=0.42, fy=0.5, zoom=1.05, vin=0.6, pasta=C2)
    s_unica(18, "02_suplica.jpg", "sepia", fx=0.5, fy=0.4, zoom=1.08, vin=0.6, pasta=C2)
    s_tabuleiro(19, "03_tabuleiro_impossivel.jpg", ["“Parece", "impossível…”"], ["Para Deus,", "nada é", "impossível."],
                fx=0.42, fy=0.38, zoom=1.15, ref="LUCAS 1.37", pasta=C2)
    s_unica(20, "04_maos_abertas.jpg", "noite", fx=0.45, fy=0.42, pasta=C2)
    individuais()
