// Agrupamento das legendas — função pura, usada pelo vídeo e pelo gerador do .srt.
export type CapWord = { start: number; end: number; word: string };
export type Block = { start: number; end: number; idx: number[] };

const MAX_WORDS = 6;
const MAX_CHARS = 38;

export const buildBlocks = (words: CapWord[]): Block[] => {
  const blocks: Block[] = [];
  let cur: number[] = [];
  const chars = (ids: number[]) => ids.map((i) => words[i].word).join(" ").length;
  words.forEach((w, i) => {
    cur.push(i);
    const next = words[i + 1];
    const punct = /[.,?!]$/.test(w.word);
    const gap = next ? next.start - w.end : 99;
    const tooLong = next ? chars([...cur, i + 1]) > MAX_CHARS : false;
    const close = !next || cur.length >= MAX_WORDS || tooLong || (cur.length >= 2 && (punct || gap > 0.45));
    if (close) {
      blocks.push({ start: words[cur[0]].start, end: 0, idx: cur });
      cur = [];
    }
  });
  blocks.forEach((b, k) => {
    const last = words[b.idx[b.idx.length - 1]];
    const nextStart = blocks[k + 1]?.start ?? last.end + 0.6;
    b.end = Math.min(last.end + 0.35, nextStart);
  });
  return blocks;
};

/** Índices de palavras-chave que ficam sempre em dourado. */
export const keyWordIdx = (words: CapWord[]): Set<number> => {
  const n = (i: number) => (words[i]?.word ?? "").toLowerCase().replace(/[.,?!]/g, "");
  const s = new Set<number>();
  words.forEach((_, i) => {
    const w = n(i);
    if (w === "6x1" || w === "domingo" || w === "44" || w === "42") s.add(i);
    if (w === "75" && n(i + 1) === "a" && n(i + 2) === "1") [i, i + 1, i + 2].forEach((k) => s.add(k));
    if (w === "40" && n(i + 1) === "horas") [i, i + 1].forEach((k) => s.add(k));
    if (w === "14" && n(i + 1) === "meses") [i, i + 1].forEach((k) => s.add(k));
    if (w === "r$" && n(i + 1) === "21" && n(i + 2) === "mil") [i, i + 1, i + 2].forEach((k) => s.add(k));
    if (w === "lei" && n(i + 1) === "complementar") [i, i + 1].forEach((k) => s.add(k));
  });
  return s;
};
