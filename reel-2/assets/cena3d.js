// Mundo 3D do reel "Plantão HERO" (Three.js r169, determinístico: tudo sai de `t`).
//   calendário de arrancar folhas (SÁBADO → 20, 21, 22, 23 → 24 de OUTUBRO), relógio que gira até 7:30 (19H30),
//   gotas de ouro na "unção", carrossel de fotos reais dos cultos em volta dele ("adoração e comunhão").
// O calendário e o relógio voltam na cartela final.
// Duas passadas por quadro: o que está atrás do plano da pessoa (z < 0) vai para #c3dTras (sob o recorte),
// o resto para #c3dFrente. Câmera fixa em z=14, fov 32 => 239,14 px por unidade no plano z=0.
import * as THREE from "three";
import { RoomEnvironment } from "three/addons/RoomEnvironment.js";
import { RoundedBoxGeometry } from "three/addons/RoundedBoxGeometry.js";

const PX = 239.14, CZ = 14, TAU = Math.PI * 2;
const UZ = (xpx, ypx, z = 0) => new THREE.Vector3(((xpx - 540) / PX) * ((CZ - z) / CZ), ((960 - ypx) / PX) * ((CZ - z) / CZ), z);
const PXU = (z) => PX * (CZ / (CZ - z));             // pixels por unidade na profundidade z
const cl = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const P = (t, a, b) => cl((t - a) / (b - a));
const E = {
  outC: (x) => 1 - Math.pow(1 - x, 3), inC: (x) => x * x * x,
  ioC: (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2),
  outB: (x) => 1 + 2.70158 * Math.pow(x - 1, 3) + 1.70158 * Math.pow(x - 1, 2),
  outE: (x) => (x >= 1 ? 1 : 1 - Math.pow(2, -10 * x)),
  outEl: (x) => (x <= 0 ? 0 : x >= 1 ? 1 : Math.pow(2, -9 * x) * Math.sin((x * 10 - 0.75) * (TAU / 3)) + 1),
};
const lerp = (a, b, u) => a + (b - a) * u;
const mola = (t, t0, amp, freq = 14, dec = 5) => (t < t0 ? 0 : amp * Math.exp(-(t - t0) * dec) * Math.sin((t - t0) * freq));
function rng(seed) {
  return function () {
    seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
    let x = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    x = (x + Math.imul(x ^ (x >>> 7), 61 | x)) ^ x;
    return ((x ^ (x >>> 14)) >>> 0) / 4294967296;
  };
}
const AMARELO = "#f5b800", PRETO = "#0e0d0b", VERMELHO = "#e3262c";
const carregar = (src) => new Promise((ok, erro) => { const im = new Image(); im.onload = () => ok(im); im.onerror = erro; im.src = src; });
function texto(ctx, s, x, y, fonte, cor, alinh = "center", esp = 0) {
  ctx.font = fonte; ctx.fillStyle = cor; ctx.textAlign = alinh; ctx.textBaseline = "alphabetic";
  if (ctx.letterSpacing !== undefined) ctx.letterSpacing = esp + "px";
  ctx.fillText(s, x, y);
  if (ctx.letterSpacing !== undefined) ctx.letterSpacing = "0px";
}
function tex(c, r) { const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = r.capabilities.getMaxAnisotropy(); return t; }

// ------------------------------------------------------------------ artes (canvas)
function folha(n) {
  const c = document.createElement("canvas"); c.width = 600; c.height = 680;
  const x = c.getContext("2d");
  x.fillStyle = "#fbf8f1"; x.fillRect(0, 0, 600, 680);
  x.fillStyle = VERMELHO; x.fillRect(0, 0, 600, 150);
  texto(x, "SÁBADO", 300, 122, '400 118px "Bebas Neue"', "#fff", "center", 10);
  texto(x, String(n), 300, 560, '400 430px "Bebas Neue"', n === 24 ? PRETO : "#2b2a28");
  texto(x, "OUTUBRO", 300, 650, '400 74px "Bebas Neue"', n === 24 ? VERMELHO : "#77736a", "center", 14);
  x.strokeStyle = "rgba(0,0,0,0.08)"; x.lineWidth = 3; x.strokeRect(1.5, 1.5, 597, 677);
  return c;
}
function mostrador(logo) {
  const c = document.createElement("canvas"); c.width = c.height = 1024;
  const x = c.getContext("2d");
  x.fillStyle = "#fbf8f1"; x.beginPath(); x.arc(512, 512, 512, 0, TAU); x.fill();
  x.translate(512, 512);
  for (let i = 0; i < 60; i++) {
    const a = (i / 60) * TAU, grande = i % 5 === 0;
    x.save(); x.rotate(a);
    x.fillStyle = grande ? PRETO : "#9a958a";
    x.fillRect(-(grande ? 9 : 3), -488, grande ? 18 : 6, grande ? 62 : 26);
    x.restore();
  }
  for (let h = 1; h <= 12; h++) {
    const a = (h / 12) * TAU;
    texto(x, String(h), Math.sin(a) * 360, -Math.cos(a) * 360 + 34, '400 104px "Bebas Neue"', h === 7 ? VERMELHO : PRETO);
  }
  const lw = 300, lh = lw * logo.height / logo.width;
  x.drawImage(logo, -lw / 2, 120, lw, lh);
  texto(x, "PLANTÃO", 0, -150, '700 44px "Space Mono"', "#77736a", "center", 8);
  return c;
}
function cartao(img, seed) {
  const c = document.createElement("canvas"); c.width = 560; c.height = 700;
  const x = c.getContext("2d");
  x.fillStyle = "#fbf8f1"; x.fillRect(0, 0, 560, 700);
  const w = 512, h = 600, s = Math.max(w / img.width, h / img.height);
  const sw = w / s, sh = h / s;
  x.drawImage(img, (img.width - sw) / 2, (img.height - sh) / 2 - img.height * 0.04, sw, sh, 24, 24, w, h);
  texto(x, ["ADORAÇÃO", "COMUNHÃO", "IRMÃOS", "LOUVOR", "ORAÇÃO", "FAMÍLIA", "PALAVRA", "HERO"][seed % 8], 280, 676, '400 52px "Bebas Neue"', PRETO, "center", 6);
  return c;
}
function versoCartao() {
  const c = document.createElement("canvas"); c.width = 280; c.height = 350;
  const x = c.getContext("2d");
  x.fillStyle = AMARELO; x.fillRect(0, 0, 280, 350);
  texto(x, "H", 140, 250, '700 230px "UnifrakturCook"', PRETO);
  return c;
}
function pontoSuave() {
  const c = document.createElement("canvas"); c.width = c.height = 64;
  const x = c.getContext("2d");
  const g = x.createRadialGradient(32, 32, 0, 32, 32, 32);
  g.addColorStop(0, "rgba(255,255,255,1)"); g.addColorStop(0.35, "rgba(255,230,150,0.8)"); g.addColorStop(1, "rgba(255,190,40,0)");
  x.fillStyle = g; x.fillRect(0, 0, 64, 64);
  return c;
}

// ------------------------------------------------------------------ montagem
export async function montar(cTras, cFrente, EV) {
  await Promise.all(['400 100px "Bebas Neue"', '700 100px "Space Mono"', '700 100px "UnifrakturCook"'].map((f) => document.fonts.load(f)));
  const logo = await carregar("assets/brand/logo_hero_patrocinio.png");
  const FOTOS = ["p02", "p06", "p11", "p05", "p13", "p12", "p16", "p08"];
  const imgs = await Promise.all(FOTOS.map((p) => carregar("assets/fotos/culto_" + p + ".jpg")));

  const gl = document.createElement("canvas"); gl.width = 1080; gl.height = 1920;
  const renderer = new THREE.WebGLRenderer({ canvas: gl, antialias: true, alpha: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1); renderer.setSize(1080, 1920, false); renderer.setClearColor(0x000000, 0);
  renderer.toneMapping = THREE.NoToneMapping; renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.autoClear = false;
  const ctxT = cTras.getContext("2d"), ctxF = cFrente.getContext("2d");
  const cena = new THREE.Scene();
  cena.environment = new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(), 0.04).texture;
  cena.environmentIntensity = 0.6;
  const cam = new THREE.PerspectiveCamera(32, 1080 / 1920, 0.1, 100); cam.position.set(0, 0, CZ);
  const chave = new THREE.DirectionalLight(0xfff4e2, 1.3); chave.position.set(-3, 5, 9); cena.add(chave);
  const rec = new THREE.DirectionalLight(0xffc040, 0.8); rec.position.set(6, 1, -2); cena.add(rec);
  cena.add(new THREE.AmbientLight(0xffffff, 0.45));
  const papel = (map) => new THREE.MeshStandardMaterial({ map, roughness: 0.75, metalness: 0 });

  // ---------------- calendário de arrancar
  const cal = new THREE.Group();
  const CW = 1.5, CH = 1.7;
  const bloco = new THREE.Mesh(new RoundedBoxGeometry(CW + 0.08, CH + 0.08, 0.32, 3, 0.04), new THREE.MeshStandardMaterial({ color: 0x15130f, roughness: 0.6 }));
  bloco.position.z = -0.17; cal.add(bloco);
  const argola = new THREE.MeshStandardMaterial({ color: 0xd9a514, metalness: 0.9, roughness: 0.25 });
  for (const ax of [-0.45, 0.45]) {
    const a = new THREE.Mesh(new THREE.TorusGeometry(0.1, 0.025, 10, 28), argola);
    a.position.set(ax, CH / 2 + 0.02, 0.02); a.rotation.y = Math.PI / 2; cal.add(a);
  }
  const nums = [20, 21, 22, 23, 24];
  const folhas = nums.map((n, i) => {
    const piv = new THREE.Group(); piv.position.set(0, CH / 2, 0.002 + (nums.length - i) * 0.004);
    const m = new THREE.Mesh(new THREE.PlaneGeometry(CW, CH), papel(tex(folha(n), renderer)));
    m.position.y = -CH / 2; piv.add(m); cal.add(piv);
    return piv;
  });
  cena.add(cal);

  // ---------------- relógio
  const rel = new THREE.Group();
  const caixa = new THREE.Mesh(new THREE.CylinderGeometry(1.0, 1.0, 0.26, 64), new THREE.MeshStandardMaterial({ color: 0x15130f, metalness: 0.4, roughness: 0.35 }));
  caixa.rotation.x = Math.PI / 2; caixa.position.z = -0.14; rel.add(caixa);
  const aro = new THREE.Mesh(new THREE.TorusGeometry(0.96, 0.05, 16, 80), argola); aro.position.z = 0.02; rel.add(aro);
  const face = new THREE.Mesh(new THREE.CircleGeometry(0.92, 64), new THREE.MeshStandardMaterial({ map: tex(mostrador(logo), renderer), roughness: 0.6 }));
  face.position.z = 0.0; rel.add(face);
  const mHora = new THREE.Group(), mMin = new THREE.Group();
  const pont = (comp, larg, cor) => { const m = new THREE.Mesh(new THREE.BoxGeometry(larg, comp, 0.03), new THREE.MeshStandardMaterial({ color: cor, roughness: 0.4, metalness: 0.2 })); m.position.y = comp / 2 - 0.08; return m; };
  mHora.add(pont(0.55, 0.075, 0x0e0d0b)); mHora.position.z = 0.03;
  mMin.add(pont(0.8, 0.05, 0x0e0d0b)); mMin.position.z = 0.05;
  const seg = new THREE.Group(); seg.add(pont(0.82, 0.018, 0xe3262c)); seg.position.z = 0.07;
  const eixo = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.06, 20), argola); eixo.rotation.x = Math.PI / 2; eixo.position.z = 0.08;
  rel.add(mHora, mMin, seg, eixo);
  cena.add(rel);

  // ---------------- gotas de ouro (unção)
  const ouro = new THREE.MeshPhysicalMaterial({ color: 0xf2b21c, emissive: 0x7a4c00, emissiveIntensity: 0.6, metalness: 1, roughness: 0.14, clearcoat: 1, clearcoatRoughness: 0.05 });
  const perfil = [];
  for (let i = 0; i <= 24; i++) { const a = (i / 24) * Math.PI; perfil.push(new THREE.Vector2(Math.sin(a) * (0.5 - 0.42 * Math.pow(1 - i / 24, 3)) * 0.42, -Math.cos(a) * 0.62 + (1 - i / 24) * 0.25)); }
  const gGeo = new THREE.LatheGeometry(perfil, 40);
  const GOTAS = [[300, -1.2, 0.0], [800, -0.9, 0.22], [175, 0.6, 0.48], [915, 0.4, 0.7], [560, -2.4, 0.33]];
  const gotas = GOTAS.map(() => { const m = new THREE.Mesh(gGeo, ouro); cena.add(m); return m; });
  const ondas = GOTAS.map(() => { const m = new THREE.Mesh(new THREE.TorusGeometry(1, 0.02, 8, 90), new THREE.MeshBasicMaterial({ color: 0xe8a200, transparent: true, depthWrite: false, toneMapped: false })); m.rotation.x = Math.PI / 2 - 0.25; cena.add(m); return m; });
  const NB = 260, rb = rng(9), bPos = new Float32Array(NB * 3), bDat = [];
  for (let i = 0; i < NB; i++) bDat.push([rb() * 10 - 5, rb() * 9 - 1, rb() * 6 - 4, 0.6 + rb() * 1.2, rb() * TAU]);
  const bGeo = new THREE.BufferGeometry(); bGeo.setAttribute("position", new THREE.BufferAttribute(bPos, 3));
  const bMat = new THREE.PointsMaterial({ size: 0.1, map: new THREE.CanvasTexture(pontoSuave()), transparent: true, depthWrite: false, color: 0xe8a200 });
  const brilhos = new THREE.Points(bGeo, bMat); brilhos.frustumCulled = false; cena.add(brilhos);

  // ---------------- carrossel de fotos
  const vTex = tex(versoCartao(), renderer);
  const cartoes = imgs.map((im, i) => {
    const g = new THREE.Group();
    const f = new THREE.Mesh(new THREE.PlaneGeometry(1.12, 1.4), papel(tex(cartao(im, i), renderer)));
    const v = new THREE.Mesh(new THREE.PlaneGeometry(1.12, 1.4), papel(vTex)); v.rotation.y = Math.PI;
    g.add(f, v); cena.add(g); return g;
  });

  // ------------------------------------------------------------------ coreografia
  const T = {
    calIn: EV.sabado - 0.2, calSai: EV.sera + 0.35,
    relIn: EV.as7 - 0.3, relSai: EV.sera + 0.45,
    fimIn: EV.cartela + 0.35,
    unc: EV.uncao - 0.08, uncFim: EV.seg[6],
    car: EV.momento3 - 0.35, carSai: EV.irmaos2 + 0.25, carFora: EV.seg[7] - 0.02,
  };
  const pCal = UZ(195, 640, 0.8), pRel = UZ(885, 640, 0.8);
  const sObj = 300 / (CW * PXU(0.8)), sRel = 300 / (2 * PXU(0.8));
  const pCalFim = UZ(270, 1030, 1.0), pRelFim = UZ(810, 1030, 1.0);
  const sCalFim = 330 / (CW * PXU(1.0)), sRelFim = 330 / (2 * PXU(1.0));
  const cab = UZ(540, 700, 0);

  function atualiza(t) {
    // ---------- calendário
    const fim = t >= T.fimIn;
    cal.visible = (t >= T.calIn && t < T.calSai + 0.4) || fim;
    if (cal.visible) {
      if (!fim) {
        const u = E.outB(P(t, T.calIn, T.calIn + 0.45)), s = P(t, T.calSai, T.calSai + 0.4);
        cal.position.copy(UZ(-260, 400, 0.8).lerp(pCal, u)).add(new THREE.Vector3(-s * 4, s * 1.5, 0));
        cal.scale.setScalar(sObj * (1 + mola(t, EV.dia24, 0.08, 22, 6)));
        cal.rotation.set(0.12 + Math.sin(t * 1.3) * 0.03, lerp(-1.2, 0.32, u) + s * 1.5, lerp(-0.5, 0.08, u));
      } else {
        const u = E.outB(P(t, T.fimIn, T.fimIn + 0.55));
        cal.position.copy(UZ(-300, 1300, 1).lerp(pCalFim, u)); cal.scale.setScalar(sCalFim);
        cal.rotation.set(0.08, lerp(-1.4, 0.28, u) + Math.sin(t * 1.1) * 0.05, lerp(-0.4, 0.06, u));
      }
      // folhas 20..23 arrancadas entre "dia" e "24" (no fim: já no 24)
      const tf0 = EV.dia - 0.08, tf1 = EV.dia24 - 0.02;
      folhas.forEach((f, i) => {
        if (i === 4) { f.visible = true; return; }
        const t0 = lerp(tf0, tf1, i / 4), u = fim ? 1 : P(t, t0, t0 + 0.32);
        f.visible = u < 1 && t >= T.calIn - 0.01;
        f.rotation.x = -E.inC(u) * 2.4; f.position.y = CH / 2 + E.inC(u) * 1.6; f.position.x = Math.sin(u * 3 + i) * u * 0.8;
      });
    }
    // ---------- relógio
    rel.visible = (t >= T.relIn && t < T.relSai + 0.4) || fim;
    if (rel.visible) {
      let ang;
      if (!fim) {
        const u = E.outB(P(t, T.relIn, T.relIn + 0.4)), s = P(t, T.relSai, T.relSai + 0.4);
        rel.position.copy(UZ(1340, 400, 0.8).lerp(pRel, u)).add(new THREE.Vector3(s * 4, s * 1.5, 0));
        rel.scale.setScalar(sRel * (1 + mola(t, EV.meia + 0.15, 0.07, 22, 6)));
        rel.rotation.set(0.1 + Math.sin(t * 1.2) * 0.03, lerp(1.2, -0.3, u) - s * 1.5, lerp(0.5, -0.06, u));
        ang = E.outEl(P(t, EV.as7 - 0.1, EV.meia + 0.25));
      } else {
        const u = E.outB(P(t, T.fimIn + 0.12, T.fimIn + 0.67));
        rel.position.copy(UZ(1380, 1300, 1).lerp(pRelFim, u)); rel.scale.setScalar(sRelFim);
        rel.rotation.set(0.06, lerp(1.4, -0.26, u) + Math.sin(t * 1.0) * 0.05, lerp(0.4, -0.05, u));
        ang = 1;
      }
      // 7:30 -> minuto 180°, hora entre 7 e 8 (225°); vêm do 12:00 dando voltas
      mMin.rotation.z = -lerp(0, TAU * 2 + Math.PI, ang);
      mHora.rotation.z = -lerp(0, TAU * 7.5 / 12, ang);
      seg.rotation.z = -t * TAU / 4;
    }
    // ---------- gotas de ouro
    const vu = t >= T.unc - 0.1 && t < T.uncFim + 0.3;
    GOTAS.forEach(([xp, z, atraso], i) => {
      const g = gotas[i], o = ondas[i];
      const dt = t - T.unc - atraso;
      const yChao = 1300, dur = 0.95;
      g.visible = vu && dt > 0 && dt < dur;
      if (g.visible) {
        const u = dt / dur;
        const p = UZ(xp, lerp(-150, yChao, u * u), z);
        g.position.copy(p); const s = 1.5 + 0.5 * u; g.scale.set(s, s * (1 + 0.5 * u), s);
        g.rotation.y = t * 2;
      }
      const du = dt - dur;
      o.visible = vu && du > 0 && du < 0.9;
      if (o.visible) { o.position.copy(UZ(xp, yChao + 40, z)); o.scale.setScalar(lerp(0.1, 2.0, E.outC(du / 0.9))); o.material.opacity = 1 - du / 0.9; }
    });
    brilhos.visible = vu;
    if (vu) {
      const a = P(t, T.unc - 0.1, T.unc + 0.3) * (1 - P(t, T.uncFim - 0.2, T.uncFim + 0.3));
      bDat.forEach(([x0, y0, z, v, f], i) => {
        const y = ((y0 - (t - T.unc) * v * 0.9) % 9 + 9) % 9 - 4.5;
        bPos[i * 3] = x0 + Math.sin(t * 1.3 + f) * 0.25; bPos[i * 3 + 1] = y + 2; bPos[i * 3 + 2] = z;
      });
      bGeo.attributes.position.needsUpdate = true; bMat.opacity = a * 0.9;
    }
    // ---------- carrossel
    const vc = t >= T.car && t < T.carFora;
    cartoes.forEach((g, i) => {
      g.visible = vc;
      if (!vc) return;
      const ent = E.outC(P(t, T.car + i * 0.04, T.car + 0.6 + i * 0.04));
      const sai = E.inC(P(t, T.carSai, T.carFora));
      const abre = E.ioC(P(t, EV.comunhao - 0.15, EV.comunhao + 0.45));
      const raio = lerp(7, lerp(2.1, 2.4, abre), ent) + sai * 3;
      const ang = (i / cartoes.length) * TAU + lerp(-2.2, 0, ent) + (t - T.car) * 0.75 + sai * 2;
      // órbita inclinada: a parte da frente passa baixa (peito), a de trás alta (atrás da cabeça)
      const x = Math.sin(ang) * raio, zz = Math.cos(ang) * raio;
      g.position.set(cab.x + x, cab.y - 0.1 - zz * 0.62 + Math.sin(t * 2 + i) * 0.05, zz * 0.8 + sai * 6);
      g.rotation.set(0.12, Math.sin(ang) * 0.55, Math.sin(i * 1.7) * 0.1);   // sempre de frente para a câmera (as fotos aparecem também atrás dele)
      // na frente do rosto o cartão "atravessa": encolhe e reaparece do outro lado
      const frente = 1 - E.ioC(cl((Math.cos(ang) - 0.5) / 0.3)) * (1 - sai);
      g.scale.setScalar(0.95 * frente * lerp(0.6, 1, ent) * (1 + mola(t, i % 2 ? EV.adoracao : EV.comunhao, 0.06, 18, 6)));
      g.visible = frente > 0.02;
    });
  }

  const objs = [cal, rel, ...gotas, ...ondas, brilhos, ...cartoes];
  const tras = (o) => (o === brilhos ? false : o.position.z < -0.05);
  function passada(ctx, querTras) {
    const vis = objs.map((o) => o.visible);
    let algum = false;
    objs.forEach((o, i) => { o.visible = vis[i] && tras(o) === querTras; algum = algum || o.visible; });
    ctx.clearRect(0, 0, 1080, 1920);
    if (algum) { renderer.clear(); renderer.render(cena, cam); ctx.drawImage(gl, 0, 0); }
    objs.forEach((o, i) => (o.visible = vis[i]));
  }
  return {
    render(t, abalo = [0, 0]) {
      atualiza(t);
      cam.position.set(abalo[0], abalo[1], CZ);
      passada(ctxT, true);
      passada(ctxF, false);
    },
  };
}
