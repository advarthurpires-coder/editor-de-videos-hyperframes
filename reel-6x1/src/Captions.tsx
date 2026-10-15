import { buildBlocks, keyWordIdx } from "./captionBlocks";
import { T } from "./timeline";
import { C, clamp, easeOutCubic, ramp, WORDS } from "./util";
import { SANS } from "./ui";

const BLOCKS = buildBlocks(WORDS);
const KEYS = keyWordIdx(WORDS);

// Quando um título grande já mostra a mesma informação, a legenda baixa a opacidade (sem sumir).
const DIM: [number, number][] = [
  [T.n75 + 0.65, T.emenda],
  [T.h44, T.salario],
  [T.comente6x1, T.checklist],
];

export const Captions = ({ t }: { t: number }) => {
  const b = BLOCKS.find((x) => t >= x.start - 0.05 && t < x.end);
  if (!b) return null;
  const k = ramp(t, b.start - 0.05, b.start + 0.1, easeOutCubic);
  const dim = DIM.some(([a, z]) => t >= a && t < z) ? 0.72 : 1;
  // palavra falada agora
  let current = -1;
  for (const i of b.idx) if (WORDS[i].start <= t + 0.02) current = i;
  return (
    <div style={{ position: "absolute", left: 90, right: 90, top: 1290, transform: "translateY(-50%)", display: "flex", justifyContent: "center" }}>
      <div
        style={{
          maxWidth: 900,
          padding: "16px 30px 18px",
          borderRadius: 22,
          background: "rgba(13,31,60,0.55)",
          boxShadow: "0 10px 30px rgba(3,8,20,0.25)",
          textAlign: "center",
          fontFamily: SANS,
          fontWeight: 600,
          fontSize: 50,
          lineHeight: 1.2,
          color: C.white,
          opacity: clamp(k) * dim,
          transform: `translateY(${(1 - k) * 10}px) scale(${0.97 + 0.03 * k})`,
          textShadow: "0 2px 10px rgba(3,8,20,0.6)",
        }}
      >
        {b.idx.map((i, n) => {
          const on = i === current;
          const gold = on || KEYS.has(i);
          return (
            <span key={i} style={{ color: gold ? (on ? "#E2C88F" : C.gold) : C.white, transition: "none" }}>
              {WORDS[i].word}
              {n < b.idx.length - 1 ? " " : ""}
            </span>
          );
        })}
      </div>
    </div>
  );
};
