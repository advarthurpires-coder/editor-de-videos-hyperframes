import { Img, staticFile } from "remotion";
import { CHAPTERS, T } from "./timeline";
import { C, clamp, ramp } from "./util";
import { SANS } from "./ui";

export const Hud = ({ t }: { t: number }) => {
  const endFade = 1 - ramp(t, T.finale + 0.5, T.finale + 0.9);
  const cur = CHAPTERS.find((c) => t >= c.from && t < c.to);
  const label = cur ? `${cur.n} · ${cur.label}` : t < CHAPTERS[0].from ? "FIM DA ESCALA 6x1" : "SÉRIE 6x1";
  // troca de rótulo com fade curto
  const edges = [CHAPTERS[0].from, ...CHAPTERS.map((c) => c.to)];
  const near = Math.min(...edges.map((e) => Math.abs(t - e)));
  const labelOp = clamp(near / 0.2);
  return (
    <>
      {/* gradientes de leitura */}
      <div style={{ position: "absolute", inset: 0, background: "linear-gradient(180deg, rgba(10,22,42,0.78) 0%, rgba(10,22,42,0) 16%, rgba(10,22,42,0) 58%, rgba(10,22,42,0.55) 82%, rgba(10,22,42,0.7) 100%)" }} />
      <div style={{ position: "absolute", inset: 0, background: "radial-gradient(130% 80% at 50% 45%, rgba(0,0,0,0) 55%, rgba(6,14,30,0.55) 100%)" }} />
      <div style={{ opacity: endFade }}>
        {/* barra de capítulos */}
        <div style={{ position: "absolute", left: 90, width: 900, top: 158, display: "flex", gap: 12 }}>
          {CHAPTERS.map((c) => {
            const p = clamp((t - c.from) / (c.to - c.from));
            return (
              <div key={c.n} style={{ flex: 1, height: 5, borderRadius: 3, background: "rgba(255,255,255,0.18)", overflow: "hidden" }}>
                <div style={{ width: `${p * 100}%`, height: "100%", background: C.gold, boxShadow: "0 0 10px rgba(184,151,90,0.8)" }} />
              </div>
            );
          })}
        </div>
        <div style={{ position: "absolute", left: 90, top: 180, fontFamily: SANS, fontWeight: 600, fontSize: 19, letterSpacing: "0.2em", color: C.gold, opacity: labelOp }}>
          {label}
        </div>
        {/* selo de canto */}
        <Img src={staticFile("simbolo_dourado.png")} style={{ position: "absolute", right: 90, top: 70, width: 64, height: 64, opacity: 0.85 }} />
      </div>
      {/* rodapé */}
      <div style={{ position: "absolute", left: 0, right: 0, top: 1490, textAlign: "center", fontFamily: SANS, fontWeight: 500, fontSize: 18, letterSpacing: "0.2em", color: C.white, opacity: 0.6 }}>
        INFORMAÇÃO DE 15/10/2026 · SUJEITA A ATUALIZAÇÃO
      </div>
    </>
  );
};
