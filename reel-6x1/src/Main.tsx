import { ThreeCanvas } from "@remotion/three";
import { useEffect, useState } from "react";
import { AbsoluteFill, Audio, continueRender, delayRender, staticFile, useCurrentFrame } from "remotion";
import { Captions } from "./Captions";
import { Hud } from "./Hud";
import { Scenes } from "./Scenes";
import { T } from "./timeline";
import { C, FPS, H, ramp, W } from "./util";
import { World } from "./World";

const FONTS: [string, number, string][] = [
  ["Outfit", 400, "outfit-latin-400-normal.woff2"],
  ["Outfit", 500, "outfit-latin-500-normal.woff2"],
  ["Outfit", 600, "outfit-latin-600-normal.woff2"],
  ["Outfit", 700, "outfit-latin-700-normal.woff2"],
  ["Cormorant Garamond", 500, "cormorant-garamond-latin-500-normal.woff2"],
  ["Cormorant Garamond", 600, "cormorant-garamond-latin-600-normal.woff2"],
  ["Cormorant Garamond", 700, "cormorant-garamond-latin-700-normal.woff2"],
];

export const useFonts = () => {
  const [ready, setReady] = useState(false);
  const [handle] = useState(() => delayRender("fontes"));
  useEffect(() => {
    Promise.all(
      FONTS.map(([fam, w, file]) => {
        const f = new FontFace(fam, `url(${staticFile(`fonts/${file}`)}) format('woff2')`, { weight: String(w) });
        (document.fonts as unknown as { add: (f: FontFace) => void }).add(f);
        return f.load();
      }),
    ).then(() => {
      setReady(true);
      continueRender(handle);
    });
  }, [handle]);
  return ready;
};

/** Desfoque leve nas transições de capítulo (profundidade de campo). */
const DOF: number[] = [5.5, 11.6, 24.2, 35.3, 43.3, 61.4, 74.5, 83.3];
const dofBlur = (t: number) => Math.max(0, ...DOF.map((d) => 4 * (1 - Math.abs(t - d) / 0.35)));

export type MainProps = { captions: boolean; audio: boolean };

export const Main = ({ captions, audio }: MainProps) => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const ready = useFonts();
  const flash40 = Math.max(0, 1 - Math.abs(t - (T.h40 + 0.15)) / 0.35);
  const whiteIn = ramp(t, T.finale + 0.75, T.finale + 0.95) * (1 - ramp(t, T.finale + 0.95, T.finale + 1.3));
  return (
    <AbsoluteFill style={{ background: C.navyDeep }}>
      {ready && (
        <>
          <AbsoluteFill style={{ filter: dofBlur(t) > 0.2 ? `blur(${dofBlur(t)}px)` : undefined }}>
            <ThreeCanvas width={W} height={H} shadows gl={{ antialias: true, preserveDrawingBuffer: true }}>
              <World />
            </ThreeCanvas>
          </AbsoluteFill>
          <AbsoluteFill style={{ background: `rgba(232,208,154,${flash40 * 0.18 + whiteIn * 0.35})`, mixBlendMode: "screen" }} />
          {/* fusão final: o 3D escurece enquanto o símbolo assume */}
          <AbsoluteFill style={{ background: C.navyDeep, opacity: 0.97 * ramp(t, T.finale + 0.8, T.finale + 1.15) }} />
          <Hud t={t} />
          <Scenes t={t} />
          {captions && <Captions t={t} />}
        </>
      )}
      {audio && <Audio src={staticFile("audio_6x1_limpo_versaoB.wav")} />}
    </AbsoluteFill>
  );
};

export const CaptionsOnly = () => {
  const frame = useCurrentFrame();
  const ready = useFonts();
  return <AbsoluteFill>{ready && <Captions t={frame / FPS} />}</AbsoluteFill>;
};
