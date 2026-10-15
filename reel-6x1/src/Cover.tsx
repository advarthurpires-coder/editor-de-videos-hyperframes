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
          <div style={{ position: "absolute", left: 0, right: 0, top: 360, textAlign: "center" }}>
            <Img src={staticFile("simbolo_dourado.png")} style={{ width: 92, opacity: 0.95 }} />
            <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 24, letterSpacing: "0.3em", color: C.gold, marginTop: 26 }}>ATUALIZADO EM 15/10/2026</div>
            <div style={{ fontFamily: SERIF, fontWeight: 700, fontSize: 168, lineHeight: 1, color: C.white, marginTop: 34, fontVariantNumeric: "lining-nums", textShadow: "0 10px 40px rgba(3,8,20,0.7)" }}>
              FIM DA 6x1:
            </div>
            <div style={{ fontFamily: SERIF, fontWeight: 700, fontSize: 92, lineHeight: 1.05, color: C.white, marginTop: 14, textShadow: "0 10px 40px rgba(3,8,20,0.7)" }}>
              o que muda e <span style={{ ...GOLD_TEXT, filter: "drop-shadow(0 8px 24px rgba(3,8,20,0.7))" }}>QUANDO</span>
            </div>
            <div style={{ width: 300, height: 3, background: C.gold, margin: "34px auto 0" }} />
          </div>
        </>
      )}
    </AbsoluteFill>
  );
};
