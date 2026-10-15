import React from "react";
import { C, clamp, easeInCubic, easeOutCubic, ramp } from "./util";

export const SERIF = "'Cormorant Garamond', serif";
export const SANS = "'Outfit', sans-serif";

export const GOLD_TEXT: React.CSSProperties = {
  background: "linear-gradient(180deg, #E8D09A 0%, #B8975A 55%, #9A7A43 100%)",
  WebkitBackgroundClip: "text",
  backgroundClip: "text",
  color: "transparent",
};

/** Bloco centralizado em y com entrada/saída cinematográfica. */
export const Appear: React.FC<{
  t: number;
  a: number;
  b: number;
  y: number;
  x?: number;
  dy?: number;
  inDur?: number;
  outDur?: number;
  scaleFrom?: number;
  blur?: number;
  exit?: "up" | "fade" | "back";
  plate?: boolean;
  style?: React.CSSProperties;
  children: React.ReactNode;
}> = ({ t, a, b, y, x = 540, dy = 40, inDur = 0.4, outDur = 0.3, scaleFrom = 0.94, blur = 10, exit = "up", plate = true, style, children }) => {
  if (t < a || t > b) return null;
  const i = ramp(t, a, a + inDur, easeOutCubic);
  const o = ramp(t, b - outDur, b, easeInCubic);
  const op = Math.min(i, 1 - o);
  const ty = (1 - i) * dy + (exit === "up" ? -o * dy : 0);
  const sc = (scaleFrom + (1 - scaleFrom) * i) * (exit === "back" ? 1 - o * 0.25 : 1);
  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        transform: `translate(-50%, -50%) translateY(${ty}px) scale(${sc})`,
        opacity: op,
        filter: blur ? `blur(${(1 - i) * blur + o * blur * 0.6}px)` : undefined,
        whiteSpace: "nowrap",
        textAlign: "center",
        ...style,
      }}
    >
      {plate && (
        <div
          style={{
            position: "absolute",
            inset: "-60px -90px",
            zIndex: -1,
            background: "radial-gradient(closest-side, rgba(8,18,36,0.72) 0%, rgba(8,18,36,0.5) 55%, rgba(8,18,36,0) 100%)",
          }}
        />
      )}
      {children}
    </div>
  );
};

export const Serif: React.FC<{ size: number; gold?: boolean; weight?: number; style?: React.CSSProperties; children: React.ReactNode }> = ({
  size,
  gold,
  weight = 700,
  style,
  children,
}) => (
  <div
    style={{
      fontFamily: SERIF,
      fontWeight: weight,
      fontSize: size,
      lineHeight: 0.95,
      color: C.white,
      letterSpacing: "0.01em",
      fontVariantNumeric: "lining-nums",
      fontFeatureSettings: '"lnum" 1',
      textShadow: gold ? undefined : "0 6px 30px rgba(5,12,28,0.65)",
      filter: gold ? "drop-shadow(0 6px 22px rgba(5,12,28,0.6))" : undefined,
      ...(gold ? GOLD_TEXT : {}),
      ...style,
    }}
  >
    {children}
  </div>
);

export const Micro: React.FC<{ size?: number; color?: string; spacing?: number; weight?: number; style?: React.CSSProperties; children: React.ReactNode }> = ({
  size = 30,
  color = C.white,
  spacing = 0.2,
  weight = 600,
  style,
  children,
}) => (
  <div
    style={{
      fontFamily: SANS,
      fontWeight: weight,
      fontSize: size,
      letterSpacing: `${spacing}em`,
      textTransform: "uppercase",
      color,
      textShadow: "0 3px 16px rgba(5,12,28,0.7)",
      ...style,
    }}
  >
    {children}
  </div>
);

/** Etiqueta/pílula. */
export const Tag: React.FC<{ filled?: boolean; size?: number; style?: React.CSSProperties; children: React.ReactNode }> = ({ filled, size = 34, style, children }) => (
  <div
    style={{
      display: "inline-block",
      fontFamily: SANS,
      fontWeight: 600,
      fontSize: size,
      letterSpacing: "0.16em",
      padding: `${size * 0.42}px ${size * 0.9}px`,
      borderRadius: 999,
      border: `2.5px solid ${C.gold}`,
      color: filled ? C.navy : C.gold,
      background: filled ? "linear-gradient(180deg,#DCC08A,#B8975A 60%,#A0803F)" : "rgba(12,27,51,0.72)",
      boxShadow: filled ? "0 14px 40px rgba(184,151,90,0.35)" : "0 12px 36px rgba(5,12,28,0.55)",
      ...style,
    }}
  >
    {children}
  </div>
);

/** Superfície de mármore / papel para cartões em CSS 3D. */
export const MARBLE_BG =
  "radial-gradient(120% 90% at 20% 10%, #FFFFFF 0%, #F7F5F0 45%, #ECE7DC 100%)";

export const Card3D: React.FC<{
  w: number;
  h?: number;
  rx?: number;
  ry?: number;
  rz?: number;
  z?: number;
  style?: React.CSSProperties;
  children: React.ReactNode;
}> = ({ w, h, rx = 0, ry = 0, rz = 0, z = 0, style, children }) => (
  <div style={{ perspective: 1500, perspectiveOrigin: "50% 40%" }}>
    <div
      style={{
        width: w,
        height: h,
        transform: `translateZ(${z}px) rotateX(${rx}deg) rotateY(${ry}deg) rotateZ(${rz}deg)`,
        transformStyle: "preserve-3d",
        background: MARBLE_BG,
        borderRadius: 26,
        border: `3px solid ${C.gold}`,
        boxShadow: "0 40px 80px rgba(3,8,20,0.65), 0 10px 24px rgba(3,8,20,0.45), inset 0 0 0 10px rgba(184,151,90,0.12)",
        color: C.navy,
        overflow: "hidden",
        position: "relative",
        ...style,
      }}
    >
      {children}
    </div>
  </div>
);

/** Contador mecânico: cada dígito rola verticalmente. */
export const Roller: React.FC<{ value: number; digits: number; size: number; gold?: boolean }> = ({ value, digits, size, gold }) => {
  const cols = [];
  for (let d = digits - 1; d >= 0; d--) {
    const place = Math.pow(10, d);
    // posição contínua do dígito, com "vai um" suave como num contador mecânico
    const lower = value % place;
    const pos = d === 0 ? value % 10 : (Math.floor(value / place) % 10) + Math.max(0, lower - (place - 1));
    cols.push(
      <div key={d} style={{ height: size, overflow: "hidden", width: size * 0.52 }}>
        <div style={{ transform: `translateY(${-pos * size}px)` }}>
          {Array.from({ length: 11 }).map((_, n) => (
            <div key={n} style={{ height: size, lineHeight: `${size}px`, fontFamily: SERIF, fontWeight: 700, fontSize: size, fontVariantNumeric: "lining-nums", fontFeatureSettings: '"lnum" 1', ...(gold ? GOLD_TEXT : { color: C.white }) }}>
              {n % 10}
            </div>
          ))}
        </div>
      </div>,
    );
  }
  return <div style={{ display: "flex", justifyContent: "center" }}>{cols}</div>;
};

/** Marca de carimbo dourada. */
export const StampMark: React.FC<{ t: number; hit: number; size?: number; children: React.ReactNode; rot?: number }> = ({ t, hit, size = 70, children, rot = -6 }) => {
  if (t < hit) return null;
  const k = ramp(t, hit, hit + 0.22, easeOutCubic);
  const sc = 1.3 - 0.3 * k;
  return (
    <div
      style={{
        transform: `rotate(${rot}deg) scale(${sc})`,
        opacity: clamp(k * 2),
        whiteSpace: "nowrap",
        border: `${size * 0.09}px solid ${C.gold}`,
        outline: `${size * 0.03}px solid rgba(184,151,90,0.7)`,
        outlineOffset: size * 0.08,
        borderRadius: size * 0.22,
        padding: `${size * 0.22}px ${size * 0.5}px`,
        fontFamily: SANS,
        fontWeight: 700,
        fontSize: size,
        letterSpacing: "0.1em",
        background: "rgba(12,27,51,0.6)",
        boxShadow: `0 0 ${60 * (1 - k) + 20}px rgba(184,151,90,${0.55 * (1 - k) + 0.15})`,
        ...GOLD_TEXT,
        backgroundColor: "rgba(12,27,51,0.6)",
      }}
    >
      <span style={GOLD_TEXT}>{children}</span>
    </div>
  );
};

// ---------- ícones (traço dourado) ----------
const IconWrap: React.FC<{ size: number; children: React.ReactNode }> = ({ size, children }) => (
  <svg width={size} height={size} viewBox="0 0 100 100" style={{ filter: "drop-shadow(0 4px 6px rgba(0,0,0,0.25))" }}>
    <defs>
      <linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stopColor="#E2C88F" />
        <stop offset="0.55" stopColor="#B8975A" />
        <stop offset="1" stopColor="#8E703C" />
      </linearGradient>
    </defs>
    {children}
  </svg>
);

export const IconPerson = ({ size = 90 }: { size?: number }) => (
  <IconWrap size={size}>
    <circle cx="50" cy="30" r="17" fill="url(#g)" />
    <path d="M18 88 C18 62 32 52 50 52 C68 52 82 62 82 88 Z" fill="url(#g)" />
  </IconWrap>
);

export const IconBuilding = ({ size = 90 }: { size?: number }) => (
  <IconWrap size={size}>
    <rect x="22" y="14" width="56" height="76" rx="4" fill="url(#g)" />
    {[0, 1, 2, 3].map((r) =>
      [0, 1, 2].map((c) => <rect key={`${r}${c}`} x={30 + c * 15} y={22 + r * 14} width="9" height="8" fill="#0D1F3C" />),
    )}
    <rect x="43" y="74" width="14" height="16" fill="#0D1F3C" />
  </IconWrap>
);

export const IconClock = ({ size = 70, crossed }: { size?: number; crossed?: boolean }) => (
  <IconWrap size={size}>
    <circle cx="50" cy="50" r="36" fill="none" stroke="url(#g)" strokeWidth="8" />
    <path d="M50 28 V50 L64 60" fill="none" stroke="url(#g)" strokeWidth="7" strokeLinecap="round" />
    {crossed && <path d="M16 84 L84 16" stroke="#0D1F3C" strokeWidth="14" strokeLinecap="round" />}
    {crossed && <path d="M16 84 L84 16" stroke="url(#g)" strokeWidth="7" strokeLinecap="round" />}
  </IconWrap>
);

export const CheckBox: React.FC<{ k: number; size?: number }> = ({ k, size = 54 }) => (
  <svg width={size} height={size} viewBox="0 0 60 60">
    <rect x="4" y="4" width="52" height="52" rx="10" fill={k > 0 ? `rgba(184,151,90,${0.18 * k})` : "none"} stroke={C.gold} strokeWidth="4" />
    <path
      d="M15 31 L26 42 L46 19"
      fill="none"
      stroke={C.gold}
      strokeWidth="7"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeDasharray="50"
      strokeDashoffset={50 * (1 - k)}
    />
  </svg>
);
