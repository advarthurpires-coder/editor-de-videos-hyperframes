"""Trilha instrumental original de louvor do reel "Noite da Melhor Idade" (síntese, sem samples de terceiros).

Ré maior, 72 bpm, 14 compassos + cauda (ver roteiro.py):
  c1–3   preparo   piano em arpejo e pad suave (D – Bm7 – Gmaj7)
  c4     chegada   entra o baixo (Asus4 -> A)
  c5–8   palavra   melodia no piano, bumbo "coração" nos tempos 1 e 3, swell no fim do c8
  c9–12  comunhão  refrão: pad aberto, bumbo nos 4 tempos, brilho na oitava de cima, prato no drop
  c13    rostos    G -> A, prepara a resolução
  c14    final     Ré com 9ª, sustentado até o fim

Uso: python3 -I tools/gerar_trilha.py assets/music/trilha_louvor.wav
Determinística (semente fixa).
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audio_util import fftconv, hp, lp, wav  # noqa: E402
from roteiro import BAR, BEAT, SR, TOTAL  # noqa: E402

N = int((TOTAL + 1) * SR)
DRY = np.zeros((N, 2))
WET = np.zeros((N, 2))      # vai para o reverb
rng = np.random.default_rng(20261023)


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def put(sig, t, gain=1.0, pan=0.0, rev=0.3):
    i = int(round(t * SR))
    if i >= N:
        return
    sig = sig[: N - i]
    lg, rg = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    st = np.stack([sig * lg, sig * rg], 1) * gain
    DRY[i: i + len(sig)] += st * (1 - rev)
    WET[i: i + len(sig)] += st * rev


# ------------------------------------------------------------------ instrumentos
def piano(m, vel=1.0, dur=3.2):
    t = np.arange(int(dur * SR)) / SR
    f = hz(m)
    out = np.zeros_like(t)
    for n in range(1, 11):
        fn = f * n * np.sqrt(1 + 0.0004 * n * n)          # leve inarmonicidade de corda
        if fn > 9000:
            break
        a = (1 / n ** 1.6) * (0.55 + 0.45 * vel)
        out += a * np.sin(2 * np.pi * fn * t + rng.uniform(0, 6.28)) * np.exp(-t * (0.7 + 0.45 * n) * (f / 300) ** 0.35)
    out += 0.004 * rng.standard_normal(len(t)) * np.exp(-t / 0.006)   # martelo
    env = np.minimum(1, t / 0.004) * np.minimum(1, (dur - t) / 0.3)
    return lp(out * env, 2400 + 3600 * vel) * 0.16 * vel


def pad(notes, dur, att=1.4, rel=1.8, bright=2600):
    ln = dur + rel
    t = np.arange(int(ln * SR)) / SR
    out = np.zeros_like(t)
    for m in notes:
        f = hz(m)
        for d in (-0.09, -0.03, 0.03, 0.09):
            fd = f * 2 ** (d / 12)
            ph = 2 * np.pi * fd * t + rng.uniform(0, 6.28)
            for n in range(1, max(2, int(min(16, bright / fd)))):
                out += np.sin(n * ph) / n ** 1.5
    env = np.minimum(1, t / att) * np.where(t < dur, 1.0, np.exp(-(t - dur) / (rel / 3)))
    return lp(out * env, bright * 0.7) * 0.010


def baixo(m, dur, vel=1.0):
    t = np.arange(int((dur + 0.4) * SR)) / SR
    f = hz(m)
    out = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t) + 0.08 * np.sin(6 * np.pi * f * t)
    env = np.minimum(1, t / 0.03) * np.where(t < dur, np.exp(-t * 0.25), np.exp(-dur * 0.25) * np.exp(-(t - dur) / 0.12))
    return out * env * 0.11 * vel


def bumbo(vel=1.0):
    t = np.arange(int(0.6 * SR)) / SR
    fr = 44 + 70 * np.exp(-t / 0.035)
    out = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t / 0.20)
    out += 0.12 * lp(rng.standard_normal(len(t)), 2500) * np.exp(-t / 0.008)
    return out * 0.42 * vel


def prato(dur=3.0, vel=1.0):
    t = np.arange(int(dur * SR)) / SR
    x = hp(rng.standard_normal(len(t)), 5000)
    return x * np.exp(-t / (dur / 3.5)) * np.minimum(1, t / 0.002) * 0.07 * vel


def swell(dur):
    """Prato ao contrário + ruído filtrado subindo (prepara o drop)."""
    t = np.arange(int(dur * SR)) / SR
    x = hp(rng.standard_normal(len(t)), 3500)
    return x * (t / dur) ** 2.6 * 0.10


def sino(m, vel=1.0):
    t = np.arange(int(2.5 * SR)) / SR
    f = hz(m)
    out = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 3)
    return out * np.exp(-t / 0.7) * np.minimum(1, t / 0.003) * 0.05 * vel


# ------------------------------------------------------------------ harmonia (Ré maior)
D3, E3, Fs3, G3, A3, B3 = 50, 52, 54, 55, 57, 59
C4s, D4, E4, Fs4, G4, A4, B4 = 61, 62, 64, 66, 67, 69, 71
C5s, D5, E5, Fs5, G5, A5, B5 = 73, 74, 76, 78, 79, 81, 83

# (baixo, notas do pad, notas do arpejo) por compasso
ACORDES = [
    (D3 - 12, [D4, Fs4, A4, E5], [D3, A3, E4, Fs4, A4, Fs4, E4, A3]),       # c1  Dadd9
    (B3 - 24, [D4, Fs4, A4, B3], [B3 - 12, Fs3, D4, A3, B3, D4, Fs4, D4]),   # c2  Bm7
    (G3 - 24, [D4, Fs4, B3, G4], [G3 - 12, D3, B3, Fs4, G4, Fs4, D4, B3]),   # c3  Gmaj7
    (A3 - 24, [D4, E4, A4, C5s], [A3 - 12, E3, A3, D4, E4, C5s - 12, E4, A3]),  # c4  Asus4 -> A
    (D3 - 12, [D4, Fs4, A4], [D3, A3, D4, Fs4, A4, Fs4, D4, A3]),            # c5  D
    (C4s - 24, [C4s, E4, A4], [C4s - 12, A3, C4s, E4, A4, E4, C4s, A3]),     # c6  A/C#
    (B3 - 24, [D4, Fs4, B3, A4], [B3 - 12, Fs3, B3, D4, Fs4, D4, B3, Fs3]),  # c7  Bm7
    (G3 - 24, [D4, G4, B3], [G3 - 12, D3, G3, B3, D4, A3, C4s - 12, E3]),    # c8  G -> A
    (D3 - 12, [D4, Fs4, A4, D5], [D3, A3, D4, Fs4, A4, Fs4, D4, A3]),        # c9  D (drop)
    (A3 - 24, [C4s, E4, A4, E5], [A3 - 12, E3, A3, C4s, E4, C4s, A3, E3]),   # c10 A
    (B3 - 24, [D4, Fs4, B4, Fs5 - 12], [B3 - 12, Fs3, B3, D4, Fs4, D4, B3, Fs3]),  # c11 Bm
    (G3 - 24, [D4, G4, B4, D5], [G3 - 12, D3, G3, B3, D4, B3, G3, D3]),      # c12 G
    (G3 - 24, [D4, G4, B4, E5], [G3 - 12, D3, G3, B3, A3, C4s, E4, A4]),     # c13 G -> A
    (D3 - 12, [D4, Fs4, A4, E5, A5], [D3, A3, D4, E4, Fs4, A4]),             # c14 Dadd9 final
]

# melodia: (compasso, tempo dentro do compasso, nota, duração em tempos)
MELODIA = [
    (4, 0, A4, 1), (4, 1, D5, 1), (4, 2, E5, 1), (4, 3, Fs5, 1),
    (5, 0, E5, 2), (5, 2, C5s, 1), (5, 3, A4, 1),
    (6, 0, D5, 1), (6, 1, C5s, 1), (6, 2, B4, 2),
    (7, 0, B4, 1), (7, 1, A4, 1), (7, 2, G4, 1), (7, 3, A4, 1),
    (8, 0, Fs5, 2), (8, 2, A5, 1), (8, 3, Fs5, 1),
    (9, 0, E5, 3), (9, 3, C5s, 1),
    (10, 0, D5, 1), (10, 1, E5, 1), (10, 2, Fs5, 1), (10, 3, D5, 1),
    (11, 0, B4, 2), (11, 2, D5, 2),
    (12, 0, E5, 2), (12, 2, C5s, 2),
    (13, 0, D5, 4),
]


def main(saida):
    for c, (b, padn, arp) in enumerate(ACORDES):
        t0 = c * BAR
        final = c == 13
        # pad: suave no início, aberto no refrão
        g = 0.7 if c < 4 else (0.9 if c < 8 else 1.25)
        if final:
            put(pad(padn, TOTAL - t0 - 1.2, att=0.6, rel=2.0), t0, g * 0.9, 0.0, 0.55)
        else:
            put(pad(padn, BAR, att=1.4 if c < 8 else 0.5, rel=1.6), t0 - (0.2 if c else 0), g, 0.0, 0.5)
        # arpejo de piano (colcheias); no final, só um arpejo lento que sobe
        passo = BEAT / 2 if not final else BEAT / 2.5
        for k, m in enumerate(arp):
            vel = 0.55 + 0.25 * (k % 4 == 0) + (0.12 if c >= 8 else 0)
            if c in (0, 1) and k % 2:          # abertura mais esparsa
                vel *= 0.8
            put(piano(m, vel), t0 + k * passo, 1.0, -0.25 + 0.5 * (k % 2), 0.35)
        if final:
            put(piano(D3 - 12, 1.0, 5.0), t0, 1.0, 0.0, 0.35)
        # baixo a partir do c4
        if c >= 3:
            if c >= 8 and not final:
                for k in range(4):
                    put(baixo(b, BEAT * 0.9, 0.85 + 0.15 * (k == 0)), t0 + k * BEAT, 1.0, 0.0, 0.08)
            else:
                put(baixo(b, (TOTAL - t0 - 1.0) if final else BAR * 0.97), t0, 1.0, 0.0, 0.08)
        # bumbo: "coração" (1 e 3) na palavra, os 4 tempos no refrão
        if 4 <= c < 8:
            for k in (0, 2):
                put(bumbo(0.75), t0 + k * BEAT, 1.0, 0.0, 0.1)
        elif 8 <= c < 13:
            for k in range(4):
                put(bumbo(0.95 if k in (0, 2) else 0.7), t0 + k * BEAT, 1.0, 0.0, 0.1)
            # brilho: sinos na oitava de cima, contratempo
            for k in range(4):
                put(sino(padn[-1] + 12, 0.8), t0 + k * BEAT + BEAT / 2, 1.0, 0.6 if k % 2 else -0.6, 0.7)
        if c in (3, 7):                        # transições para a palavra e para o refrão
            put(swell(BAR / 2 if c == 3 else BAR), t0 + (BAR / 2 if c == 3 else 0), 1.0 if c == 7 else 0.6, 0.0, 0.3)
        if c in (4, 8, 13):
            put(prato(3.5 if c == 8 else 2.5, 0.8 if c == 8 else 0.45), t0, 1.0, 0.0, 0.5)

    for c, k, m, d in MELODIA:
        put(piano(m + 12 * 0, 0.95, max(1.6, d * BEAT + 1.2)), c * BAR + k * BEAT, 0.95, 0.15, 0.4)
        if c >= 8:                             # refrão: dobra uma oitava acima, mais baixa
            put(piano(m + 12, 0.6, max(1.4, d * BEAT + 1.0)), c * BAR + k * BEAT, 0.45, -0.15, 0.55)

    # reverb de salão: ruído decorrelacionado com decaimento exponencial (2,8 s)
    lir = int(3.6 * SR)
    t = np.arange(lir) / SR
    ir = np.zeros((lir, 2))
    for ch in range(2):
        x = rng.standard_normal(lir) * np.exp(-t / 0.62)
        x[: int(0.022 * SR)] = 0                  # pré-atraso
        ir[:, ch] = lp(x, 6500 if ch else 6000)
    ir /= np.sqrt((ir ** 2).sum(0, keepdims=True))
    wet = np.stack([hp(WET[:, ch], 220) for ch in range(2)], 1)     # reverb sem graves (não embola)
    rev = np.stack([fftconv(wet[:, ch], ir[:, ch])[:N] for ch in range(2)], 1)
    mix = DRY + rev * 0.9
    mix = np.stack([hp(mix[:, ch], 35) for ch in range(2)], 1)
    # fade-out final
    fo = int((TOTAL - 2.0) * SR)
    mix[fo:] *= np.linspace(1, 0, N - fo)[:, None] ** 1.5
    mix = mix[: int(TOTAL * SR)]
    mix *= 0.89 / np.abs(mix).max()
    wav(saida, mix)
    print("trilha ok:", saida, f"{len(mix) / SR:.2f} s")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "assets/music/trilha_louvor.wav")
