import { useThree } from "@react-three/fiber";
import { useMemo } from "react";
import { useCurrentFrame } from "remotion";
import * as THREE from "three";
import { RoomEnvironment } from "three/examples/jsm/environments/RoomEnvironment.js";
import { applyPose, cameraAt } from "./camera";
import { HeroProps } from "./HeroProps";
import { T } from "./timeline";
import {
  canvasTexture,
  goldGradient,
  marbleDraw,
  roundRect,
  SANS,
  spacedText,
} from "./textures";
import { C, clamp, easeInCubic, easeOutBack, easeOutCubic, FPS, LEAD, lerp, ramp, rand } from "./util";

export const DAYS = ["SEG", "TER", "QUA", "QUI", "SEX", "SÁB", "DOM"];
export const COL_SPACING = 1.15;
export const colX = (i: number) => (i - 3) * COL_SPACING;
export const RAIL_Z = 2.4;
export const MARKERS = [
  { x: -6.0, label: "DIA 0", sub: "PROMULGAÇÃO" },
  { x: -2.6, label: "+2 MESES", sub: "2 FOLGAS · 42h" },
  { x: 7.4, label: "+14 MESES", sub: "40h" },
];

const GOLD = new THREE.Color(C.gold);
const MARBLE = new THREE.Color(C.offWhite);
const MARBLE_DIM = new THREE.Color("#3B4660");

// ---------- ambiente ----------
const Environment = () => {
  const { gl, scene } = useThree();
  useMemo(() => {
    const pm = new THREE.PMREMGenerator(gl);
    scene.environment = pm.fromScene(new RoomEnvironment(), 0.04).texture;
    scene.environmentIntensity = 0.55;
    scene.background = new THREE.Color(C.navyDeep);
    scene.fog = new THREE.Fog(C.navyDeep, 14, 40);
    gl.toneMapping = THREE.ACESFilmicToneMapping;
    gl.toneMappingExposure = 0.92;
    gl.shadowMap.type = THREE.PCFSoftShadowMap;
  }, [gl, scene]);
  return null;
};

const COVER_POSE = { pos: [-7.0, 0.8, 17.5] as [number, number, number], tgt: [0.3, 4.0, 0] as [number, number, number], fov: 40, roll: 0 };

const Rig = ({ t, cover }: { t: number; cover?: boolean }) => {
  const camera = useThree((s) => s.camera) as THREE.PerspectiveCamera;
  applyPose(camera, cover ? COVER_POSE : cameraAt(t));
  return null;
};

// ---------- geometria ----------
const flutedShaft = () => {
  const g = new THREE.CylinderGeometry(0.29, 0.335, 3.3, 96, 8, false);
  const p = g.attributes.position;
  for (let i = 0; i < p.count; i++) {
    const x = p.getX(i);
    const z = p.getZ(i);
    const r = Math.hypot(x, z);
    if (r < 0.05) continue;
    const a = Math.atan2(z, x);
    const f = 1 - 0.045 * Math.pow(0.5 + 0.5 * Math.cos(a * 20), 3);
    p.setX(i, x * f);
    p.setZ(i, z * f);
  }
  g.computeVertexNormals();
  return g;
};

const useShared = () =>
  useMemo(() => {
    const marbleMap = canvasTexture(512, 1024, marbleDraw(3));
    const floorMap = canvasTexture(
      1024,
      1024,
      (ctx, w, h) => {
        ctx.fillStyle = "#0B1A31";
        ctx.fillRect(0, 0, w, h);
        for (let i = 0; i < 2600; i++) {
          ctx.fillStyle = `rgba(255,255,255,${rand(i) * 0.018})`;
          ctx.fillRect(rand(i + 1) * w, rand(i + 2) * h, 2, 2);
        }
        ctx.strokeStyle = "rgba(184,151,90,0.10)";
        ctx.lineWidth = 2;
        for (let k = 0; k <= 4; k++) {
          ctx.beginPath();
          ctx.moveTo((k * w) / 4, 0);
          ctx.lineTo((k * w) / 4, h);
          ctx.moveTo(0, (k * h) / 4);
          ctx.lineTo(w, (k * h) / 4);
          ctx.stroke();
        }
      },
      [10, 10],
    );
    const dayTex = DAYS.map((d) =>
      canvasTexture(512, 220, (ctx, w, h) => {
        marbleDraw(7)(ctx, w, h);
        ctx.fillStyle = C.navy;
        ctx.font = `600 104px ${SANS}`;
        ctx.textBaseline = "middle";
        spacedText(ctx, d, w / 2, h / 2 + 6, 14);
        ctx.fillStyle = C.gold;
        ctx.fillRect(w * 0.2, h - 26, w * 0.6, 6);
      }),
    );
    const glowTex = canvasTexture(256, 256, (ctx, w, h) => {
      const g = ctx.createRadialGradient(w / 2, h / 2, 0, w / 2, h / 2, w / 2);
      g.addColorStop(0, "rgba(255,255,255,1)");
      g.addColorStop(0.35, "rgba(255,255,255,0.35)");
      g.addColorStop(1, "rgba(255,255,255,0)");
      ctx.fillStyle = g;
      ctx.fillRect(0, 0, w, h);
    });
    return { marbleMap, floorMap, dayTex, glowTex, shaft: flutedShaft() };
  }, []);

type Shared = ReturnType<typeof useShared>;

// ---------- colunas ----------
const columnState = (i: number, t: number) => {
  // aceso = dia de trabalho
  let lit = i < 5 ? 1 : i === 5 ? 1 - ramp(t, T.folgas - LEAD, T.folgas + 0.35) : 0;
  // descanso dourado (5x2)
  let rest = i >= 5 ? ramp(t, T.folgas + 0.15, T.folgas + 0.9) : 0;
  // destaque do domingo (capítulo 3)
  if (i === 6) rest += 0.8 * ramp(t, T.domingo - 0.2, T.domingo + 0.3) * (1 - ramp(t, 42.8, 43.6));
  // "tic-tic-tic" nos 6 dias
  let pulse = 0;
  if (i < 6) {
    const s = T.seisDias - LEAD + i * 0.085;
    const d = t - s;
    if (d > 0 && d < 0.45) pulse = Math.sin((d / 0.45) * Math.PI) * (1 - d / 0.45 * 0.3);
  }
  // pulso quando o 5x2 acende
  if (i < 5) {
    const d = t - (T.folgas + 0.5 + i * 0.07);
    if (d > 0 && d < 0.4) pulse = Math.max(pulse, Math.sin((d / 0.4) * Math.PI) * 0.6);
  }
  // assinatura: descanso desce, trabalho se agrupa
  const fin = ramp(t, T.finale, T.finale + 0.75);
  const sink = i >= 5 ? ramp(t, T.finale - 0.05, T.finale + 0.55, easeInCubic) : 0;
  let x = colX(i);
  let h = 1;
  let tilt = 0;
  if (i < 5) {
    x = lerp(colX(i), (i - 2) * 0.88, fin);
    h = lerp(1, 0.86 + i * 0.05, fin);
    tilt = lerp(0, (i - 2) * -0.025, fin);
    lit = 1;
  }
  rest = clamp(rest);
  return { lit, rest, pulse, x, h, tilt, sink, fin };
};

const Column = ({ i, t, s }: { i: number; t: number; s: Shared }) => {
  const st = columnState(i, t);
  const marbleCol = MARBLE_DIM.clone().lerp(MARBLE, st.lit);
  const shaftCol = marbleCol.clone().lerp(GOLD, st.rest * 0.92);
  const emissive = new THREE.Color(C.gold);
  const emI = st.rest * 0.32 + st.pulse * 0.9 + st.lit * 0.035;
  const y = -st.sink * 4.8;
  const visible = st.sink < 0.999;
  return (
    <group position={[st.x, y, 0]} rotation={[0, 0, st.tilt]} visible={visible}>
      {/* plinto com o dia */}
      <mesh castShadow receiveShadow position={[0, 0.21, 0]}>
        <boxGeometry args={[1.0, 0.42, 1.0]} />
        <meshStandardMaterial attach="material-0" map={s.marbleMap} color={marbleCol} roughness={0.5} />
        <meshStandardMaterial attach="material-1" map={s.marbleMap} color={marbleCol} roughness={0.5} />
        <meshStandardMaterial attach="material-2" map={s.marbleMap} color={marbleCol} roughness={0.5} />
        <meshStandardMaterial attach="material-3" map={s.marbleMap} color={marbleCol} roughness={0.5} />
        <meshStandardMaterial
          attach="material-4"
          map={s.dayTex[i]}
          color={marbleCol}
          roughness={0.5}
          emissive={emissive}
          emissiveIntensity={st.rest * 0.25}
        />
        <meshStandardMaterial attach="material-5" map={s.marbleMap} color={marbleCol} roughness={0.5} />
      </mesh>
      <group scale={[1, st.h, 1]}>
        <mesh castShadow position={[0, 0.48, 0]}>
          <cylinderGeometry args={[0.4, 0.42, 0.12, 48]} />
          <meshStandardMaterial color={C.gold} metalness={1} roughness={0.3} />
        </mesh>
        <mesh castShadow receiveShadow geometry={s.shaft} position={[0, 0.54 + 1.65, 0]}>
          <meshPhysicalMaterial
            map={s.marbleMap}
            color={shaftCol}
            roughness={lerp(0.48, 0.32, st.rest)}
            metalness={st.rest * 0.85}
            sheen={0.4}
            sheenColor={"#ffffff"}
            emissive={emissive}
            emissiveIntensity={emI}
          />
        </mesh>
        <mesh castShadow position={[0, 3.9, 0]}>
          <cylinderGeometry args={[0.36, 0.3, 0.14, 48]} />
          <meshStandardMaterial color={C.gold} metalness={1} roughness={0.3} emissive={emissive} emissiveIntensity={st.pulse * 0.6} />
        </mesh>
        <mesh castShadow receiveShadow position={[0, 4.06, 0]}>
          <boxGeometry args={[0.9, 0.2, 0.9]} />
          <meshStandardMaterial map={s.marbleMap} color={marbleCol} roughness={0.5} />
        </mesh>
      </group>
      {/* brilho no piso */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.012, 0.25]}>
        <planeGeometry args={[2.6, 2.6]} />
        <meshBasicMaterial
          map={s.glowTex}
          color={st.rest > 0.05 ? C.gold : "#FFE7BE"}
          transparent
          opacity={st.lit * 0.16 + st.rest * 0.5 + st.pulse * 0.35}
          blending={THREE.AdditiveBlending}
          depthWrite={false}
        />
      </mesh>
      {/* halo vertical (descanso) */}
      <sprite position={[0, 2.3, -0.2]} scale={[2.4, 5.4, 1]}>
        <spriteMaterial
          map={s.glowTex}
          color={C.gold}
          transparent
          opacity={st.rest * 0.35 + st.pulse * 0.55}
          blending={THREE.AdditiveBlending}
          depthWrite={false}
        />
      </sprite>
    </group>
  );
};

// ---------- frontão da assinatura ----------
const Pediment = ({ t }: { t: number }) => {
  const k = ramp(t, T.finale + 0.4, T.finale + 0.85, (x) => easeOutBack(x, 1.2));
  const geo = useMemo(() => {
    const sh = new THREE.Shape();
    sh.moveTo(-2.45, 0);
    sh.lineTo(2.45, 0);
    sh.lineTo(0, 1.05);
    sh.closePath();
    const hole = new THREE.Path();
    hole.moveTo(-1.6, 0.2);
    hole.lineTo(1.6, 0.2);
    hole.lineTo(0, 0.78);
    hole.closePath();
    sh.holes.push(hole);
    return new THREE.ExtrudeGeometry(sh, { depth: 1.0, bevelEnabled: true, bevelSize: 0.03, bevelThickness: 0.03, bevelSegments: 2 });
  }, []);
  if (t < T.finale + 0.35) return null;
  const y = lerp(9, 4.1, k);
  return (
    <group position={[0, y, 0]}>
      <mesh castShadow position={[0, 0.12, 0]}>
        <boxGeometry args={[4.9, 0.24, 1.15]} />
        <meshStandardMaterial color={C.gold} metalness={1} roughness={0.28} />
      </mesh>
      <mesh castShadow geometry={geo} position={[0, 0.34, -0.5]}>
        <meshStandardMaterial color={C.gold} metalness={1} roughness={0.28} />
      </mesh>
    </group>
  );
};

// ---------- trilho / linha do tempo ----------
const RAIL_X0 = -8.5;
const RAIL_X1 = 9.5;
const Rail = ({ t, s }: { t: number; s: Shared }) => {
  const p = ramp(t, T.prazos - LEAD, T.prazos + 2.2, easeOutCubic);
  if (p <= 0) return null;
  const len = (RAIL_X1 - RAIL_X0) * p;
  const tipX = RAIL_X0 + len;
  const fade = 1 - ramp(t, T.finale - 0.4, T.finale + 0.2);
  return (
    <group visible={fade > 0.01}>
      <mesh position={[RAIL_X0 + len / 2, 0.035, RAIL_Z]} receiveShadow>
        <boxGeometry args={[len, 0.07, 0.11]} />
        <meshStandardMaterial color={C.gold} metalness={1} roughness={0.25} emissive={C.gold} emissiveIntensity={0.18} />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[RAIL_X0 + len / 2, 0.011, RAIL_Z]}>
        <planeGeometry args={[len, 0.9]} />
        <meshBasicMaterial map={s.glowTex} color={C.gold} transparent opacity={0.28 * fade} blending={THREE.AdditiveBlending} depthWrite={false} />
      </mesh>
      {p < 1 && (
        <sprite position={[tipX, 0.1, RAIL_Z]} scale={[1.1, 1.1, 1]}>
          <spriteMaterial map={s.glowTex} color={"#FFE2A8"} transparent opacity={0.9} blending={THREE.AdditiveBlending} depthWrite={false} />
        </sprite>
      )}
      {MARKERS.map((m, idx) => {
        const at = [T.doisMeses - LEAD, T.doisMeses + 0.55, T.m14 - LEAD][idx];
        const k = ramp(t, at, at + 0.45, (x) => easeOutBack(x, 1.6));
        const glow = Math.max(0, 1 - Math.abs(t - at - 0.3) / 0.8);
        if (k <= 0) return null;
        return (
          <group key={idx} position={[m.x, 0, RAIL_Z]} scale={[1, k, 1]}>
            <mesh castShadow position={[0, 0.04, 0]}>
              <cylinderGeometry args={[0.32, 0.36, 0.08, 48]} />
              <meshStandardMaterial color={C.gold} metalness={1} roughness={0.25} />
            </mesh>
            <mesh castShadow position={[0, 0.62, 0]}>
              <cylinderGeometry args={[0.035, 0.035, 1.1, 16]} />
              <meshStandardMaterial color={C.gold} metalness={1} roughness={0.25} />
            </mesh>
            <mesh castShadow position={[0, 1.22, 0]}>
              <sphereGeometry args={[0.12, 32, 16]} />
              <meshStandardMaterial color={C.gold} metalness={1} roughness={0.2} emissive={C.gold} emissiveIntensity={0.3 + glow} />
            </mesh>
            <sprite position={[0, 1.22, 0]} scale={[1.4, 1.4, 1]}>
              <spriteMaterial map={s.glowTex} color={C.gold} transparent opacity={0.25 + glow * 0.6} blending={THREE.AdditiveBlending} depthWrite={false} />
            </sprite>
          </group>
        );
      })}
    </group>
  );
};

// ---------- placa + carimbo (abertura) ----------
const PLAQUE_W = 1.3;
const PLAQUE_D = 1.1;
const STAMP_Z = 0.25;
const Opening = ({ t, s }: { t: number; s: Shared }) => {
  const tex = useMemo(
    () => ({
      plaque: canvasTexture(1024, 866, (ctx, w, h) => {
        marbleDraw(11)(ctx, w, h);
        ctx.strokeStyle = C.gold;
        ctx.lineWidth = 10;
        roundRect(ctx, 24, 24, w - 48, h - 48, 18);
        ctx.stroke();
        ctx.lineWidth = 3;
        roundRect(ctx, 46, 46, w - 92, h - 92, 12);
        ctx.stroke();
        ctx.fillStyle = C.navy;
        ctx.textBaseline = "middle";
        ctx.font = `600 64px ${SANS}`;
        spacedText(ctx, "ESCALA", w / 2, h * 0.16, 24);
        ctx.font = `600 230px ${SANS}`;
        ctx.textAlign = "center";
        ctx.fillText("6x1", w / 2, h * 0.41);
      }),
      stamp: canvasTexture(1024, 340, (ctx, w, h) => {
        ctx.strokeStyle = goldGradient(ctx, 0, h);
        ctx.fillStyle = goldGradient(ctx, 0, h);
        ctx.lineWidth = 16;
        roundRect(ctx, 20, 20, w - 40, h - 40, 26);
        ctx.stroke();
        ctx.lineWidth = 5;
        roundRect(ctx, 48, 48, w - 96, h - 96, 16);
        ctx.stroke();
        ctx.font = `700 150px ${SANS}`;
        ctx.textBaseline = "middle";
        spacedText(ctx, "APROVADO", w / 2, h / 2 + 6, 10);
      }),
    }),
    [],
  );
  const sink = ramp(t, 4.6, 5.8, easeInCubic);
  if (sink >= 1) return null;
  const top = 0.78;
  // carimbo: desce já no quadro 0, impacto em ~0,1 s
  const down = ramp(t, 0, 0.1, easeInCubic);
  const up = ramp(t, 0.24, 0.6, easeInCubic);
  const stampY = top + 0.55 * (1 - down) + up * 3.2;
  const squash = t > 0.1 && t < 0.22 ? 0.85 + ((t - 0.1) / 0.12) * 0.15 : 1;
  const imprint = t >= 0.1 ? 1 : 0;
  const impScale = 1 + 0.12 * (1 - ramp(t, 0.1, 0.32, easeOutCubic));
  const dustK = ramp(t, 0.1, 1.2, easeOutCubic);
  const rot = -0.12;
  return (
    <group position={[0, -sink * 1.0, 5.0]}>
      <mesh castShadow receiveShadow position={[0, 0.35, 0]}>
        <boxGeometry args={[1.5, 0.7, 1.3]} />
        <meshStandardMaterial color={"#16294A"} metalness={0.4} roughness={0.35} />
      </mesh>
      <mesh castShadow receiveShadow position={[0, 0.74, 0]}>
        <boxGeometry args={[PLAQUE_W, 0.08, PLAQUE_D]} />
        <meshStandardMaterial attach="material-0" map={s.marbleMap} roughness={0.45} />
        <meshStandardMaterial attach="material-1" map={s.marbleMap} roughness={0.45} />
        <meshStandardMaterial attach="material-2" map={tex.plaque} roughness={0.45} />
        <meshStandardMaterial attach="material-3" map={s.marbleMap} roughness={0.45} />
        <meshStandardMaterial attach="material-4" map={s.marbleMap} roughness={0.45} />
        <meshStandardMaterial attach="material-5" map={s.marbleMap} roughness={0.45} />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, rot]} position={[0, top + 0.004, STAMP_Z]} scale={impScale}>
        <planeGeometry args={[1.14, 0.38]} />
        <meshStandardMaterial map={tex.stamp} transparent opacity={imprint} metalness={0.7} roughness={0.3} emissive={C.gold} emissiveIntensity={0.25} />
      </mesh>
      {/* carimbo de ouro (retangular) */}
      {up < 1 && (
        <group position={[0, stampY, STAMP_Z]} rotation={[0, -rot, 0]} scale={[1, squash, 1]}>
          <mesh castShadow position={[0, 0.06, 0]}>
            <boxGeometry args={[1.16, 0.12, 0.4]} />
            <meshStandardMaterial color={C.gold} metalness={1} roughness={0.3} />
          </mesh>
          <mesh castShadow position={[0, 0.16, 0]}>
            <boxGeometry args={[1.0, 0.08, 0.3]} />
            <meshStandardMaterial color={C.navy} metalness={0.5} roughness={0.3} />
          </mesh>
          <mesh castShadow position={[0, 0.38, 0]}>
            <cylinderGeometry args={[0.09, 0.15, 0.38, 40]} />
            <meshStandardMaterial color={C.gold} metalness={1} roughness={0.3} />
          </mesh>
          <mesh castShadow position={[0, 0.66, 0]}>
            <sphereGeometry args={[0.17, 40, 20]} />
            <meshStandardMaterial color={C.gold} metalness={1} roughness={0.25} />
          </mesh>
        </group>
      )}
      {/* poeira dourada */}
      {t >= 0.1 && dustK < 1 &&
        Array.from({ length: 56 }).map((_, k) => {
          const a = rand(k) * Math.PI * 2;
          const r = 0.35 + dustK * (0.5 + rand(k + 9) * 1.1);
          const y = top + 0.05 + Math.sin(dustK * Math.PI) * (0.15 + rand(k + 4) * 0.5);
          const sz = 0.04 + rand(k + 2) * 0.05;
          return (
            <sprite key={k} position={[Math.cos(a) * r, y, STAMP_Z + Math.sin(a) * r * 0.6]} scale={[sz, sz, 1]}>
              <spriteMaterial map={s.glowTex} color={"#F3D9A0"} transparent opacity={(1 - dustK) * 0.95} blending={THREE.AdditiveBlending} depthWrite={false} />
            </sprite>
          );
        })}
    </group>
  );
};

// ---------- partículas ----------
const Particles = ({ t, s }: { t: number; s: Shared }) => {
  const geo = useMemo(() => new THREE.BufferGeometry(), []);
  const N = 420;
  const arr = new Float32Array(N * 3);
  for (let i = 0; i < N; i++) {
    const bx = (rand(i) - 0.5) * 30;
    const by = rand(i + 0.3) * 9;
    const bz = (rand(i + 0.7) - 0.5) * 22 + 3;
    arr[i * 3] = bx + Math.sin(t * 0.3 + i) * 0.4;
    arr[i * 3 + 1] = (by + t * (0.05 + rand(i + 5) * 0.08)) % 9;
    arr[i * 3 + 2] = bz + Math.cos(t * 0.25 + i * 1.7) * 0.4;
  }
  geo.setAttribute("position", new THREE.BufferAttribute(arr, 3));
  return (
    <points geometry={geo}>
      <pointsMaterial
        map={s.glowTex}
        color={"#E6C88C"}
        size={0.07}
        sizeAttenuation
        transparent
        opacity={0.75}
        blending={THREE.AdditiveBlending}
        depthWrite={false}
      />
    </points>
  );
};

// ---------- clarão (tema quente) ----------
const Flare = ({ t, s }: { t: number; s: Shared }) => {
  const k = ramp(t, T.quente - 0.25, T.quente + 0.9, (x) => x);
  if (k <= 0 || k >= 1) return null;
  const x = lerp(-12, 12, k);
  const o = Math.sin(k * Math.PI);
  return (
    <group>
      <sprite position={[x, 3.2, 3]} scale={[9, 9, 1]}>
        <spriteMaterial map={s.glowTex} color={"#FFD892"} transparent opacity={o * 0.6} blending={THREE.AdditiveBlending} depthWrite={false} />
      </sprite>
      <pointLight position={[x, 3, 3]} intensity={o * 22} color={"#FFD18A"} distance={12} />
    </group>
  );
};

export const World = ({ cover }: { cover?: boolean }) => {
  const frame = useCurrentFrame();
  const t = cover ? 3.0 : frame / FPS;
  const s = useShared();
  const flash = Math.max(0, 1 - Math.abs(t - (T.h40 + 0.15)) / 0.5);
  return (
    <>
      <Environment />
      <Rig t={t} cover={cover} />
      <hemisphereLight args={["#3A5488", "#0C1B33", 0.55]} />
      <directionalLight
        position={[6, 11, 9]}
        intensity={2.4 + flash * 1.5}
        color={"#FFE1B0"}
        castShadow
        shadow-mapSize={[2048, 2048]}
        shadow-camera-left={-13}
        shadow-camera-right={13}
        shadow-camera-top={13}
        shadow-camera-bottom={-13}
        shadow-camera-near={1}
        shadow-camera-far={40}
        shadow-bias={-0.0004}
        shadow-radius={6}
      />
      <directionalLight position={[-7, 6, -10]} intensity={2.2} color={"#9DB6E6"} />
      <directionalLight position={[0, 3, 14]} intensity={0.35} color={"#FFFFFF"} />
      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[80, 80]} />
        <meshStandardMaterial map={s.floorMap} roughness={0.26} metalness={0.55} envMapIntensity={0.45} />
      </mesh>
      {DAYS.map((_, i) => (
        <Column key={i} i={i} t={t} s={s} />
      ))}
      <Pediment t={t} />
      <Rail t={t} s={s} />
      {!cover && <Opening t={t} s={s} />}
      <Particles t={t} s={s} />
      {!cover && <Flare t={t} s={s} />}
      {!cover && <HeroProps t={t} glowTex={s.glowTex} marbleMap={s.marbleMap} />}
      {cover && <directionalLight position={[3, 5, -12]} intensity={4} color={"#E8C98E"} />}
      {cover && <spotLight position={[-2, 9, 8]} angle={0.5} penumbra={0.8} intensity={180} color={"#FFE0AA"} castShadow />}
    </>
  );
};
