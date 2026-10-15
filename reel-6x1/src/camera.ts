import * as THREE from "three";
import { T } from "./timeline";
import { clamp, easeInOutCubic, lerp, shake, W, H } from "./util";

type V3 = [number, number, number];
type Key = { t: number; pos: V3; tgt: V3; fov?: number; cut?: boolean; ease?: (x: number) => number };

// Plano-sequência: cada capítulo é uma "estação" no mesmo mundo.
// Colunas em z=0 (x de -3,45 a 3,45); trilho dourado em z=2,4; placa em (0, 0.74, 5).
const KEYS: Key[] = [
  // Cena 1 · gancho: close extremo no carimbo, depois dolly-out revelando as colunas
  { t: 0, pos: [0.05, 3.35, 6.75], tgt: [0, 0.78, 5.15], fov: 38 },
  { t: 0.7, pos: [0.03, 3.15, 6.6], tgt: [0, 0.78, 5.15], fov: 38 },
  { t: 2.3, pos: [-7.8, 2.4, 19.5], tgt: [0.2, 2.15, 0], fov: 40, ease: (x) => 1 - Math.pow(1 - x, 4) },
  { t: 5.3, pos: [-6.6, 2.2, 18.2], tgt: [0.2, 2.2, 0], fov: 40 },
  // Cena 2 · alerta: órbita lenta para a direita, ângulo baixo
  { t: 7.0, pos: [-2.0, 1.6, 17.0], tgt: [0, 2.6, 0], fov: 40 },
  { t: 11.4, pos: [4.5, 1.8, 17.0], tgt: [0, 2.6, 0], fov: 40 },
  // Cena 3 · capítulo 1: a notícia flutua sobre o mundo; câmera desce em direção ao trilho
  { t: 12.6, pos: [7.0, 4.2, 13.0], tgt: [0.5, 1.6, 0], fov: 40 },
  { t: 17.2, pos: [2.5, 5.0, 13.5], tgt: [-0.5, 1.4, 0.5], fov: 40 },
  { t: 21.6, pos: [-3.0, 3.6, 12.5], tgt: [-2.5, 1.4, 1.5], fov: 40 },
  { t: 23.6, pos: [-10.5, 1.5, 7.2], tgt: [-6.0, 0.4, 2.4], fov: 40 },
  // Cena 4 · capítulo 2: linha do tempo ao lado das colunas
  { t: 25.0, pos: [-9.0, 1.9, 7.6], tgt: [-5.2, 0.6, 2.4], fov: 40 },
  { t: 26.3, pos: [-6.0, 2.2, 18.5], tgt: [0.2, 2.15, 0.5], fov: 40 },
  { t: 30.9, pos: [-3.8, 2.2, 18.2], tgt: [0.4, 2.2, 0.5], fov: 40 },
  { t: 32.6, pos: [4.4, 2.4, 8.2], tgt: [7.4, 1.6, 2.4], fov: 40 },
  { t: 35.0, pos: [5.4, 2.6, 7.8], tgt: [7.6, 1.7, 2.4], fov: 40 },
  // Cena 5 · capítulo 3: volta para a fachada
  { t: 36.8, pos: [7.0, 2.4, 18.5], tgt: [1.0, 2.3, 0], fov: 40 },
  { t: 43.0, pos: [0.0, 2.2, 20.0], tgt: [0, 2.15, 0], fov: 40 },
  // Cena 6 · capítulo 4: ângulo baixo heroico, depois plongée
  { t: 49.5, pos: [-6.5, 0.9, 12.0], tgt: [0, 3.4, 0], fov: 40 },
  { t: 55.4, pos: [-2.0, 6.0, 13.0], tgt: [0, 1.5, 0], fov: 40 },
  { t: 61.2, pos: [5.0, 2.4, 15.0], tgt: [0, 2.2, 0], fov: 40 },
  // Cena 7 · capítulo 5: duas "salas" — esquerda (empregado) e direita (empresário)
  { t: 62.4, pos: [-9.5, 2.4, 8.5], tgt: [-4.5, 2.0, 0], fov: 40 },
  { t: 67.0, pos: [-8.6, 2.2, 8.0], tgt: [-4.0, 2.0, 0], fov: 40 },
  { t: 68.6, pos: [9.5, 2.4, 8.5], tgt: [4.5, 2.0, 0], fov: 40 },
  { t: 71.4, pos: [8.6, 2.2, 8.0], tgt: [4.0, 2.0, 0], fov: 40 },
  { t: 73.4, pos: [0.0, 2.4, 19.0], tgt: [0, 2.2, 0], fov: 40 },
  // Cena 8 · tema quente: grua alta
  { t: 75.6, pos: [0.6, 2.0, 18.0], tgt: [0, 2.3, 0], fov: 40 },
  { t: 78.4, pos: [3.0, 8.5, 14.0], tgt: [0, 0.8, 0.5], fov: 40 },
  { t: 83.0, pos: [-3.5, 6.5, 14.5], tgt: [0, 1.4, 0.5], fov: 40 },
  // Cena 9 · CTA e assinatura (câmera baixa, à direita: perspectiva do símbolo)
  { t: 86.8, pos: [-1.0, 2.4, 18.5], tgt: [0, 2.2, 0], fov: 40 },
  { t: 87.9, pos: [5.0, 0.6, 19.0], tgt: [-0.2, 1.6, 0], fov: 38 },
  { t: 99, pos: [4.9, 0.6, 18.8], tgt: [-0.2, 1.6, 0], fov: 38 },
];

const lerp3 = (a: V3, b: V3, k: number): V3 => [lerp(a[0], b[0], k), lerp(a[1], b[1], k), lerp(a[2], b[2], k)];

export type CamPose = { pos: V3; tgt: V3; fov: number; roll: number };

export const cameraAt = (t: number): CamPose => {
  let i = 0;
  while (i < KEYS.length - 2 && KEYS[i + 1].t <= t) i++;
  const a = KEYS[i];
  const b = KEYS[i + 1];
  const raw = clamp((t - a.t) / (b.t - a.t));
  const k = b.cut ? (raw > 0 ? 1 : 0) : (b.ease ?? easeInOutCubic)(raw);
  const pos = lerp3(a.pos, b.pos, k);
  const tgt = lerp3(a.tgt, b.tgt, k);
  const fov = lerp(a.fov ?? 40, b.fov ?? 40, k);

  // Deriva contínua: a tela nunca fica parada.
  pos[0] += Math.sin(t * 0.55) * 0.18;
  pos[1] += Math.sin(t * 0.43 + 1.3) * 0.1;
  pos[2] += Math.cos(t * 0.37) * 0.15;

  // Impactos: carimbos e números grandes.
  const s =
    shake(t, 0.05, 0.05) +
    shake(t, T.promulga - 0.02, 0.035) +
    shake(t, T.hoje - 0.02, 0.035) +
    shake(t, T.n75 + 0.3, 0.02);
  pos[0] += s;
  pos[1] += s * 0.6;
  tgt[1] += s * 0.4;
  const roll = s * 0.15;
  return { pos, tgt, fov, roll };
};

const camCache = new THREE.PerspectiveCamera(40, W / H, 0.1, 200);

export const applyPose = (cam: THREE.PerspectiveCamera, p: CamPose) => {
  cam.fov = p.fov;
  cam.aspect = W / H;
  cam.near = 0.1;
  cam.far = 200;
  cam.position.set(...p.pos);
  cam.up.set(Math.sin(p.roll), Math.cos(p.roll), 0);
  cam.lookAt(...p.tgt);
  cam.updateProjectionMatrix();
  cam.updateMatrixWorld(true);
};

/** Projeta um ponto do mundo para pixels da tela (para rótulos HTML ancorados no 3D). */
export const project = (t: number, p: V3) => {
  applyPose(camCache, cameraAt(t));
  const v = new THREE.Vector3(...p).project(camCache);
  const dist = camCache.position.distanceTo(new THREE.Vector3(...p));
  return { x: (v.x * 0.5 + 0.5) * W, y: (-v.y * 0.5 + 0.5) * H, visible: v.z < 1, dist };
};
