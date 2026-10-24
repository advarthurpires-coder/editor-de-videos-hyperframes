"""Prepara a mídia do reel: recorta os trechos escolhidos, amplia para 1080x1920 e aplica a mesma cor em tudo.

Os vídeos chegaram em 464x832 (WhatsApp): ampliação lanczos + redução leve de ruído + nitidez suave.
Cada trecho sai com 0,8 s de folga (a transição começa 0,3 s antes do corte e termina 0,5 s depois).

Uso: python3 -I tools/preparar_midia.py
"""
import os
import subprocess

D = os.path.dirname(os.path.abspath(__file__)) + "/.."
ORIG = f"{D}/originais"
FOLGA = 0.8
COR = "eq=contrast=1.05:saturation=1.10:gamma=1.02,colortemperature=temperature=5600:mix=0.35"

# (id, arquivo de origem, ponto de entrada em s, duração do plano em s) — tempos do index.html
CLIPES = [
    ("c01", "video-21.mov", 0.3, 3.34),   # mesa posta (travelling) — abertura
    ("c02", "video-20.mp4", 0.5, 1.67),   # brasas e carne
    ("c03", "video-18.mp4", 1.0, 1.67),   # churrasqueiro
    ("c04", "video-17.mp4", 0.4, 1.67),   # detalhe das taças
    ("c06", "video-08.mov", 0.6, 1.67),   # chegada: sorrisos
    ("c07", "video-12.mp4", 1.4, 1.67),   # casal à mesa
    ("c09", "video-11.mov", 0.9, 1.67),   # a Palavra
    ("c10", "video-13.mp4", 8.6, 1.67),
    ("c12", "video-10.mov", 2.0, 1.67),   # ouvintes
    ("c13", "video-07.mov", 7.2, 1.67),
    ("c15", "video-06.mp4", 0.2, 1.67),   # drop: servindo a carne
    ("c16", "video-03.mp4", 2.0, 1.67),
    ("c19", "video-05.mp4", 3.0, 1.67),
    ("c20", "video-01.mov", 0.4, 1.67),
]
FOTOS = ["foto-02", "foto-04", "foto-06", "foto-07", "foto-08", "foto-11", "foto-13", "foto-14",
         "foto-15", "foto-18", "foto-19", "foto-20", "foto-21"]


def run(args):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"] + args, check=True)


def main():
    os.makedirs(f"{D}/assets/media/clips", exist_ok=True)
    os.makedirs(f"{D}/assets/media/fotos", exist_ok=True)
    for cid, src, ini, dur in CLIPES:
        vf = ("scale=1080:-2:flags=lanczos,crop=1080:1920,hqdn3d=1.5:1.5:6:6,unsharp=5:5:0.55:5:5:0," + COR +
              ",fps=30,format=yuv420p")
        run(["-ss", f"{max(0, ini - 0.3):.2f}", "-i", f"{ORIG}/videos/{src}", "-t", f"{dur + FOLGA:.2f}", "-an",
             "-vf", vf, "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-g", "15", "-movflags", "+faststart",
             f"{D}/assets/media/clips/{cid}.mp4"])
        print(cid, src)
    for f in FOTOS:
        run(["-i", f"{ORIG}/fotos/{f}.jpg", "-vf", "scale=-2:1920:flags=lanczos,unsharp=5:5:0.4:5:5:0," + COR,
             "-q:v", "2", f"{D}/assets/media/fotos/{f}.jpg"])
    print("fotos ok:", len(FOTOS))


if __name__ == "__main__":
    main()
