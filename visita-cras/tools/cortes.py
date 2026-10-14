# Calcula os trechos com fala (remove pausas) a partir do áudio do Arthur e grava tools/cortes.json
# Uso: python3 -I tools/cortes.py src/arthur.mp4
import sys, re, json, subprocess
src = sys.argv[1]
INI_FALA, FIM = 13.25, 108.30        # antes de 13,25 s: reação em silêncio (vai para a tela dividida)
PRE, POS, GAP_MIN = 0.07, 0.13, 0.20  # folga antes/depois da fala; pausa mínima a cortar
o = subprocess.run(["ffmpeg", "-i", src, "-af", f"silencedetect=noise=-36dB:d={GAP_MIN}", "-f", "null", "-"],
                   capture_output=True, text=True).stderr
st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", o)]
en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", o)]
fala, prev = [], 0.0
for s, e in zip(st, en):
    if s > prev: fala.append([prev, s])
    prev = e
fala.append([prev, FIM])
seg = []
for a, b in fala:
    a, b = max(a - PRE, INI_FALA), min(b + POS, FIM)
    if b - a < 0.12: continue
    if seg and a - seg[-1][1] < 0.10: seg[-1][1] = b
    else: seg.append([a, b])
# trechos muito curtos (< 0,45 s) se fundem ao vizinho, mantendo a pausa curta entre eles
out = []
for a, b in seg:
    if out and (b - a < 0.45 or out[-1][1] - out[-1][0] < 0.45) and a - out[-1][1] < 0.45: out[-1][1] = b
    else: out.append([a, b])
out = [[round(a, 3), round(b, 3)] for a, b in out]
tot = sum(b - a for a, b in out)
json.dump(out, open("tools/cortes.json", "w"))
for a, b in out: print(f"{a:7.2f} {b:7.2f} {b-a:5.2f}")
print("trechos", len(out), "fala total", round(tot, 2), "s  (bruto", FIM - INI_FALA, "s)")
