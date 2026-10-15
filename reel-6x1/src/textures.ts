import * as THREE from "three";
import { C } from "./util";

export const SERIF = "'Cormorant Garamond'";
export const SANS = "'Outfit'";

type Draw = (ctx: CanvasRenderingContext2D, w: number, h: number) => void;

export const canvasTexture = (w: number, h: number, draw: Draw, repeat?: [number, number]) => {
  const cv = document.createElement("canvas");
  cv.width = w;
  cv.height = h;
  const ctx = cv.getContext("2d")!;
  draw(ctx, w, h);
  const tex = new THREE.CanvasTexture(cv);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = 8;
  if (repeat) {
    tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
    tex.repeat.set(...repeat);
  }
  tex.needsUpdate = true;
  return tex;
};

/** Textura de mármore claro: base off-white com veios suaves. */
export const marbleDraw = (seed = 1, base = C.offWhite): Draw => (ctx, w, h) => {
  ctx.fillStyle = base;
  ctx.fillRect(0, 0, w, h);
  const r = (i: number) => {
    const x = Math.sin((i + seed * 13.7) * 91.3) * 43758.5;
    return x - Math.floor(x);
  };
  ctx.lineCap = "round";
  for (let i = 0; i < 14; i++) {
    ctx.beginPath();
    let x = r(i) * w;
    let y = 0;
    ctx.moveTo(x, y);
    while (y < h) {
      y += h / 12;
      x += (r(i * 7 + y) - 0.5) * w * 0.18;
      ctx.lineTo(x, y);
    }
    ctx.strokeStyle = `rgba(150,140,125,${0.05 + r(i + 40) * 0.08})`;
    ctx.lineWidth = 1 + r(i + 3) * 2.5;
    ctx.stroke();
  }
};

export const spacedText = (
  ctx: CanvasRenderingContext2D,
  text: string,
  x: number,
  y: number,
  spacingPx: number,
) => {
  const chars = [...text];
  const widths = chars.map((ch) => ctx.measureText(ch).width);
  const total = widths.reduce((a, b) => a + b, 0) + spacingPx * (chars.length - 1);
  let cx = x - total / 2;
  const prevAlign = ctx.textAlign;
  ctx.textAlign = "left";
  chars.forEach((ch, i) => {
    ctx.fillText(ch, cx, y);
    cx += widths[i] + spacingPx;
  });
  ctx.textAlign = prevAlign;
};

/** Ouro com gradiente para desenhos 2D em canvas. */
export const goldGradient = (ctx: CanvasRenderingContext2D, y0: number, y1: number) => {
  const g = ctx.createLinearGradient(0, y0, 0, y1);
  g.addColorStop(0, "#E2C88F");
  g.addColorStop(0.5, C.gold);
  g.addColorStop(1, "#8E703C");
  return g;
};

export const roundRect = (ctx: CanvasRenderingContext2D, x: number, y: number, w: number, h: number, r: number) => {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
};

/** Desenha "≤" com traços (a fonte web não tem o glifo). */
export const drawLeq = (ctx: CanvasRenderingContext2D, cx: number, cy: number, s: number, lw: number) => {
  ctx.save();
  ctx.lineWidth = lw;
  ctx.lineCap = "round";
  ctx.lineJoin = "round";
  ctx.beginPath();
  ctx.moveTo(cx + s * 0.45, cy - s * 0.55);
  ctx.lineTo(cx - s * 0.45, cy - s * 0.15);
  ctx.lineTo(cx + s * 0.45, cy + s * 0.25);
  ctx.moveTo(cx - s * 0.45, cy + s * 0.55);
  ctx.lineTo(cx + s * 0.45, cy + s * 0.55);
  ctx.stroke();
  ctx.restore();
};
