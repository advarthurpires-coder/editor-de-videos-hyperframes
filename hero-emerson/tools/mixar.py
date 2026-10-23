# Mixagem: voz original + trilha (drop alinhado ao giro do flyer) + efeitos sonoros nos tempos da timeline.
# Uso: python3 -I tools/mixar.py && bash tools/masterizar.sh
import os, subprocess
D = os.path.dirname(os.path.abspath(__file__)) + "/.."
DUR = 24.5
SFX = [  # (tempo s, arquivo, ganho dB)
    (0.00, "whoosh.mp3", -9), (3.40, "whoosh.mp3", -12), (3.78, "click.mp3", -10),
    (5.62, "whoosh.mp3", -12), (6.30, "click-soft.mp3", -8), (7.90, "whoosh.mp3", -13), (8.38, "click.mp3", -10),
    (9.65, "whoosh.mp3", -16), (10.10, "whoosh.mp3", -13), (10.80, "sparkle.mp3", -14),
    (12.30, "pop.mp3", -9), (12.48, "click-soft.mp3", -10), (13.90, "whoosh.mp3", -16),
    (16.20, "sparkle.mp3", -17), (18.32, "impact-bass-1.mp3", -10),
    (19.20, "whoosh.mp3", -9), (19.62, "whoosh.mp3", -7), (20.30, "impact-bass-2.mp3", -6), (20.55, "sparkle.mp3", -12),
    (22.45, "click.mp3", -9),
]
args = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", f"{D}/assets/media/voz.wav", "-i", f"{D}/assets/music/trilha_convite_hero.wav"]
for _, f, _ in SFX:
    args += ["-i", f"{D}/assets/sfx/{f}"]
fc = [
    "[0]highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=3,apad=whole_dur=%s[voz]" % DUR,
    # trilha: atrasada 0,3 s (drop cai no giro), baixa sob a voz, sobe no flyer, some no fim
    "[1]adelay=300|300,atrim=0:%s,volume='if(lt(t,19.2),0.09,if(lt(t,20.0),0.09+(t-19.2)/0.8*0.41,0.5))':eval=frame,afade=t=out:st=23.3:d=1.2[mus]" % DUR,
]
mix = ["[voz]", "[mus]"]
for i, (t, f, g) in enumerate(SFX):
    ms = int(t * 1000)
    fc.append(f"[{i+2}]aformat=sample_rates=48000:channel_layouts=stereo,volume={g}dB,adelay={ms}|{ms}[s{i}]")
    mix.append(f"[s{i}]")
fc.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0:duration=longest,atrim=0:{DUR}[out]")
args += ["-filter_complex", ";".join(fc), "-map", "[out]", "-ar", "48000", "-c:a", "pcm_s16le", f"{D}/assets/media/mix_pre.wav"]
subprocess.run(args, check=True)
print("mix_pre ok")
