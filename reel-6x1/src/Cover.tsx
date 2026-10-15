import { ThreeCanvas } from "@remotion/three";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { useFonts } from "./Main";
import { GOLD_TEXT, SANS, SERIF } from "./ui";
import { C, H, W } from "./util";
import { World } from "./World";

// Capa 1080×1920; todo o texto dentro do miolo 1080×1350 (y 285–1635).
export const Cover = () => {
  const ready = useFonts();
  return (
    <AbsoluteFill style={{ background: C.navyDeep }}>
      {ready && (
        <>
          <ThreeCanvas width={W} height={H} shadows gl={{ antialias: true, preserveDrawingBuffer: true }}>
            <World cover />
          </ThreeCanvas>
          <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(10,22,42,0.9) 0%, rgba(10,22,42,0.35) 45%, rgba(10,22,42,0) 58%, rgba(10,22,42,0.55) 80%, rgba(10,22,42,0.95) 100%)" }} />
          <AbsoluteFill style={{ background: "radial-gradient(120% 70% at 50% 55%, rgba(0,0,0,0) 50%, rgba(6,14,30,0.6) 100%)" }} />
          {/* brilho dourado atrás do advogado */}
          <div style={{ position: "absolute", left: 470 - 520, top: 640, width: 1040, height: 1040, background: "radial-gradient(closest-side, rgba(184,151,90,0.32), rgba(184,151,90,0.08) 60%, rgba(184,151,90,0) 100%)" }} />
          <Img
            src={staticFile("arthur_recorte.png")}
            style={{
              position: "absolute",
              left: 470 - 376,
              top: 690,
              width: 752,
              filter: "drop-shadow(0 0 2px rgba(232,208,154,0.55)) drop-shadow(0 0 26px rgba(184,151,90,0.35)) drop-shadow(0 30px 40px rgba(3,8,20,0.6))",
            }}
          />
          <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(10,22,42,0) 80%, rgba(10,22,42,0.85) 100%)" }} />
          <div style={{ position: "absolute", left: 0, right: 0, top: 305, textAlign: "center" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 18 }}>
              <Img src={staticFile("simbolo_dourado.png")} style={{ width: 50, opacity: 0.95 }} />
              <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 22, letterSpacing: "0.3em", color: C.gold }}>ATUALIZADO EM 15/10/2026</div>
            </div>
            <div style={{ fontFamily: SERIF, fontWeight: 700, fontSize: 158, lineHeight: 1, color: C.white, marginTop: 22, fontVariantNumeric: "lining-nums", textShadow: "0 10px 40px rgba(3,8,20,0.7)" }}>
              FIM DA 6x1:
            </div>
            <div style={{ fontFamily: SERIF, fontWeight: 700, fontSize: 88, lineHeight: 1.05, color: C.white, marginTop: 8, textShadow: "0 10px 40px rgba(3,8,20,0.7)" }}>
              o que muda e <span style={{ ...GOLD_TEXT, filter: "drop-shadow(0 8px 24px rgba(3,8,20,0.7))" }}>QUANDO</span>
            </div>
          </div>
        </>
      )}
    </AbsoluteFill>
  );
};
