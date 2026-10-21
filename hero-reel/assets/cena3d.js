// Mundo 3D do reel "Convite HERO — Deus tem um encontro com você" (Three.js r169, determinístico: tudo sai de `t`).
// Fio condutor: um INGRESSO de papel-cartão. Nasce no "convite", gira em volta da cabeça (passa ATRÁS dele e volta
// pela frente), recebe o carimbo "24 OUT · 19H30", conta "ADMITE 1 → 2 → 3" no "traga um amigo / um parente",
// volta pelo verso "CONVIDADO ESPECIAL · VOCÊ" e pousa na cartela final.
// Também: mar de partículas douradas (Galileia) e anéis de onda ("grandemente").
// Duas passadas por quadro: o que está atrás do plano da pessoa (z < 0) vai para #c3dTras (sob o recorte da pessoa),
// o resto para #c3dFrente (sobre ela). Câmera fixa em z=14, fov 32 => 239,14 px por unidade no plano z=0.
import * as THREE from "three";
import { RoomEnvironment } from "three/addons/RoomEnvironment.js";

const PX = 239.14, CZ = 14;
const TAU = Math.PI * 2;
// posição no mundo para um ponto da tela (px) a uma profundidade z
const UZ = (xpx, ypx, z = 0) => new THREE.Vector3(((xpx - 540) / PX) * ((CZ - z) / CZ), ((960 - ypx) / PX) * ((CZ - z) / CZ), z);
// escala para o ingresso (3,4 u de largura) ocupar `wpx` na tela a uma profundidade z
const ESC = (wpx, z = 0) => wpx / (3.4 * PX * (CZ / (CZ - z)));

const cl = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const P = (t, a, b) => cl((t - a) / (b - a));
const E = {
  lin: (x) => x,
  outC: (x) => 1 - Math.pow(1 - x, 3),
  inC: (x) => x * x * x,
  ioC: (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2),
  outE: (x) => (x >= 1 ? 1 : 1 - Math.pow(2, -10 * x)),
  inE: (x) => (x <= 0 ? 0 : Math.pow(2, 10 * x - 10)),
  outB: (x) => 1 + 2.70158 * Math.pow(x - 1, 3) + 1.70158 * Math.pow(x - 1, 2),
  ioS: (x) => x * x * x * (x * (6 * x - 15) + 10),
};
const lerp = (a, b, u) => a + (b - a) * u;
// chaves [[t, valor, easing do trecho que termina nessa chave], ...] — valor número ou array
function K(t, ks) {
  if (t <= ks[0][0]) return ks[0][1];
  for (let i = 1; i < ks.length; i++) {
    if (t <= ks[i][0]) {
      const [t0, v0] = ks[i - 1], [t1, v1, e] = ks[i];
      const u = E[e || "ioC"]((t - t0) / (t1 - t0));
      return Array.isArray(v0) ? v0.map((a, j) => a + (v1[j] - a) * u) : v0 + (v1 - v0) * u;
    }
  }
  return ks[ks.length - 1][1];
}
const mola = (t, t0, amp, freq = 14, dec = 5) => (t < t0 ? 0 : amp * Math.exp(-(t - t0) * dec) * Math.sin((t - t0) * freq));
function rng(seed) {
  return function () {
    seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
    let x = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    x = (x + Math.imul(x ^ (x >>> 7), 61 | x)) ^ x;
    return ((x ^ (x >>> 14)) >>> 0) / 4294967296;
  };
}

const AMARELO = "#f5b800", PRETO = "#0e0d0b";

function carregar(src) {
  return new Promise((ok, erro) => { const im = new Image(); im.onload = () => ok(im); im.onerror = erro; im.src = src; });
}

// ------------------------------------------------------------------ texturas do ingresso (canvas 2D)
const TW = 2048, TH = 904, CORTE = 0.762;            // picote a 76,2% da largura (frente)
function grao(ctx, w, h, seed, a = 0.07) {
  const r = rng(seed);
  for (let i = 0; i < 2600; i++) {
    ctx.globalAlpha = a * r();
    ctx.fillStyle = r() > 0.5 ? "#fff" : "#000";
    const s = 1 + r() * 3;
    ctx.fillRect(r() * w, r() * h, s, s);
  }
  ctx.globalAlpha = 1;
}
function picote(ctx, x, cor) {
  ctx.fillStyle = cor;
  for (let y = 40; y < TH - 30; y += 34) ctx.fillRect(x - 3, y, 6, 16);
}
function texto(ctx, s, x, y, fonte, cor, esp = 0, alinh = "left") {
  ctx.font = fonte; ctx.fillStyle = cor; ctx.textAlign = alinh; ctx.textBaseline = "alphabetic";
  if (ctx.letterSpacing !== undefined) ctx.letterSpacing = esp + "px";
  ctx.fillText(s, x, y);
  if (ctx.letterSpacing !== undefined) ctx.letterSpacing = "0px";
}

function frente(logoHero) {
  const c = document.createElement("canvas"); c.width = TW; c.height = TH;
  const x = c.getContext("2d");
  const xc = TW * CORTE;
  x.fillStyle = PRETO; x.fillRect(0, 0, TW, TH);
  const g = x.createRadialGradient(TW * 0.35, TH * 0.3, 50, TW * 0.35, TH * 0.4, TW * 0.6);
  g.addColorStop(0, "#2a2414"); g.addColorStop(1, "rgba(0,0,0,0)");
  x.fillStyle = g; x.fillRect(0, 0, xc, TH);
  grao(x, xc, TH, 11);
  x.strokeStyle = AMARELO; x.lineWidth = 5; x.strokeRect(30, 30, xc - 60, TH - 60);
  x.lineWidth = 2; x.strokeRect(44, 44, xc - 88, TH - 88);
  texto(x, "CONVITE", 92, 238, '400 172px "Anton"', AMARELO, 10);
  texto(x, "IGREJA BATISTA DA LAGOINHA · PATROCÍNIO/MG", 98, 302, '700 36px "Barlow Condensed"', "rgba(255,255,255,0.78)", 5);
  const lw = 560, lh = lw * logoHero.height / logoHero.width;
  x.drawImage(logoHero, xc - lw - 70, 88, lw, lh);
  texto(x, "DEUS TEM UM ENCONTRO", 92, 478, 'italic 800 104px "Barlow Condensed"', "#ffffff", 1);
  texto(x, "COM VOCÊ.", 92, 572, 'italic 800 104px "Barlow Condensed"', AMARELO, 1);
  // campos
  x.fillStyle = "rgba(245,184,0,0.9)"; x.fillRect(92, 640, xc - 184, 3);
  texto(x, "DATA", 98, 700, '700 34px "Barlow Condensed"', AMARELO, 6);
  texto(x, "HORA", 470, 700, '700 34px "Barlow Condensed"', AMARELO, 6);
  texto(x, "LOCAL", 800, 700, '700 34px "Barlow Condensed"', AMARELO, 6);
  texto(x, "__ / __", 98, 790, '800 62px "Barlow Condensed"', "rgba(255,255,255,0.35)", 4);
  texto(x, "__ : __", 470, 790, '800 62px "Barlow Condensed"', "rgba(255,255,255,0.35)", 4);
  texto(x, "AV. FARIA PEREIRA, 3083", 800, 790, '800 60px "Barlow Condensed"', "#ffffff", 1);
  // canhoto
  x.fillStyle = AMARELO; x.fillRect(xc, 0, TW - xc, TH);
  grao(x, TW, TH, 12, 0.05);
  picote(x, xc, PRETO);
  texto(x, "ADMITE", xc + (TW - xc) / 2, 172, '800 78px "Barlow Condensed"', PRETO, 10, "center");
  texto(x, "Nº 0024", xc + (TW - xc) / 2, 812, '700 50px "Barlow Condensed"', PRETO, 6, "center");
  x.fillStyle = PRETO; x.fillRect(xc + 60, 205, TW - xc - 120, 4); x.fillRect(xc + 60, 735, TW - xc - 120, 4);
  return c;
}

function verso(logoHero) {
  // visto por trás: o canhoto fica à ESQUERDA
  const c = document.createElement("canvas"); c.width = TW; c.height = TH;
  const x = c.getContext("2d");
  const xc = TW * (1 - CORTE);
  x.fillStyle = AMARELO; x.fillRect(0, 0, TW, TH);
  grao(x, TW, TH, 21, 0.06);
  x.strokeStyle = PRETO; x.lineWidth = 5; x.strokeRect(xc + 30, 30, TW - xc - 60, TH - 60);
  texto(x, "CONVIDADO", xc + 92, 300, '400 236px "Anton"', PRETO, 6);
  texto(x, "Especial", xc + 98, 520, '700 200px "UnifrakturCook"', PRETO, 2);
  texto(x, "NOME", xc + 98, 690, '700 40px "Barlow Condensed"', PRETO, 8);
  texto(x, "VOCÊ", xc + 250, 800, 'italic 800 170px "Barlow Condensed"', PRETO, 4);
  x.fillStyle = PRETO; x.fillRect(xc + 240, 822, 760, 6);
  const lw = 470, lh = lw * logoHero.height / logoHero.width;
  x.drawImage(logoHero, TW - lw - 80, TH - lh - 70, lw, lh);
  // canhoto preto
  x.fillStyle = PRETO; x.fillRect(0, 0, xc, TH);
  grao(x, xc, TH, 22, 0.08);
  picote(x, xc, AMARELO);
  texto(x, "ADMITE", xc / 2, 230, '800 70px "Barlow Condensed"', "rgba(255,255,255,0.8)", 10, "center");
  texto(x, "VOCÊ", xc / 2, 470, '400 150px "Anton"', AMARELO, 4, "center");
  texto(x, "+2", xc / 2, 690, '400 170px "Anton"', AMARELO, 4, "center");
  return c;
}

function digito(n) {
  const c = document.createElement("canvas"); c.width = 300; c.height = 380;
  const x = c.getContext("2d");
  x.fillStyle = AMARELO; x.fillRect(0, 0, 300, 380);
  grao(x, 300, 380, 30 + n, 0.05);
  texto(x, String(n), 150, 340, '400 380px "Anton"', PRETO, 0, "center");
  return c;
}

function carimbo() {
  const c = document.createElement("canvas"); c.width = 1100; c.height = 520;
  const x = c.getContext("2d");
  x.translate(550, 260); x.rotate(-0.11);
  x.strokeStyle = AMARELO; x.fillStyle = AMARELO;
  x.lineWidth = 14; x.beginPath(); x.roundRect(-500, -205, 1000, 410, 40); x.stroke();
  x.lineWidth = 5; x.beginPath(); x.roundRect(-470, -177, 940, 354, 28); x.stroke();
  texto(x, "24 OUT", -20, 70, '400 230px "Anton"', AMARELO, 8, "center");
  texto(x, "SÁBADO · 19H30", 0, 150, '800 64px "Barlow Condensed"', AMARELO, 12, "center");
  texto(x, "CULTO HERO", 0, -110, '800 52px "Barlow Condensed"', AMARELO, 18, "center");
  // tinta falhada (determinística)
  x.setTransform(1, 0, 0, 1, 0, 0);
  x.globalCompositeOperation = "destination-out";
  const r = rng(77);
  for (let i = 0; i < 900; i++) { x.globalAlpha = 0.25 + r() * 0.6; x.beginPath(); x.arc(r() * 1100, r() * 520, 1 + r() * 7, 0, TAU); x.fill(); }
  x.globalAlpha = 1; x.globalCompositeOperation = "source-over";
  return c;
}

function pontoSuave() {
  const c = document.createElement("canvas"); c.width = c.height = 64;
  const x = c.getContext("2d");
  const g = x.createRadialGradient(32, 32, 0, 32, 32, 32);
  g.addColorStop(0, "rgba(255,255,255,1)"); g.addColorStop(0.35, "rgba(255,235,170,0.8)"); g.addColorStop(1, "rgba(255,200,60,0)");
  x.fillStyle = g; x.fillRect(0, 0, 64, 64);
  return c;
}

function tex(canvas, renderer) {
  const t = new THREE.CanvasTexture(canvas);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = renderer.capabilities.getMaxAnisotropy();
  return t;
}

// ------------------------------------------------------------------ geometria do ingresso (cantos + meias-luas do picote)
const WT = 3.4, HT = 1.5;
function formaIngresso() {
  const s = new THREE.Shape(), r = 0.07, nr = 0.11, xn = WT * CORTE - WT / 2;
  const x0 = -WT / 2, x1 = WT / 2, y0 = -HT / 2, y1 = HT / 2;
  s.moveTo(x0 + r, y0);
  s.lineTo(xn - nr, y0); s.absarc(xn, y0, nr, Math.PI, 0, true);
  s.lineTo(x1 - r, y0); s.quadraticCurveTo(x1, y0, x1, y0 + r);
  s.lineTo(x1, y1 - r); s.quadraticCurveTo(x1, y1, x1 - r, y1);
  s.lineTo(xn + nr, y1); s.absarc(xn, y1, nr, 0, Math.PI, true);
  s.lineTo(x0 + r, y1); s.quadraticCurveTo(x0, y1, x0, y1 - r);
  s.lineTo(x0, y0 + r); s.quadraticCurveTo(x0, y0, x0 + r, y0);
  return s;
}
function uvPlano(geo, espelha) {
  const p = geo.attributes.position, uv = geo.attributes.uv;
  for (let i = 0; i < p.count; i++) {
    const u = (p.getX(i) + WT / 2) / WT;
    uv.setXY(i, espelha ? 1 - u : u, (p.getY(i) + HT / 2) / HT);
  }
  uv.needsUpdate = true;
  return geo;
}

function brilhoMat() {
  return new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    uniforms: { pos: { value: -1 }, forca: { value: 0 } },
    vertexShader: "varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }",
    fragmentShader: "uniform float pos; uniform float forca; varying vec2 vUv;" +
      "void main(){ float d = (vUv.x + (vUv.y - 0.5) * 0.55) - pos; float a = exp(-d*d/0.0035) * forca + exp(-d*d/0.03) * forca * 0.25;" +
      " gl_FragColor = vec4(vec3(1.0, 0.93, 0.7) * a, a); }",
  });
}

function fazIngresso(texF, texV, renderer, comBrilho) {
  const forma = formaIngresso();
  const g = new THREE.Group();
  const prof = 0.035;
  const borda = new THREE.Mesh(new THREE.ExtrudeGeometry(forma, { depth: prof, bevelEnabled: false, curveSegments: 18 }),
    new THREE.MeshStandardMaterial({ color: 0xc99a1a, metalness: 0.85, roughness: 0.32 }));
  borda.position.z = -prof / 2;
  g.add(borda);
  const papel = (map) => new THREE.MeshPhysicalMaterial({ map, roughness: 0.5, metalness: 0.0, clearcoat: 0.55, clearcoatRoughness: 0.25 });
  const f = new THREE.Mesh(uvPlano(new THREE.ShapeGeometry(forma, 18), false), papel(texF));
  f.position.z = prof / 2 + 0.001;
  g.add(f);
  const v = new THREE.Mesh(uvPlano(new THREE.ShapeGeometry(forma, 18), false), papel(texV));
  v.rotation.y = Math.PI; v.position.z = -prof / 2 - 0.001;
  g.add(v);
  let brilho = null;
  if (comBrilho) {
    brilho = new THREE.Mesh(uvPlano(new THREE.ShapeGeometry(forma, 18), false), brilhoMat());
    brilho.position.z = prof / 2 + 0.004;
    g.add(brilho);
  }
  return { g, f, v, brilho };
}

// ------------------------------------------------------------------ montagem
export async function montar(cTras, cFrente, EV) {
  await Promise.all([
    document.fonts.load('400 100px "Anton"'), document.fonts.load('800 100px "Barlow Condensed"'),
    document.fonts.load('italic 800 100px "Barlow Condensed"'), document.fonts.load('700 100px "Barlow Condensed"'),
    document.fonts.load('700 100px "UnifrakturCook"'),
  ]);
  const logoHero = await carregar("assets/brand/logo_hero_patrocinio.png");

  const gl = document.createElement("canvas"); gl.width = 1080; gl.height = 1920;
  const renderer = new THREE.WebGLRenderer({ canvas: gl, antialias: true, alpha: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1);
  renderer.setSize(1080, 1920, false);
  renderer.setClearColor(0x000000, 0);
  renderer.toneMapping = THREE.NoToneMapping;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  const ctxT = cTras.getContext("2d"), ctxF = cFrente.getContext("2d");

  const cena = new THREE.Scene();
  const pm = new THREE.PMREMGenerator(renderer);
  cena.environment = pm.fromScene(new RoomEnvironment(), 0.04).texture;
  cena.environmentIntensity = 0.55;
  const cam = new THREE.PerspectiveCamera(32, 1080 / 1920, 0.1, 100);
  cam.position.set(0, 0, CZ);
  const chave = new THREE.DirectionalLight(0xfff1d6, 1.25); chave.position.set(3, 4, 9); cena.add(chave);
  const recorte = new THREE.DirectionalLight(0xffb020, 0.9); recorte.position.set(-6, 2, -3); cena.add(recorte);
  cena.add(new THREE.AmbientLight(0xffffff, 0.42));

  // ---------------- ingressos
  const texF = tex(frente(logoHero), renderer), texV = tex(verso(logoHero), renderer);
  const ing = fazIngresso(texF, texV, renderer, true);
  const copias = [fazIngresso(texF, texV, renderer, false), fazIngresso(texF, texV, renderer, false)];
  const leque = new THREE.Group();                     // pivô no canto inferior esquerdo, para abrir em leque
  copias.forEach((c) => { c.g.position.set(WT / 2, HT / 2, 0); const p = new THREE.Group(); p.add(c.g); leque.add(p); });
  const raiz = new THREE.Group();
  const pivoLeque = new THREE.Group(); pivoLeque.position.set(-WT / 2, -HT / 2, 0); pivoLeque.add(leque);
  raiz.add(pivoLeque); raiz.add(ing.g); cena.add(raiz);

  const digs = [1, 2, 3].map((n) => tex(digito(n), renderer));
  const dig = new THREE.Mesh(new THREE.PlaneGeometry(0.42, 0.532), new THREE.MeshBasicMaterial({ map: digs[0], toneMapped: false }));
  dig.position.set(WT * CORTE - WT / 2 + (WT * (1 - CORTE)) / 2, -0.015, 0.0195);
  ing.g.add(dig);
  const selo = new THREE.Mesh(new THREE.PlaneGeometry(1.25, 0.591), new THREE.MeshBasicMaterial({ map: tex(carimbo(), renderer), transparent: true, depthWrite: false, toneMapped: false }));
  selo.position.set(-0.86, -0.43, 0.024);
  ing.g.add(selo);

  // ---------------- faíscas douradas (frente)
  const NF = 160, rf = rng(5);
  const fz = new Float32Array(NF * 3), fv = [];
  for (let i = 0; i < NF; i++) {
    const a = rf() * TAU, el = (rf() - 0.5) * 1.4, sp = 0.9 + rf() * 2.6;
    fv.push([Math.cos(a) * Math.cos(el) * sp, Math.sin(el) * sp + 0.6, Math.sin(a) * Math.cos(el) * sp * 0.6, 0.35 + rf() * 0.8]);
  }
  const fGeo = new THREE.BufferGeometry(); fGeo.setAttribute("position", new THREE.BufferAttribute(fz, 3));
  const fMat = new THREE.PointsMaterial({ size: 0.075, map: new THREE.CanvasTexture(pontoSuave()), transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, color: 0xffd25a });
  const faiscas = new THREE.Points(fGeo, fMat); cena.add(faiscas);

  // ---------------- mar da Galileia (atrás): superfície de partículas vista de cima, com câmera própria
  const GX = 210, GZ = 96, NM = GX * GZ;
  const mPos = new Float32Array(NM * 3), mCor = new Float32Array(NM * 3);
  const base = [];
  for (let j = 0; j < GZ; j++) for (let i = 0; i < GX; i++) {
    const rj = rng(j * 1000 + i);
    base.push([-18 + (36 * i) / (GX - 1) + (rj() - 0.5) * 0.08, 5 - 50 * Math.pow(j / (GZ - 1), 1.15), 1 - 0.7 * (j / (GZ - 1))]);
  }
  const mGeo = new THREE.BufferGeometry();
  mGeo.setAttribute("position", new THREE.BufferAttribute(mPos, 3));
  mGeo.setAttribute("color", new THREE.BufferAttribute(mCor, 3));
  const mMat = new THREE.PointsMaterial({ size: 0.13, map: new THREE.CanvasTexture(pontoSuave()), vertexColors: true, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending });
  const mar = new THREE.Points(mGeo, mMat); mar.frustumCulled = false; cena.add(mar);
  const camMar = new THREE.PerspectiveCamera(50, 1080 / 1920, 0.1, 200);
  camMar.position.set(0, 2.4, 9);
  camMar.lookAt(0, 2.4 - 28 * Math.tan((11 * Math.PI) / 180), -19);

  // ---------------- anéis de onda (atrás)
  const aneis = [];
  for (let i = 0; i < 5; i++) {
    const m = new THREE.Mesh(new THREE.TorusGeometry(1, 0.014, 8, 160), new THREE.MeshBasicMaterial({ color: 0xffc83a, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, toneMapped: false }));
    cena.add(m); aneis.push(m);
  }

  // ------------------------------------------------------------------ coreografia
  const T = {
    entra: EV.convite - 0.22, pousa: EV.convite + 0.95,
    centro24: EV.dia24 - 0.42, bate: EV.dia24 + 0.02,
    lado: EV.lagoinha - 0.35,
    traga: EV.traga1 - 0.1, amigo: EV.amigo + 0.04, parente: EV.parente + 0.04,
    sai: EV.adorar - 0.32, fora: EV.adorar + 0.75,
    vip: EV.convidado - 0.45, vipSai: EV.split - 0.22, vipFora: EV.split + 0.25,
    fin: EV.junto - 0.05, fim: EV.cartela + 0.55,
  };
  // trajetória de entrada: de trás (alto à direita) -> atrás da cabeça -> lado esquerdo -> frente -> pouso
  const p0 = UZ(1040, 160, -7), p1 = UZ(610, 470, -2.6), p2 = UZ(80, 560, -0.2), p3 = UZ(300, 980, 2.4);
  const pRepouso = UZ(812, 1105, 2.0);
  const curva = new THREE.CatmullRomCurve3([p0, p1, p2, p3, pRepouso], false, "centripetal");
  const sRepouso = ESC(430, 2.0);

  const pCentro = UZ(540, 1000, 3.0), sCentro = ESC(740, 3.0);
  const pLado = UZ(250, 1150, 2.2), sLado = ESC(380, 2.2);
  const pTraga = UZ(540, 1110, 2.5), sTraga = ESC(640, 2.5);
  const pVip = UZ(540, 1050, 3.2), sVip = ESC(900, 3.2);
  const pFim = UZ(540, 1010, 1.0), sFim = ESC(860, 1.0);

  const v = new THREE.Vector3();
  function poseIngresso(t) {
    // retorna {vis, pos, s, rx, ry, rz}
    if (t < T.entra || (t > T.fora && t < T.vip) || (t > T.vipFora && t < T.fin)) return null;
    let pos, s, rx = 0, ry = 0, rz = 0;
    const bob = Math.sin(t * 2.1) * 0.045, sway = Math.sin(t * 1.3) * 0.08;
    if (t < T.pousa) {
      const u = E.ioC(P(t, T.entra, T.pousa));
      pos = curva.getPoint(u);
      s = lerp(ESC(260, -7), sRepouso, E.outC(u));
      ry = lerp(-TAU * 1.25, -0.32, E.outC(u));
      rx = lerp(0.5, 0.1, u); rz = lerp(0.6, -0.12, u);
    } else if (t < T.centro24) {
      pos = pRepouso.clone(); pos.y += bob; s = sRepouso; ry = -0.32 + sway; rx = 0.1; rz = -0.12;
    } else if (t < T.lado) {
      const u = E.outB(P(t, T.centro24, T.centro24 + 0.38));
      pos = pRepouso.clone().lerp(pCentro, u); s = lerp(sRepouso, sCentro, u);
      ry = lerp(-0.32, 0.08 * Math.sin(t * 1.1), u); rx = lerp(0.1, -0.06, u); rz = lerp(-0.12, 0.02, u);
      const imp = mola(t, T.bate, 0.07, 26, 7);
      s *= 1 - Math.abs(imp) * 0.6; rx += imp;
      pos.y += bob * 0.5;
    } else if (t < T.traga) {
      const u = E.ioC(P(t, T.lado, T.lado + 0.45));
      pos = pCentro.clone().lerp(pLado, u); s = lerp(sCentro, sLado, u);
      ry = lerp(0, 0.38, u) + sway * u; rx = lerp(-0.06, 0.12, u); rz = lerp(0.02, 0.1, u); pos.y += bob * u;
    } else if (t < T.sai) {
      const u = E.outC(P(t, T.traga, T.traga + 0.42));
      pos = pLado.clone().lerp(pTraga, u); s = lerp(sLado, sTraga, u);
      ry = lerp(0.38, 0.05 * Math.sin(t * 1.4), u); rx = lerp(0.12, -0.04, u); rz = lerp(0.1, 0.0, u); pos.y += bob * 0.6;
      rz += mola(t, T.amigo, 0.05, 20, 6) + mola(t, T.parente, 0.05, 20, 6);
    } else if (t <= T.fora) {
      // os ingressos sobem girando em volta dele e somem por trás
      const u = E.ioC(P(t, T.sai, T.fora));
      const ang = lerp(0, TAU * 0.9, u);
      const r = lerp(0, 2.6, Math.sqrt(u));
      pos = new THREE.Vector3(pTraga.x + Math.sin(ang) * r, lerp(pTraga.y, 6.5, u), lerp(pTraga.z, -4, Math.sin(Math.min(1, u * 1.3) * Math.PI / 2)) + Math.cos(ang) * r * 0.3);
      s = lerp(sTraga, sTraga * 0.6, u); ry = lerp(0, TAU, u); rx = lerp(-0.04, -0.6, u); rz = lerp(0, 0.4, u);
    } else if (t <= T.vipFora) {
      if (t < T.vip + 0.62) {
        const u = E.outB(P(t, T.vip, T.vip + 0.62));
        pos = UZ(540, 2400, 2.5).lerp(pVip, u); s = lerp(sVip * 0.7, sVip, u);
        rx = lerp(-1.4, -0.05, u); ry = lerp(Math.PI - 0.9, Math.PI + 0.12, u); rz = lerp(-0.3, 0.02, u);
      } else if (t < T.vipSai) {
        pos = pVip.clone(); pos.y += bob * 0.8; s = sVip;
        ry = Math.PI + 0.12 + Math.sin((t - T.vip) * 1.2) * 0.16; rx = -0.05 + Math.sin(t * 1.7) * 0.03; rz = 0.02;
        s *= 1 + mola(t, EV.especial2, 0.05, 18, 6);
      } else {
        const u = E.inC(P(t, T.vipSai, T.vipFora));
        pos = pVip.clone().lerp(UZ(-700, 900, 3.5), u); s = sVip;
        ry = lerp(Math.PI + 0.12, Math.PI + 1.3, u); rz = lerp(0.02, 0.35, u); rx = -0.05;
      }
    } else {
      // final: sobe de baixo girando e pousa no centro da cartela
      const u = E.outC(P(t, T.fin, T.fim));
      pos = UZ(540, 2500, 4).lerp(pFim, u); s = lerp(sFim * 1.25, sFim, u);
      ry = lerp(-TAU, 0, u) + (t > T.fim ? Math.sin((t - T.fim) * 1.1) * 0.12 : 0);
      rx = lerp(1.0, -0.06, u) + (t > T.fim ? Math.sin(t * 1.5) * 0.03 : 0);
      rz = lerp(0.5, -0.03, u);
      if (t > T.fim) pos.y += Math.sin((t - T.fim) * 2.0) * 0.03;
    }
    return { pos, s, rx, ry, rz };
  }

  function atualiza(t) {
    // ---------- ingresso
    const p = poseIngresso(t);
    raiz.visible = !!p;
    if (p) {
      raiz.position.copy(p.pos); raiz.scale.setScalar(p.s);
      raiz.rotation.set(p.rx, p.ry, p.rz);
      // carimbo: invisível antes do 24, bate grande e assenta
      const sv = t >= T.bate;
      selo.visible = sv;
      if (sv) {
        const u = P(t, T.bate, T.bate + 0.16);
        const k = lerp(2.6, 1.0, E.inC(u));
        selo.scale.set(k, k, 1);
        selo.material.opacity = lerp(0.0, 1.0, P(t, T.bate, T.bate + 0.06));
        selo.position.z = 0.024 + (1 - u) * 0.5;
      }
      // contador ADMITE 1 -> 2 -> 3 (vira como placa de aeroporto)
      const flip = (t0) => { const u = P(t, t0 - 0.09, t0 + 0.09); return u <= 0 || u >= 1 ? 1 : Math.abs(Math.cos(u * Math.PI)); };
      let n = 0;
      if (t >= T.amigo) n = 1;
      if (t >= T.parente) n = 2;
      dig.material.map = digs[n];
      dig.scale.y = Math.min(flip(T.amigo), flip(T.parente));
      // leque: as cópias abrem atrás do ingresso principal
      const a1 = E.outB(P(t, T.amigo - 0.05, T.amigo + 0.3)), a2 = E.outB(P(t, T.parente - 0.05, T.parente + 0.3));
      const naFase = t >= T.amigo - 0.05 && t <= T.fora;
      leque.children[0].visible = naFase; leque.children[1].visible = naFase && t >= T.parente - 0.05;
      leque.children[0].rotation.z = 0.2 * a1; leque.children[0].position.z = -0.06;
      leque.children[1].rotation.z = 0.4 * a2; leque.children[1].position.z = -0.12;
      // brilho que atravessa o ingresso
      let b = 0, bp = -1;
      for (const [t0, f] of [[EV.especial - 0.05, 1.0], [T.pousa - 0.15, 0.6], [T.bate + 0.25, 0.5], [EV.especial2 - 0.1, 1.0], [T.fim - 0.1, 0.9], [T.fim + 1.6, 0.7]]) {
        if (t >= t0 && t < t0 + 0.7) { b = f; bp = lerp(-0.4, 1.5, E.ioC((t - t0) / 0.7)); }
      }
      ing.brilho.material.uniforms.forca.value = b;
      ing.brilho.material.uniforms.pos.value = bp;
    }

    // ---------- faíscas: no "especial" (ao redor do ingresso) e no "especial" do convidado
    faiscas.visible = false;
    for (const [t0, c] of [[EV.especial, pRepouso], [EV.especial2, pVip], [T.fim, pFim]]) {
      const dt = t - t0;
      if (dt >= 0 && dt < 1.3) {
        faiscas.visible = true;
        for (let i = 0; i < NF; i++) {
          const [vx, vy, vz, vida] = fv[i];
          const tt = Math.min(dt, vida);
          fz[i * 3] = c.x + vx * tt * 1.3; fz[i * 3 + 1] = c.y + vy * tt * 1.1 - 1.6 * tt * tt; fz[i * 3 + 2] = c.z + 0.5 + vz * tt;
          if (dt > vida) fz[i * 3 + 2] = 99;          // apagada (fora do frustum)
        }
        fGeo.attributes.position.needsUpdate = true;
        fMat.opacity = 1 - P(dt, 0.6, 1.3);
      }
    }

    // ---------- mar da Galileia
    const m0 = EV.grandao - 0.38, m1 = EV.seg[10] - 0.05;
    mar.visible = t > m0 && t < m1 + 0.4;
    if (mar.visible) {
      const sobe = E.outC(P(t, m0, m0 + 0.8)), desce = E.inC(P(t, m1 - 0.1, m1 + 0.35));
      for (let i = 0; i < NM; i++) {
        const [gx, gz, f] = base[i];
        const w = 0.36 * Math.sin(0.42 * gx + 1.35 * t + 0.16 * gz) + 0.24 * Math.sin(0.66 * gz - 1.05 * t + 0.28 * gx) + 0.08 * Math.sin(1.8 * gx + 2.3 * t - 0.4 * gz);
        mPos[i * 3] = gx; mPos[i * 3 + 1] = w - 3.2 * (1 - sobe) - 3 * desce; mPos[i * 3 + 2] = gz;
        const crista = 0.55 + 0.45 * cl((w + 0.5) / 1.1);
        const k = Math.min(1, f * crista * 1.35);
        mCor[i * 3] = 1.0 * k; mCor[i * 3 + 1] = 0.76 * k; mCor[i * 3 + 2] = 0.22 * k;
      }
      mGeo.attributes.position.needsUpdate = true; mGeo.attributes.color.needsUpdate = true;
      mMat.opacity = sobe * (1 - desce);
    }

    // ---------- anéis ("grandemente"): saem de trás da cabeça
    const a0 = EV.grandemente - 0.05;
    const cab = UZ(540, 560, -1.2);
    aneis.forEach((a, i) => {
      const dt = t - a0 - i * 0.16;
      a.visible = dt > 0 && dt < 1.5;
      if (a.visible) {
        const u = dt / 1.5;
        const r = lerp(0.6, 6.5, E.outC(u));
        a.position.copy(cab); a.scale.setScalar(r);
        a.rotation.set(0.42 + 0.05 * i, Math.sin(i) * 0.2, 0);
        a.material.opacity = (1 - u) * (u < 0.08 ? u / 0.08 : 1) * 0.95;
      }
    });
  }

  // camada de cada objeto: atrás (z < 0 no mundo) ou na frente
  const tras = (o) => {
    if (o === raiz) return raiz.position.z < 0;
    return o === mar || aneis.includes(o);
  };
  const objs = [raiz, faiscas, mar, ...aneis];
  renderer.autoClear = false;
  function passada(ctx, querTras) {
    const vis = objs.map((o) => o.visible);
    let algum = false;
    renderer.clear();
    if (querTras && vis[2]) {                      // o mar usa a própria câmera, desenhado primeiro (fica no fundo)
      objs.forEach((o, i) => (o.visible = i === 2));
      renderer.render(cena, camMar); algum = true;
    }
    let resto = false;
    objs.forEach((o, i) => { o.visible = i !== 2 && vis[i] && tras(o) === querTras; resto = resto || o.visible; });
    if (resto) { renderer.render(cena, cam); algum = true; }
    ctx.clearRect(0, 0, 1080, 1920);
    if (algum) ctx.drawImage(gl, 0, 0);
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
