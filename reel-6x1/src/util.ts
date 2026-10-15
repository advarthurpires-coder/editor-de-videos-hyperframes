import words from "./data/words.json";

export const FPS = 30;
export const W = 1080;
export const H = 1920;
export const VOICE_END = 87.95;
// narração + 0,8 s de assinatura
export const TOTAL_SEC = VOICE_END + 0.8;
export const TOTAL_FRAMES = Math.round(TOTAL_SEC * FPS);

export type Word = { start: number; end: number; word: string };
export const WORDS = words as Word[];

// Antecipação padrão: a animação começa 3 quadros antes da palavra.
export const LEAD = 3 / FPS;

export const C = {
  navy: "#0D1F3C",
  navyDeep: "#0C1B33",
  gold: "#B8975A",
  goldLight: "#D9BE86",
  offWhite: "#F7F5F0",
  white: "#FFFFFF",
};

export const clamp = (v: number, a = 0, b = 1) => Math.min(b, Math.max(a, v));
export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

export const easeOutCubic = (t: number) => 1 - Math.pow(1 - t, 3);
export const easeInCubic = (t: number) => t * t * t;
export const easeInOutCubic = (t: number) =>
  t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
export const easeOutBack = (t: number, s = 1.70158) => {
  const c3 = s + 1;
  return 1 + c3 * Math.pow(t - 1, 3) + s * Math.pow(t - 1, 2);
};
export const easeOutExpo = (t: number) => (t >= 1 ? 1 : 1 - Math.pow(2, -10 * t));

/** 0→1 entre a e b (segundos), com easing. */
export const ramp = (t: number, a: number, b: number, ease: (x: number) => number = easeInOutCubic) =>
  ease(clamp((t - a) / (b - a)));

/** Janela de visibilidade com entrada/saída: 0 fora, 1 dentro. */
export const win = (t: number, a: number, b: number, fadeIn = 0.25, fadeOut = 0.25) =>
  Math.min(ramp(t, a, a + fadeIn, easeOutCubic), 1 - ramp(t, b - fadeOut, b, easeInCubic));

/** Mola amortecida simples (pop com leve overshoot), 0→1. */
export const pop = (t: number, start: number, dur = 0.45) => {
  const x = clamp((t - start) / dur);
  if (x <= 0) return 0;
  if (x >= 1) return 1;
  return 1 - Math.exp(-6 * x) * Math.cos(x * 9.5);
};

/** Pseudoaleatório determinístico. */
export const rand = (i: number) => {
  const x = Math.sin(i * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
};

/** Tremor de câmera que decai depois de um impacto. */
export const shake = (t: number, at: number, amp = 1, dur = 0.45) => {
  const d = t - at;
  if (d < 0 || d > dur) return 0;
  const k = 1 - d / dur;
  return Math.sin(d * 70) * amp * k * k;
};

/** Início da n-ésima ocorrência de uma palavra (normalizada) no JSON. */
export const wordAt = (needle: string, nth = 1, after = 0) => {
  let n = 0;
  for (const w of WORDS) {
    const norm = w.word.toLowerCase().replace(/[.,?!]/g, "");
    if (w.start >= after && norm === needle.toLowerCase()) {
      n++;
      if (n === nth) return w.start;
    }
  }
  throw new Error(`Palavra não encontrada: ${needle}`);
};
