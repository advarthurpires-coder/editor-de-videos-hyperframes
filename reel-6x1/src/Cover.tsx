import { ThreeCanvas } from "@remotion/three";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { useFonts } from "./Main";
import { GOLD_TEXT, SANS, SERIF } from "./ui";
import { C, H, W } from "./util";
import { World } from "./World";

// Capa no padrão do perfil: advogado em destaque, logo empilhado no canto superior direito,
// linha de identificação no topo e título serifado em caixa translúcida na altura do peito.
// Todo o texto essencial fica dentro do miolo 1080×1350 (y 285–1635).
const WHITE_LOGO = "brightness(0) invert(1)";

export const Cover = () => {
  const ready = useFonts();
  return (
    <AbsoluteFill style={{ background: C.navyDeep }}>
      {ready && (
        <>
          {/* cenário 3D desfocado (profundidade de campo, como nas fotos) */}
          <AbsoluteFill style={{ filter: "blur(5px)", transform: "scale(1.03)" }}>
            <ThreeCanvas width={W} height={H} shadows gl={{ antialias: true, preserveDrawingBuffer: true }}>
              <World cover />
            </ThreeCanvas>
          </AbsoluteFill>
          <AbsoluteFill style={{ background: "radial-gradient(90% 60% at 50% 40%, rgba(10,22,42,0.15) 0%, rgba(8,18,36,0.75) 100%)" }} />
          <div style={{ position: "absolute", left: 540 - 520, top: 300, width: 1040, height: 1040, background: "radial-gradient(closest-side, rgba(184,151,90,0.28), rgba(184,151,90,0.06) 60%, rgba(184,151,90,0) 100%)" }} />
          {/* advogado */}
          <Img
            src={staticFile("arthur_recorte.png")}
            style={{
              position: "absolute",
              left: 540 - 500,
              top: 380,
              width: 1000,
              filter: "drop-shadow(0 0 2px rgba(232,208,154,0.45)) drop-shadow(0 0 30px rgba(184,151,90,0.3)) drop-shadow(0 30px 50px rgba(3,8,20,0.6))",
            }}
          />
          <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(8,18,36,0.55) 0%, rgba(8,18,36,0) 14%, rgba(8,18,36,0) 55%, rgba(8,18,36,0.55) 78%, rgba(8,18,36,0.92) 100%)" }} />
          {/* linha de identificação no topo */}
          <div style={{ position: "absolute", left: 60, right: 60, top: 140, display: "flex", justifyContent: "space-between", fontFamily: SANS, fontWeight: 500, fontSize: 17, letterSpacing: "0.22em", color: "rgba(255,255,255,0.75)" }}>
            <span>@adv.arthurpiresnascimento</span>
            <span>www.advarthurpires.com.br</span>
          </div>
          {/* logo empilhado (branco), canto superior direito */}
          <div style={{ position: "absolute", right: 70, top: 330, display: "flex", alignItems: "center", gap: 14 }}>
            <Img src={staticFile("simbolo_dourado.png")} style={{ width: 74, filter: WHITE_LOGO }} />
            <div>
              <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 21, lineHeight: 1.08, letterSpacing: "0.06em", color: C.white }}>
                ARTHUR
                <br />
                PIRES
                <br />
                NASCIMENTO
              </div>
              <div style={{ height: 1.5, background: C.gold, margin: "5px 0 4px" }} />
              <div style={{ fontFamily: SANS, fontWeight: 400, fontSize: 8.5, letterSpacing: "0.24em", color: C.white }}>ADVOCACIA ESPECIALIZADA</div>
            </div>
          </div>
          {/* título em caixa translúcida */}
          <div style={{ position: "absolute", left: 0, right: 0, top: 1150, display: "flex", justifyContent: "center" }}>
            <div
              style={{
                padding: "34px 54px 36px",
                borderRadius: 28,
                background: "rgba(13,31,60,0.62)",
                border: "1.5px solid rgba(255,255,255,0.14)",
                boxShadow: "0 30px 60px rgba(3,8,20,0.45)",
                textAlign: "center",
              }}
            >
              <div style={{ fontFamily: SERIF, fontWeight: 700, fontSize: 150, lineHeight: 0.95, color: C.white, fontVariantNumeric: "lining-nums" }}>FIM DA 6x1:</div>
              <div style={{ fontFamily: SERIF, fontWeight: 600, fontSize: 80, lineHeight: 1.1, color: C.white, marginTop: 6 }}>
                o que muda e <span style={GOLD_TEXT}>QUANDO</span>
              </div>
              <div style={{ fontFamily: SANS, fontWeight: 500, fontSize: 20, letterSpacing: "0.3em", color: C.gold, marginTop: 14 }}>ATUALIZADO EM 15/10/2026</div>
            </div>
          </div>
        </>
      )}
    </AbsoluteFill>
  );
};
