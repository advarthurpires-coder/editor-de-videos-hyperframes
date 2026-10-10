from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H = 1080, 1920
txt = 'Make do dia '
f = ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-SemiBold.otf', 50)
ef = ImageFont.truetype('/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf', 109)
def emoji(ch, size):
    im = Image.new('RGBA', (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((0, 0), ch, font=ef, embedded_color=True)
    im = im.crop(im.getbbox()); r = size / im.height
    return im.resize((round(im.width * r), size), Image.LANCZOS)
em = [emoji('✨', 50), emoji('💋', 50)]
tw = f.getlength(txt); total = tw + sum(e.width for e in em) + 6
x0 = (W - total) / 2; y = 250
layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
d.text((x0, y), txt, font=f, fill=(255, 255, 255, 255))
x = x0 + tw
for e in em:
    layer.alpha_composite(e, (round(x), y + 6)); x += e.width + 6
# sombra suave para legibilidade
sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); a = layer.split()[3]
sh.putalpha(a.point(lambda v: int(v * 0.55)).filter(ImageFilter.GaussianBlur(6)))
out = Image.new('RGBA', (W, H), (0, 0, 0, 0)); out.alpha_composite(sh, (0, 3)); out.alpha_composite(layer)
out.save('titulo.png'); print('ok', round(total))
