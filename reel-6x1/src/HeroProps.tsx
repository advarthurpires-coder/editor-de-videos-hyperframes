import { useMemo } from "react";
import * as THREE from "three";
import { applyPose, cameraAt } from "./camera";
import { T } from "./timeline";
import { canvasTexture, drawLeq, goldGradient, marbleDraw, roundRect, SANS, SERIF, spacedText } from "./textures";
import { C, easeInCubic, easeOutBack, easeOutCubic, H, LEAD, lerp, pop, ramp, W, win } from "./util";

const tmpCam = new THREE.PerspectiveCamera();

/** Converte (px da tela, profundidade) em coordenadas no espaço da câmera. */
const screenToCam = (fov: number, cx: number, cy: number, d: number): [number, number, number] => {
  const hh = d * Math.tan(THREE.MathUtils.degToRad(fov / 2));
  return [((cx - W / 2) / (W / 2)) * hh * (W / H), ((H / 2 - cy) / (H / 2)) * hh, -d];
};

const GoldMat = ({ e = 0, r = 0.28 }: { e?: number; r?: number }) => (
  <meshStandardMaterial color={C.gold} metalness={1} roughness={r} emissive={C.gold} emissiveIntensity={e} />
);

// ---------- peças ----------
const triangleGeo = () => {
  const R = 0.75;
  const pts = [0, 1, 2].map((k) => {
    const a = Math.PI / 2 + (k * 2 * Math.PI) / 3;
    return new THREE.Vector2(Math.cos(a) * R, Math.sin(a) * R);
  });
  const sh = new THREE.Shape(pts);
  const inner = pts.map((p) => p.clone().multiplyScalar(0.7));
  sh.holes.push(new THREE.Path(inner.reverse()));
  return new THREE.ExtrudeGeometry(sh, { depth: 0.16, bevelEnabled: true, bevelSize: 0.05, bevelThickness: 0.05, bevelSegments: 4 });
};

const checkGeo = () => {
  const sh = new THREE.Shape();
  sh.moveTo(-0.62, 0.05);
  sh.lineTo(-0.38, 0.3);
  sh.lineTo(-0.12, 0.04);
  sh.lineTo(0.48, 0.66);
  sh.lineTo(0.72, 0.42);
  sh.lineTo(-0.12, -0.44);
  sh.closePath();
  return new THREE.ExtrudeGeometry(sh, { depth: 0.18, bevelEnabled: true, bevelSize: 0.04, bevelThickness: 0.05, bevelSegments: 4 });
};

const crossGeo = () => {
  const a = 0.17;
  const b = 0.5;
  const sh = new THREE.Shape();
  sh.moveTo(-a, b);
  sh.lineTo(a, b);
  sh.lineTo(a, a);
  sh.lineTo(b, a);
  sh.lineTo(b, -a);
  sh.lineTo(a, -a);
  sh.lineTo(a, -b);
  sh.lineTo(-a, -b);
  sh.lineTo(-a, -a);
  sh.lineTo(-b, -a);
  sh.lineTo(-b, a);
  sh.lineTo(-a, a);
  sh.closePath();
  return new THREE.ExtrudeGeometry(sh, { depth: 0.16, bevelEnabled: true, bevelSize: 0.035, bevelThickness: 0.04, bevelSegments: 3 });
};

const shieldGeo = () => {
  const sh = new THREE.Shape();
  sh.moveTo(0, 0.55);
  sh.bezierCurveTo(0.2, 0.42, 0.38, 0.42, 0.48, 0.42);
  sh.bezierCurveTo(0.5, 0.0, 0.38, -0.36, 0, -0.58);
  sh.bezierCurveTo(-0.38, -0.36, -0.5, 0.0, -0.48, 0.42);
  sh.bezierCurveTo(-0.38, 0.42, -0.2, 0.42, 0, 0.55);
  return new THREE.ExtrudeGeometry(sh, { depth: 0.16, bevelEnabled: true, bevelSize: 0.035, bevelThickness: 0.04, bevelSegments: 3 });
};

const Hourglass = ({ sand }: { sand: number }) => {
  const glass = useMemo(() => {
    const pts: THREE.Vector2[] = [];
    for (let i = 0; i <= 24; i++) {
      const y = -0.6 + (1.2 * i) / 24;
      const r = 0.07 + 0.33 * Math.pow(Math.abs(y) / 0.6, 0.8);
      pts.push(new THREE.Vector2(r, y));
    }
    return new THREE.LatheGeometry(pts, 48);
  }, []);
  return (
    <group>
      {[0.7, -0.7].map((y) => (
        <mesh key={y} castShadow position={[0, y, 0]}>
          <cylinderGeometry args={[0.52, 0.52, 0.12, 48]} />
          <GoldMat />
        </mesh>
      ))}
      {[0, 1, 2].map((k) => {
        const a = (k * 2 * Math.PI) / 3;
        return (
          <mesh key={k} position={[Math.cos(a) * 0.45, 0, Math.sin(a) * 0.45]}>
            <cylinderGeometry args={[0.035, 0.035, 1.3, 12]} />
            <GoldMat />
          </mesh>
        );
      })}
      <mesh geometry={glass}>
        <meshPhysicalMaterial color={"#DCE6F5"} transparent opacity={0.28} roughness={0.05} metalness={0} side={THREE.DoubleSide} depthWrite={false} />
      </mesh>
      {/* areia: cone de cima esvazia, de baixo enche */}
      <mesh position={[0, 0.06 + 0.25 * (1 - sand) * 0.5, 0]} scale={[1 - sand * 0.7, Math.max(0.02, 1 - sand), 1 - sand * 0.7]}>
        <coneGeometry args={[0.3, 0.42, 32]} />
        <GoldMat e={0.2} r={0.6} />
      </mesh>
      <mesh position={[0, -0.6 + 0.2 * Math.max(0.05, sand), 0]} scale={[0.5 + sand * 0.5, Math.max(0.05, sand), 0.5 + sand * 0.5]}>
        <coneGeometry args={[0.32, 0.4, 32]} />
        <GoldMat e={0.2} r={0.6} />
      </mesh>
    </group>
  );
};

const Stamp = () => (
  <group>
    <mesh castShadow position={[0, 0.05, 0]}>
      <cylinderGeometry args={[0.55, 0.55, 0.12, 64]} />
      <GoldMat />
    </mesh>
    <mesh castShadow position={[0, 0.32, 0]}>
      <cylinderGeometry args={[0.13, 0.22, 0.44, 48]} />
      <GoldMat />
    </mesh>
    <mesh castShadow position={[0, 0.66, 0]}>
      <sphereGeometry args={[0.22, 48, 24]} />
      <GoldMat r={0.22} />
    </mesh>
  </group>
);

const Padlock = ({ closed }: { closed: number }) => (
  <group>
    <mesh castShadow>
      <boxGeometry args={[0.62, 0.5, 0.22]} />
      <GoldMat r={0.25} />
    </mesh>
    <mesh position={[0, 0.25 + 0.22 * (1 - closed), 0]}>
      <torusGeometry args={[0.2, 0.05, 16, 48, Math.PI]} />
      <GoldMat r={0.22} />
    </mesh>
    <mesh position={[-0.2, 0.25 + 0.22 * (1 - closed) - 0.06, 0]}>
      <cylinderGeometry args={[0.05, 0.05, 0.12, 16]} />
      <GoldMat />
    </mesh>
    <mesh position={[0.2, 0.25 - 0.06 + 0.22 * (1 - closed), 0]}>
      <cylinderGeometry args={[0.05, 0.05, 0.12, 16]} />
      <GoldMat />
    </mesh>
    <mesh position={[0, 0.02, 0.115]}>
      <circleGeometry args={[0.06, 24]} />
      <meshBasicMaterial color={C.navyDeep} />
    </mesh>
    <mesh position={[0, -0.08, 0.115]}>
      <planeGeometry args={[0.04, 0.14]} />
      <meshBasicMaterial color={C.navyDeep} />
    </mesh>
  </group>
);

const Bus = () => (
  <group>
    <mesh castShadow>
      <boxGeometry args={[1.0, 0.62, 0.42]} />
      <GoldMat />
    </mesh>
    {[-0.3, 0, 0.3].map((x) => (
      <mesh key={x} position={[x, 0.1, 0.215]}>
        <planeGeometry args={[0.22, 0.2]} />
        <meshStandardMaterial color={C.navy} metalness={0.5} roughness={0.2} />
      </mesh>
    ))}
    {[-0.3, 0.3].map((x) => (
      <mesh key={x} position={[x, -0.33, 0.12]} rotation={[Math.PI / 2, 0, 0]}>
        <cylinderGeometry args={[0.1, 0.1, 0.08, 24]} />
        <meshStandardMaterial color={C.navyDeep} metalness={0.4} roughness={0.4} />
      </mesh>
    ))}
  </group>
);

const Diploma = () => (
  <group rotation={[0, 0, 0.18]}>
    <mesh castShadow rotation={[0, 0, Math.PI / 2]}>
      <cylinderGeometry args={[0.2, 0.2, 1.3, 48]} />
      <meshPhysicalMaterial color={C.offWhite} roughness={0.5} sheen={0.5} />
    </mesh>
    {[-0.66, 0.66].map((x) => (
      <mesh key={x} position={[x, 0, 0]} rotation={[0, 0, Math.PI / 2]}>
        <cylinderGeometry args={[0.215, 0.215, 0.05, 48]} />
        <GoldMat />
      </mesh>
    ))}
    <mesh position={[0, 0, 0]} rotation={[0, 0, Math.PI / 2]}>
      <cylinderGeometry args={[0.215, 0.215, 0.12, 48]} />
      <GoldMat />
    </mesh>
    <mesh position={[0.05, -0.3, 0.12]} rotation={[0, 0, -0.3]}>
      <boxGeometry args={[0.1, 0.35, 0.02]} />
      <GoldMat />
    </mesh>
    <mesh position={[-0.08, -0.3, 0.12]} rotation={[0, 0, 0.3]}>
      <boxGeometry args={[0.1, 0.35, 0.02]} />
      <GoldMat />
    </mesh>
  </group>
);

const Store = ({ awning }: { awning: THREE.Texture }) => (
  <group>
    <mesh castShadow receiveShadow position={[0, 0, 0]}>
      <boxGeometry args={[1.7, 1.15, 0.9]} />
      <meshStandardMaterial color={"#17305A"} metalness={0.3} roughness={0.45} />
    </mesh>
    {/* porta e vitrine */}
    <mesh position={[-0.42, -0.2, 0.455]}>
      <planeGeometry args={[0.42, 0.72]} />
      <meshStandardMaterial color={C.offWhite} emissive={"#FFE6B8"} emissiveIntensity={0.45} />
    </mesh>
    <mesh position={[0.32, -0.08, 0.455]}>
      <planeGeometry args={[0.72, 0.46]} />
      <meshStandardMaterial color={C.offWhite} emissive={"#FFE6B8"} emissiveIntensity={0.45} />
    </mesh>
    {/* letreiro */}
    <mesh position={[0, 0.42, 0.46]}>
      <planeGeometry args={[1.3, 0.16]} />
      <GoldMat e={0.3} />
    </mesh>
    {/* toldo */}
    <mesh castShadow position={[0, 0.22, 0.62]} rotation={[0.55, 0, 0]}>
      <boxGeometry args={[1.8, 0.04, 0.5]} />
      <meshStandardMaterial map={awning} metalness={0.4} roughness={0.4} />
    </mesh>
    {/* telhado */}
    <mesh castShadow position={[0, 0.63, 0]}>
      <boxGeometry args={[1.86, 0.1, 1.0]} />
      <GoldMat />
    </mesh>
  </group>
);

// ---------- montagem ----------
type Props = { t: number; glowTex: THREE.Texture; marbleMap: THREE.Texture };

export const HeroProps = ({ t, glowTex }: Props) => {
  const geo = useMemo(() => ({ tri: triangleGeo(), check: checkGeo(), cross: crossGeo(), shield: shieldGeo() }), []);
  const tex = useMemo(
    () => ({
      coin: canvasTexture(512, 512, (ctx, w, h) => {
        ctx.fillStyle = goldGradient(ctx, 0, h);
        ctx.fillRect(0, 0, w, h);
        ctx.strokeStyle = "rgba(70,48,12,0.55)";
        ctx.lineWidth = 10;
        ctx.beginPath();
        ctx.arc(w / 2, h / 2, w * 0.43, 0, Math.PI * 2);
        ctx.stroke();
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.arc(w / 2, h / 2, w * 0.39, 0, Math.PI * 2);
        ctx.stroke();
        ctx.fillStyle = C.navy;
        ctx.strokeStyle = C.navy;
        drawLeq(ctx, w * 0.27, h * 0.5, 82, 15);
        ctx.font = `700 150px ${SANS}`;
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText("40h", w * 0.6, h * 0.52);
      }),
      payslip: canvasTexture(640, 840, (ctx, w, h) => {
        marbleDraw(21)(ctx, w, h);
        ctx.strokeStyle = C.gold;
        ctx.lineWidth = 8;
        roundRect(ctx, 20, 20, w - 40, h - 40, 16);
        ctx.stroke();
        ctx.fillStyle = C.navy;
        ctx.font = `600 54px ${SANS}`;
        ctx.textBaseline = "middle";
        spacedText(ctx, "HOLERITE", w / 2, 92, 12);
        ctx.fillStyle = C.gold;
        ctx.fillRect(70, 140, w - 140, 5);
        for (let k = 0; k < 6; k++) {
          const y = 210 + k * 70;
          ctx.fillStyle = "rgba(13,31,60,0.75)";
          ctx.fillRect(70, y, 200 + ((k * 53) % 120), 16);
          ctx.fillRect(w - 70 - 120, y, 120, 16);
        }
        ctx.fillStyle = C.navy;
        ctx.fillRect(70, 660, w - 140, 3);
        ctx.font = `700 62px ${SERIF}`;
        ctx.textAlign = "left";
        ctx.fillText("SALÁRIO", 70, 720);
        ctx.fillStyle = C.gold;
        ctx.textAlign = "right";
        ctx.fillText("100%", w - 70, 720);
      }),
      week: canvasTexture(1400, 420, (ctx, w, h) => {
        marbleDraw(31)(ctx, w, h);
        ctx.fillStyle = C.navy;
        ctx.fillRect(0, 0, w, 110);
        ctx.fillStyle = C.gold;
        ctx.font = `600 52px ${SANS}`;
        ctx.textBaseline = "middle";
        spacedText(ctx, "SEMANA", w / 2, 58, 18);
        const days = ["SEG", "TER", "QUA", "QUI", "SEX", "SÁB", "DOM"];
        days.forEach((d, k) => {
          const x = 30 + k * 194;
          ctx.strokeStyle = "rgba(13,31,60,0.25)";
          ctx.lineWidth = 3;
          roundRect(ctx, x, 140, 176, 250, 16);
          ctx.stroke();
          ctx.fillStyle = k >= 5 ? C.gold : C.navy;
          ctx.font = `600 50px ${SANS}`;
          ctx.textAlign = "center";
          ctx.fillText(d, x + 88, 265);
        });
      }),
      awning: canvasTexture(512, 128, (ctx, w, h) => {
        for (let k = 0; k < 8; k++) {
          ctx.fillStyle = k % 2 ? C.offWhite : C.gold;
          ctx.fillRect((k * w) / 8, 0, w / 8 + 1, h);
        }
      }),
      domTile: canvasTexture(256, 360, (ctx, w, h) => {
        ctx.fillStyle = goldGradient(ctx, 0, h);
        ctx.fillRect(0, 0, w, h);
        ctx.fillStyle = C.navy;
        ctx.font = `700 76px ${SANS}`;
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText("DOM", w / 2, h / 2);
      }),
    }),
    [],
  );

  const pose = cameraAt(t);
  applyPose(tmpCam, pose);
  const fov = pose.fov;
  const at = (cx: number, cy: number, d: number) => screenToCam(fov, cx, cy, d);

  const items: React.ReactNode[] = [];

  // Cena 2 · triângulo de aviso
  {
    const a = T.cuidado - LEAD;
    const vis = win(t, a, T.cobrar - 0.02, 0.05, 0.3);
    if (vis > 0) {
      const spin = (1 - ramp(t, a, a + 0.75, easeOutCubic)) * Math.PI * 3;
      const sc = pop(t, a, 0.5) * vis;
      items.push(
        <group key="tri" position={at(540, 640, 6)} rotation={[0, spin + Math.sin(t * 2) * 0.12, 0]} scale={sc}>
          <mesh geometry={geo.tri} position={[0, 0, -0.08]} castShadow>
            <GoldMat e={0.12} />
          </mesh>
          <mesh position={[0, 0.06, 0.05]}>
            <boxGeometry args={[0.13, 0.42, 0.1]} />
            <GoldMat e={0.12} />
          </mesh>
          <mesh position={[0, -0.27, 0.05]}>
            <sphereGeometry args={[0.08, 24, 16]} />
            <GoldMat e={0.12} />
          </mesh>
        </group>,
      );
    }
  }

  // Cena 2 · ampulheta ("quando vale")
  {
    const a = T.quando - LEAD;
    const vis = win(t, a, 11.85, 0.05, 0.3);
    if (vis > 0) {
      const sc = pop(t, a, 0.5) * vis * 0.48;
      items.push(
        <group key="hg1" position={at(540, 950, 6)} rotation={[0.15, t * 1.6, 0.1]} scale={sc}>
          <Hourglass sand={ramp(t, a, a + 1.2)} />
        </group>,
      );
    }
  }

  // Carimbo que "entra" na tela (PROMULGAÇÃO e VALE A REGRA DE HOJE)
  for (const hit of [T.promulga - 0.03, T.hoje - 0.03]) {
    const inK = ramp(t, hit - 0.42, hit, easeInCubic);
    const outK = ramp(t, hit + 0.08, hit + 0.38, easeInCubic);
    if (t > hit - 0.42 && outK < 1) {
      const d = lerp(15, 4.6, inK) + outK * 10;
      const cy = hit === T.hoje - 0.03 ? 760 : 700;
      items.push(
        <group key={`stamp${hit}`} position={at(540, cy, d)} rotation={[Math.PI / 2 - 0.25, 0, 0]}>
          <Stamp />
        </group>,
      );
    }
  }

  // Cena 3 · ampulheta virando (prazos)
  {
    const a = T.prazos - LEAD;
    const vis = win(t, a, 24.25, 0.05, 0.3);
    if (vis > 0) {
      const flip = ramp(t, a + 0.1, a + 0.75, (x) => easeOutBack(x, 1.4)) * Math.PI;
      items.push(
        <group key="hg2" position={at(540, 640, 6)} rotation={[0, t * 0.8, flip]} scale={pop(t, a, 0.45) * vis * 0.8}>
          <Hourglass sand={1 - ramp(t, a + 0.75, a + 2.2)} />
        </group>,
      );
    }
  }

  // Cena 4 · holerite + cadeado
  {
    const a = T.salario - LEAD;
    const vis = win(t, a, 36.3, 0.05, 0.35);
    if (vis > 0) {
      const closed = ramp(t, a + 0.35, a + 0.6, easeInCubic);
      const sc = pop(t, a, 0.5) * vis * 0.6;
      items.push(
        <group key="slip" position={at(540, 610, 6.4)} rotation={[-0.12, -0.3 + ramp(t, a, a + 2) * 0.3 + Math.sin(t) * 0.04, 0.03]} scale={sc}>
          <mesh castShadow>
            <boxGeometry args={[1.6, 2.1, 0.08]} />
            <meshStandardMaterial attach="material-0" color={C.offWhite} />
            <meshStandardMaterial attach="material-1" color={C.offWhite} />
            <meshStandardMaterial attach="material-2" color={C.offWhite} />
            <meshStandardMaterial attach="material-3" color={C.offWhite} />
            <meshStandardMaterial attach="material-4" map={tex.payslip} roughness={0.5} />
            <meshStandardMaterial attach="material-5" color={C.offWhite} />
          </mesh>
          <group position={[0.62, -0.92, 0.2]} scale={0.95} rotation={[0, 0.25, 0]}>
            <Padlock closed={closed} />
          </group>
          <sprite position={[0.62, -0.92, 0.4]} scale={[1.4, 1.4, 1]}>
            <spriteMaterial map={glowTex} color={C.gold} transparent opacity={Math.max(0, 1 - Math.abs(t - a - 0.62) / 0.5) * 0.8} blending={THREE.AdditiveBlending} depthWrite={false} />
          </sprite>
        </group>,
      );
    }
  }

  // Cena 5 · calendário semanal (DOM em ouro)
  {
    const a = T.preferencia - LEAD;
    const vis = win(t, a, T.menos40 - 0.1, 0.05, 0.3);
    if (vis > 0) {
      const rise = ramp(t, T.domingo - LEAD, T.domingo + 0.35, (x) => easeOutBack(x, 1.6));
      items.push(
        <group key="week" position={at(540, 700, 7)} rotation={[-0.35 + ramp(t, a, a + 2.4) * 0.15, -0.18 + Math.sin(t * 0.8) * 0.05, 0]} scale={pop(t, a, 0.5) * vis * 0.85}>
          <mesh castShadow receiveShadow>
            <boxGeometry args={[2.8, 0.84, 0.1]} />
            <meshStandardMaterial attach="material-0" color={C.offWhite} />
            <meshStandardMaterial attach="material-1" color={C.offWhite} />
            <meshStandardMaterial attach="material-2" color={C.offWhite} />
            <meshStandardMaterial attach="material-3" color={C.offWhite} />
            <meshStandardMaterial attach="material-4" map={tex.week} roughness={0.5} />
            <meshStandardMaterial attach="material-5" color={C.offWhite} />
          </mesh>
          <mesh castShadow position={[1.07 + 0.0, -0.1 + rise * 0.12, 0.06 + rise * 0.25]} rotation={[0, -rise * 0.25, 0]} scale={1 + rise * 0.18}>
            <boxGeometry args={[0.36, 0.5, 0.06]} />
            <meshStandardMaterial attach="material-0" color={C.gold} metalness={1} roughness={0.3} />
            <meshStandardMaterial attach="material-1" color={C.gold} metalness={1} roughness={0.3} />
            <meshStandardMaterial attach="material-2" color={C.gold} metalness={1} roughness={0.3} />
            <meshStandardMaterial attach="material-3" color={C.gold} metalness={1} roughness={0.3} />
            <meshStandardMaterial attach="material-4" map={tex.domTile} metalness={0.7} roughness={0.3} emissive={C.gold} emissiveIntensity={0.25 * rise} />
            <meshStandardMaterial attach="material-5" color={C.gold} metalness={1} roughness={0.3} />
          </mesh>
          <sprite position={[1.07, 0, 0.3]} scale={[1.2, 1.2, 1]}>
            <spriteMaterial map={glowTex} color={C.gold} transparent opacity={rise * 0.45} blending={THREE.AdditiveBlending} depthWrite={false} />
          </sprite>
        </group>,
      );
    }
  }

  // Cena 5 · selo ≤ 40h
  {
    const a = T.menos40 - LEAD;
    const vis = win(t, a, T.tambem - 0.05, 0.05, 0.3);
    if (vis > 0) {
      const spin = (1 - ramp(t, a, a + 0.9, easeOutCubic)) * Math.PI * 4;
      items.push(
        <group key="coin" position={at(540, 660, 6)} rotation={[Math.PI / 2 + 0.12, spin + Math.sin(t * 1.5) * 0.1, 0]} scale={pop(t, a, 0.5) * vis * 0.65}>
          <mesh castShadow rotation={[0, Math.PI / 2, 0]}>
            <cylinderGeometry args={[0.78, 0.78, 0.14, 96]} />
            <meshStandardMaterial attach="material-0" color={C.gold} metalness={1} roughness={0.28} />
            <meshStandardMaterial attach="material-1" map={tex.coin} metalness={0.85} roughness={0.32} />
            <meshStandardMaterial attach="material-2" map={tex.coin} metalness={0.85} roughness={0.32} />
          </mesh>
        </group>,
      );
    }
  }

  // Cena 5 · check dourado
  {
    const a = T.tambem - LEAD;
    const vis = win(t, a, 43.5, 0.05, 0.3);
    if (vis > 0) {
      items.push(
        <group key="check" position={at(540, 640, 6)} rotation={[0.1, (1 - ramp(t, a, a + 0.6, easeOutCubic)) * Math.PI * 1.5 + Math.sin(t * 1.4) * 0.12, 0]} scale={pop(t, a, 0.5) * vis * 0.8}>
          <mesh geometry={geo.check} castShadow position={[0, 0, -0.09]}>
            <GoldMat e={0.15} />
          </mesh>
        </group>,
      );
    }
  }

  // Cena 6 · emblemas 3D sobre os cartões do tambor
  {
    const swap = [T.saude - LEAD, T.profissionais - LEAD, T.micro - LEAD, T.hoje - 0.15];
    for (let k = 0; k < 3; k++) {
      const a = swap[k];
      const b = swap[k + 1];
      const vis = win(t, a, b, 0.05, 0.25);
      if (vis <= 0) continue;
      const spinIn = (1 - ramp(t, a, a + 0.6, easeOutCubic)) * -Math.PI;
      const spinOut = ramp(t, b - 0.25, b, easeInCubic) * Math.PI * 0.6;
      const rotY = spinIn + spinOut + Math.sin(t * 1.2) * 0.18;
      const sc = pop(t, a, 0.5) * vis;
      const base = at(540, 430, 7);
      if (k === 0) {
        const icons = [
          { x: -1.05, el: <mesh geometry={geo.cross} position={[0, 0, -0.08]}><GoldMat e={0.1} /></mesh>, d: 0 },
          { x: 0, el: <mesh geometry={geo.shield} position={[0, 0, -0.08]}><GoldMat e={0.1} /></mesh>, d: 0.12 },
          { x: 1.05, el: <Bus />, d: 0.24 },
        ];
        items.push(
          <group key="emb0" position={base} scale={sc * 0.8}>
            {icons.map((ic, n) => (
              <group key={n} position={[ic.x, Math.sin(t * 2 + n) * 0.05, 0]} rotation={[0, rotY + n * 0.2, 0]} scale={pop(t, a + ic.d, 0.45)}>
                {ic.el}
              </group>
            ))}
          </group>,
        );
      } else if (k === 1) {
        items.push(
          <group key="emb1" position={base} rotation={[0.1, rotY, 0]} scale={sc * 0.8}>
            <Diploma />
          </group>,
        );
      } else {
        items.push(
          <group key="emb2" position={base} rotation={[0.18, rotY * 0.6 - 0.35, 0]} scale={sc * 0.65}>
            <Store awning={tex.awning} />
          </group>,
        );
      }
    }
  }

  return (
    <group position={tmpCam.position.clone()} quaternion={tmpCam.quaternion.clone()}>
      <pointLight position={[2.5, 3, 1]} intensity={14} color={"#FFE3B5"} distance={14} decay={1.6} />
      <pointLight position={[-3, -1, -2]} intensity={6} color={"#9DB6E6"} distance={14} decay={1.6} />
      {items}
    </group>
  );
};


