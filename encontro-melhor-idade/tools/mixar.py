# Mixagem: trilha de louvor + poucos efeitos suaves (brilho no título e no final, sopro nas polaroides).
# Uso: python3 -I tools/mixar.py && bash tools/masterizar.sh
import os
import subprocess

D = os.path.dirname(os.path.abspath(__file__)) + "/.."
B = 60 / 72
BAR = 4 * B
DUR = 49.0
R = 11 * BAR
SFX = [  # (tempo s, arquivo, ganho dB)
    (0.25, "sparkle.mp3", -17),
    (R + 0.10, "whoosh.mp3", -22), (R + 0.10 + 2 * B, "whoosh.mp3", -22),
    (R + 0.10 + 4 * B, "whoosh.mp3", -22), (R + 0.10 + 6 * B, "whoosh.mp3", -22),
    (13 * BAR + 3.5 * B + 0.85, "sparkle.mp3", -15),
]
args = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", f"{D}/assets/music/trilha_louvor.wav"]
for _, f, _ in SFX:
    args += ["-i", f"{D}/assets/sfx/{f}"]
fc = ["[0]aformat=sample_rates=48000:channel_layouts=stereo[mus]"]
mix = ["[mus]"]
for i, (t, f, g) in enumerate(SFX):
    ms = int(t * 1000)
    fc.append(f"[{i+1}]aformat=sample_rates=48000:channel_layouts=stereo,volume={g}dB,adelay={ms}|{ms}[s{i}]")
    mix.append(f"[s{i}]")
fc.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0:duration=first,atrim=0:{DUR}[out]")
args += ["-filter_complex", ";".join(fc), "-map", "[out]", "-ar", "48000", "-c:a", "pcm_s16le", f"{D}/assets/media/mix_pre.wav"]
subprocess.run(args, check=True)
print("mix_pre ok")
