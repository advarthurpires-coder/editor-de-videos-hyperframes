// Mundo 3D do reel "Culto Hero" (Three.js r169, renderização determinística a partir do tempo).
// Uma única câmera fixa; cada objeto tem sua janela de visibilidade e sua animação calculada só de `t`.
// Unidades: câmera em z=14, fov 32 => 239,14 px por unidade no plano z=0 (quadro 1080×1920).
import * as THREE from "three";
import { RoomEnvironment } from "three/addons/RoomEnvironment.js";
import { RoundedBoxGeometry } from "three/addons/RoundedBoxGeometry.js";
import { FontLoader } from "three/addons/FontLoader.js";
import { TextGeometry } from "three/addons/TextGeometry.js";

const PX = 239.14;
const U = (xpx, ypx) => [(xpx - 540) / PX, (960 - ypx) / PX];
const TAU = Math.PI * 2;

// ------------------------------------------------------------------ tempo / easing
const cl = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const P = (t, a, b) => cl((t - a) / (b - a));
const E = {
  lin: (x) => x,
  inC: (x) => x * x * x,
  outC: (x) => 1 - Math.pow(1 - x, 3),
  ioC: (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2),
  outE: (x) => (x >= 1 ? 1 : 1 - Math.pow(2, -10 * x)),
  inE: (x) => (x <= 0 ? 0 : Math.pow(2, 10 * x - 10)),
  outB: (x) => 1 + 2.70158 * Math.pow(x - 1, 3) + 1.70158 * Math.pow(x - 1, 2),
  outB2: (x) => 1 + 3.6 * Math.pow(x - 1, 3) + 2.6 * Math.pow(x - 1, 2),
  outBounce: (x) => {
    const n = 7.5625, d = 2.75;
    if (x < 1 / d) return n * x * x;
    if (x < 2 / d) return n * (x -= 1.5 / d) * x + 0.75;
    if (x < 2.5 / d) return n * (x -= 2.25 / d) * x + 0.9375;
    return n * (x -= 2.625 / d) * x + 0.984375;
  },
};
// chaves [[t, valor, easing do trecho que termina nessa chave], ...]
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
const dentro = (t, a, b) => t >= a && t < b;
function rng(seed) {
  return function () {
    seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
    let x = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    x = (x + Math.imul(x ^ (x >>> 7), 61 | x)) ^ x;
    return ((x ^ (x >>> 14)) >>> 0) / 4294967296;
  };
}
// mola amortecida: oscilação que morre após o instante t0
const mola = (t, t0, amp, freq = 12, dec = 4) => (t < t0 ? 0 : amp * Math.exp(-(t - t0) * dec) * Math.sin((t - t0) * freq));

// ------------------------------------------------------------------ montagem
export async function montar(canvas, T) {
  const W = (f, palavra, n = 0) => T[f - 1].palavras.filter((p) => p.w.toLowerCase().startsWith(palavra.toLowerCase()))[n].s;

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1);
  renderer.setSize(1080, 1920, false);
  renderer.setClearColor(0x000000, 0);
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;
  renderer.outputColorSpace = THREE.SRGBColorSpace;

  const cena = new THREE.Scene();
  const pm = new THREE.PMREMGenerator(renderer);
  cena.environment = pm.fromScene(new RoomEnvironment(), 0.04).texture;
  const cam = new THREE.PerspectiveCamera(32, 1080 / 1920, 0.1, 100);
  cam.position.set(0, 0, 14);

  const luzChave = new THREE.DirectionalLight(0xfff2dc, 2.2);
  luzChave.position.set(3, 5, 8);
  cena.add(luzChave);
  const luzRecorte = new THREE.DirectionalLight(0xe9a513, 1.4);
  luzRecorte.position.set(-5, 2, -4);
  cena.add(luzRecorte);
  const hemi = new THREE.HemisphereLight(0xfff4e0, 0x1a1208, 0.6);
  cena.add(hemi);
  const luzSirene = new THREE.PointLight(0xff2a1a, 0, 18, 1.4);
  cena.add(luzSirene);

  // ---------------------------------------------------------------- materiais
  const M = {
    preto: new THREE.MeshStandardMaterial({ color: 0x0e0e0e, metalness: 0.55, roughness: 0.28 }),
    pretoFosco: new THREE.MeshStandardMaterial({ color: 0x141414, metalness: 0.1, roughness: 0.6 }),
    mostarda: new THREE.MeshStandardMaterial({ color: 0xe9a513, metalness: 0.25, roughness: 0.35 }),
    mostardaMetal: new THREE.MeshStandardMaterial({ color: 0xd9940c, metalness: 0.9, roughness: 0.3 }),
    ouro: new THREE.MeshStandardMaterial({ color: 0xc98a12, metalness: 1.0, roughness: 0.25 }),
    creme: new THREE.MeshStandardMaterial({ color: 0xf3ebdd, metalness: 0.0, roughness: 0.55 }),
    cremeBrilho: new THREE.MeshStandardMaterial({ color: 0xf3ebdd, metalness: 0.1, roughness: 0.25 }),
    couro: new THREE.MeshStandardMaterial({ color: 0x3a2618, metalness: 0.05, roughness: 0.55 }),
    vidro: new THREE.MeshPhysicalMaterial({ color: 0xcfe6ff, metalness: 0, roughness: 0.05, transparent: true, opacity: 0.28, clearcoat: 1 }),
    cinza: new THREE.MeshStandardMaterial({ color: 0x8b8b8b, metalness: 0.2, roughness: 0.45 }),
    cinzaEsc: new THREE.MeshStandardMaterial({ color: 0x4a4a4a, metalness: 0.3, roughness: 0.4 }),
    aco: new THREE.MeshStandardMaterial({ color: 0x9a9a9a, metalness: 0.95, roughness: 0.35 }),
  };

  // ---------------------------------------------------------------- texturas de canvas
  await Promise.all(["400 80px Anton", "800 60px 'Barlow Condensed'", "700 60px UnifrakturCook", "600 40px Oswald"].map((f) => document.fonts.load(f)));
  function canvasTex(w, h, desenhar) {
    const c = document.createElement("canvas");
    c.width = w; c.height = h;
    desenhar(c.getContext("2d"), w, h);
    const tx = new THREE.CanvasTexture(c);
    tx.colorSpace = THREE.SRGBColorSpace;
    tx.anisotropy = 4;
    return tx;
  }
  function brilhoTex(cor) {
    return canvasTex(256, 256, (g) => {
      const r = g.createRadialGradient(128, 128, 0, 128, 128, 128);
      r.addColorStop(0, cor + "ff"); r.addColorStop(0.25, cor + "aa"); r.addColorStop(1, cor + "00");
      g.fillStyle = r; g.fillRect(0, 0, 256, 256);
    });
  }
  function sprite(tex, w, h, aditivo = true) {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({
      map: tex, transparent: true, depthWrite: false, blending: aditivo ? THREE.AdditiveBlending : THREE.NormalBlending,
    }));
    return m;
  }
  const texSombra = canvasTex(256, 256, (g) => {
    const r = g.createRadialGradient(128, 128, 0, 128, 128, 128);
    r.addColorStop(0, "rgba(0,0,0,0.55)"); r.addColorStop(0.6, "rgba(0,0,0,0.2)"); r.addColorStop(1, "rgba(0,0,0,0)");
    g.fillStyle = r; g.fillRect(0, 0, 256, 256);
  });

  // ---------------------------------------------------------------- fontes / formas
  const fl = new FontLoader();
  const FG = fl.parse(window.FONTES3D.gotica);
  const FA = fl.parse(window.FONTES3D.anton);
  function texto3d(str, font, size, depth, mats, bevel = 0.03) {
    const g = new TextGeometry(str, { font, size, depth, curveSegments: 10, bevelEnabled: bevel > 0, bevelThickness: bevel, bevelSize: bevel * 0.7, bevelSegments: 3 });
    g.computeBoundingBox();
    g.center();
    return new THREE.Mesh(g, mats);
  }
  function alturaPara(obj, h) {
    const b = new THREE.Box3().setFromObject(obj);
    obj.scale.multiplyScalar(h / (b.max.y - b.min.y));
  }
  function formasDe(lista) {
    return lista.map((f) => {
      const s = new THREE.Shape(f.ext.map((p) => new THREE.Vector2(p[0], p[1])));
      f.furos.forEach((h) => s.holes.push(new THREE.Path(h.map((p) => new THREE.Vector2(p[0], p[1])))));
      return s;
    });
  }
  function poligonoArredondado(pts, r) {
    const s = new THREE.Shape();
    const n = pts.length;
    for (let i = 0; i < n; i++) {
      const p0 = pts[(i - 1 + n) % n], p1 = pts[i], p2 = pts[(i + 1) % n];
      const a = new THREE.Vector2(p0[0] - p1[0], p0[1] - p1[1]).normalize().multiplyScalar(r);
      const b = new THREE.Vector2(p2[0] - p1[0], p2[1] - p1[1]).normalize().multiplyScalar(r);
      if (i === 0) s.moveTo(p1[0] + a.x, p1[1] + a.y); else s.lineTo(p1[0] + a.x, p1[1] + a.y);
      s.quadraticCurveTo(p1[0], p1[1], p1[0] + b.x, p1[1] + b.y);
    }
    s.closePath();
    return s;
  }
  function retArred(w, h, r) {
    return poligonoArredondado([[-w / 2, -h / 2], [w / 2, -h / 2], [w / 2, h / 2], [-w / 2, h / 2]], r);
  }
  const extr = (shape, depth, bevel = 0.03) => new THREE.ExtrudeGeometry(shape, { depth, bevelEnabled: bevel > 0, bevelThickness: bevel, bevelSize: bevel * 0.8, bevelSegments: 3, curveSegments: 24 });

  const objs = []; // {o, up(t)}
  function add(o, up) { cena.add(o); objs.push({ o, up }); return o; }

  // ================================================================= FITAS DE AVISO (abertura e loop)
  function fita(sentido, seed) {
    const tex = canvasTex(1024, 96, (g, w, h) => {
      g.fillStyle = "#E9A513"; g.fillRect(0, 0, w, h);
      g.fillStyle = "#0d0d0d";
      const bloco = (x0, x1) => { for (let x = x0 - 60; x < x1; x += 44) { g.beginPath(); g.moveTo(x, h); g.lineTo(x + 22, h); g.lineTo(x + 22 + 50, 0); g.lineTo(x + 50, 0); g.closePath(); g.fill(); } };
      g.save(); g.beginPath(); g.rect(0, 0, 150, h); g.rect(512, 0, 150, h); g.clip(); bloco(0, 1024); g.restore();
      g.font = "400 62px Anton"; g.textBaseline = "middle"; g.textAlign = "center";
      g.fillText("ATENÇÃO", 331, h / 2 + 3); g.fillText("AVISO", 843, h / 2 + 3);
      g.fillRect(0, 0, w, 6); g.fillRect(0, h - 6, w, 6);
    });
    tex.wrapS = THREE.RepeatWrapping;
    tex.repeat.set(5, 1);
    const geo = new THREE.PlaneGeometry(16, 0.78, 220, 1);
    const base = geo.attributes.position.array.slice();
    const mesh = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ map: tex, roughness: 0.5, metalness: 0.05, side: THREE.DoubleSide }));
    const piv = new THREE.Group();
    piv.add(mesh);
    piv.userData = { mesh, base, tex, sentido, seed };
    return piv;
  }
  const fitaA = fita(1, 1), fitaB = fita(-1, 2);
  fitaA.rotation.z = 0.46; fitaA.position.set(0, 0.25, -1.6);
  fitaB.rotation.z = -0.46; fitaB.position.set(0, 0.25, -2.0);
  [fitaA, fitaB].forEach((f) => add(f, (t) => {
    const ab = dentro(t, 0, 4.0), fe = t >= 62.5;
    f.visible = ab || fe;
    if (!f.visible) return;
    const d = f.userData;
    let x;
    if (ab) x = K(t, [[0, 0], [3.5, 0], [3.95, 17 * d.sentido, "inC"]]);
    else x = K(t, [[62.5, -17 * d.sentido], [63.0, 0, "outE"]]);
    // "estalo" inicial: a fita vibra e assenta (frame 0 = último frame, para o loop)
    const tr = ab ? mola(t, 0, 0.18, 26, 6) : mola(t, 63.0, 0.18, 26, 6);
    d.mesh.position.set(x, tr, 0);
    d.tex.offset.x = -t * 0.12 * d.sentido;
    const p = d.mesh.geometry.attributes.position;
    for (let i = 0; i < p.count; i++) {
      const bx = d.base[i * 3], by = d.base[i * 3 + 1];
      p.array[i * 3 + 2] = 0.22 * Math.sin(bx * 0.55 + t * 2.1 + d.seed) + 0.08 * Math.sin(bx * 1.7 - t * 3.3) + by * 0.12 * Math.sin(bx * 0.9 + t);
    }
    p.needsUpdate = true;
    d.mesh.geometry.computeVertexNormals();
  }));

  // ================================================================= PLACA "!" (gancho)
  const placa = new THREE.Group();
  {
    const R = 1.62, tri = (r) => [[0, r], [-r * 0.866, -r * 0.5], [r * 0.866, -r * 0.5]];
    const ext = new THREE.Mesh(extr(poligonoArredondado(tri(R), 0.32), 0.22, 0.04), M.preto);
    const inn = new THREE.Mesh(extr(poligonoArredondado(tri(R * 0.78), 0.22), 0.06, 0.02), M.mostarda);
    inn.position.z = 0.24;
    const ex = texto3d("!", FA, 1.0, 0.12, M.preto, 0.015);
    alturaPara(ex, 1.05);
    ex.position.set(0, -0.12, 0.38);
    placa.add(ext, inn, ex);
    const brilho = sprite(brilhoTex("#e9a513"), 7, 7);
    brilho.position.z = -1.5;
    brilho.material.opacity = 0.55;
    placa.add(brilho);
  }
  const [, py] = U(540, 770);
  add(placa, (t) => {
    placa.visible = dentro(t, 0.2, 3.98);
    if (!placa.visible) return;
    const s = K(t, [[0.2, 0.2], [1.18, 1, "outC"], [3.55, 1], [3.95, 0, "inC"]]) * (1 + mola(t, 1.18, 0.07, 30, 7));
    placa.scale.setScalar(Math.max(0.001, s));
    placa.position.set(0, py + 0.05 * Math.sin(t * 1.6), K(t, [[0.2, -12], [1.18, 0, "outC"], [3.55, 0], [3.95, -5, "inC"]]));
    placa.rotation.y = K(t, [[0.2, -4 * Math.PI], [1.18, 0, "outC"]]) + 0.12 * Math.sin(t * 1.3) * P(t, 1.2, 1.8) + K(t, [[3.55, 0], [3.95, Math.PI, "inC"]]);
    placa.rotation.z = mola(t, 1.18, 0.06, 18, 5);
  });

  // ================================================================= NUMERAIS GÓTICOS 1 · 2 · 3
  function numeral(ch) {
    const g = new THREE.Group();
    const n = texto3d(ch, FG, 2, 0.55, [M.mostarda, M.ouro], 0.05);
    alturaPara(n, 2.5);
    g.add(n);
    const b = sprite(brilhoTex("#e9a513"), 6, 6);
    b.position.z = -2;
    b.material.opacity = 0.45;
    g.add(b);
    return g;
  }
  const BADGE = U(150, 312);
  function animNumeral(g, t0, tBadge, tFim, y) {
    add(g, (t) => {
      g.visible = dentro(t, t0, tFim);
      if (!g.visible) return;
      const slam = [[t0, 10], [t0 + 0.4, 0, "outE"]];
      const z = K(t, slam);
      const b = P(t, tBadge, tBadge + 0.4);
      const eb = E.ioC(b);
      g.position.set(BADGE[0] * eb, y + (BADGE[1] - y) * eb, z);
      g.scale.setScalar(1 - 0.72 * eb);
      g.rotation.y = K(t, [[t0, 1.5], [t0 + 0.75, 0, "outC"]]) + 0.18 * Math.sin((t - t0) * 1.4) * (1 - eb) + eb * 0.25 * Math.sin(t * 2);
      g.rotation.x = mola(t, t0 + 0.4, 0.12, 16, 6);
      g.children[1].visible = b < 0.5;
    });
  }
  animNumeral(numeral("1"), 3.85, 6.75, 15.1, U(0, 760)[1]);
  animNumeral(numeral("2"), 17.0, 17.85, 24.4, U(0, 860)[1]);
  animNumeral(numeral("3"), 24.4, 26.95, 35.0, U(0, 840)[1]);

  // ================================================================= CARROSSEL: tipos de homem
  function capacete(mat = M.mostarda, mat2 = M.preto) {
    const g = new THREE.Group();
    const casco = new THREE.Mesh(new THREE.SphereGeometry(0.62, 48, 24, 0, TAU, 0, Math.PI / 2), mat);
    casco.scale.y = 0.88;
    const aba = new THREE.Mesh(new THREE.CylinderGeometry(0.8, 0.82, 0.07, 64), mat);
    aba.scale.z = 1.12; aba.position.z = 0.06;
    const crista = new THREE.Mesh(new THREE.TorusGeometry(0.56, 0.07, 14, 48, Math.PI), mat);
    crista.rotation.y = Math.PI / 2; crista.scale.y = 0.9;
    const faixa = new THREE.Mesh(new THREE.CylinderGeometry(0.625, 0.63, 0.1, 48, 1, true), mat2);
    faixa.position.y = 0.06;
    g.add(casco, aba, crista, faixa);
    g.position.y = -0.2;
    const w = new THREE.Group(); w.add(g); return w;
  }
  function maleta() {
    const g = new THREE.Group();
    const corpo = new THREE.Mesh(new RoundedBoxGeometry(1.5, 1.04, 0.42, 4, 0.08), M.couro);
    const alca = new THREE.Mesh(new THREE.TorusGeometry(0.22, 0.05, 12, 32, Math.PI), M.preto);
    alca.position.y = 0.52;
    const tampa = new THREE.Mesh(new THREE.BoxGeometry(1.52, 0.03, 0.44), M.preto);
    tampa.position.y = 0.22;
    g.add(corpo, alca, tampa);
    [-0.45, 0.45].forEach((x) => { const f = new THREE.Mesh(new RoundedBoxGeometry(0.16, 0.12, 0.05, 2, 0.02), M.ouro); f.position.set(x, 0.22, 0.23); g.add(f); });
    return g;
  }
  function volante() {
    const g = new THREE.Group();
    const aro = new THREE.Mesh(new THREE.TorusGeometry(0.72, 0.09, 20, 72), M.preto);
    const cubo = new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.24, 0.16, 40), M.ouro);
    cubo.rotation.x = Math.PI / 2;
    g.add(aro, cubo);
    [Math.PI / 2 + Math.PI, Math.PI / 6 + Math.PI * 0.05, (5 * Math.PI) / 6 - Math.PI * 0.05].forEach((a) => {
      const r = new THREE.Mesh(new RoundedBoxGeometry(0.6, 0.12, 0.07, 2, 0.03), M.preto);
      r.position.set(Math.cos(a) * 0.42, Math.sin(a) * 0.42, 0);
      r.rotation.z = a;
      g.add(r);
    });
    const logo = texto3d("H", FG, 0.2, 0.03, M.preto, 0);
    logo.position.z = 0.09;
    g.add(logo);
    return g;
  }
  function capelo() {
    const g = new THREE.Group();
    const tabua = new THREE.Mesh(new RoundedBoxGeometry(1.35, 0.07, 1.35, 2, 0.02), M.preto);
    tabua.rotation.y = Math.PI / 4;
    const copa = new THREE.Mesh(new THREE.CylinderGeometry(0.48, 0.52, 0.42, 40), M.preto);
    copa.position.y = -0.24;
    const botao = new THREE.Mesh(new THREE.SphereGeometry(0.07, 16, 12), M.ouro);
    botao.position.y = 0.06;
    const fio = new THREE.Mesh(new THREE.CylinderGeometry(0.015, 0.015, 0.6, 8), M.ouro);
    fio.position.set(0.42, -0.24, 0.42); fio.rotation.z = 0.05;
    const borla = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.09, 0.28, 16), M.mostarda);
    borla.position.set(0.43, -0.6, 0.42);
    g.add(tabua, copa, botao, fio, borla);
    g.rotation.x = 0.35;
    g.position.y = 0.2;
    const w = new THREE.Group(); w.add(g); return w;
  }
  function oculos(aro = M.preto) {
    const g = new THREE.Group();
    [-0.36, 0.36].forEach((x) => {
      const a = new THREE.Mesh(new THREE.TorusGeometry(0.3, 0.05, 16, 48), aro);
      a.position.x = x; a.scale.y = 0.82;
      const l = new THREE.Mesh(new THREE.CircleGeometry(0.29, 40), M.vidro);
      l.position.set(x, 0, 0.005); l.scale.y = 0.82;
      const haste = new THREE.Mesh(new THREE.BoxGeometry(0.035, 0.035, 0.9), aro);
      haste.position.set(x * 1.86, 0.05, -0.45);
      g.add(a, l, haste);
    });
    const ponte = new THREE.Mesh(new THREE.TorusGeometry(0.1, 0.035, 10, 24, Math.PI), aro);
    ponte.position.y = 0.06;
    g.add(ponte);
    g.rotation.y = 0.0;
    return g;
  }
  const carrossel = new THREE.Group();
  const itens = [capacete(), maleta(), volante(), capelo(), oculos()];
  const RAIO = 1.45;
  itens.forEach((it, k) => {
    const a = (k * TAU) / 5;
    const suporte = new THREE.Group();
    suporte.position.set(Math.sin(a) * RAIO, 0, Math.cos(a) * RAIO);
    suporte.add(it);
    it.userData.k = k;
    carrossel.add(suporte);
  });
  const anelLuz = sprite(brilhoTex("#e9a513"), 6, 3.2);
  anelLuz.position.set(0, -1.2, 0);
  anelLuz.rotation.x = -Math.PI / 2;
  anelLuz.material.opacity = 0.6;
  carrossel.add(anelLuz);
  const palavras1 = ["Peão", "empresário", "motorista", "estudante", "aposentado"].map((w) => W(3, w));
  const CY = U(0, 820)[1];
  add(carrossel, (t) => {
    carrossel.visible = dentro(t, 7.0, 10.95);
    if (!carrossel.visible) return;
    // gira até o item de cada palavra (o giro termina no início da palavra)
    let ang = 0.9;
    for (let k = 0; k < 5; k++) {
      const de = k === 0 ? 0.9 : -((k - 1) * TAU) / 5, alvo = -(k * TAU) / 5;
      const ini = k === 0 ? 7.0 : palavras1[k] - 0.34;
      if (t >= ini) ang = de + (alvo - de) * E.outB(P(t, ini, palavras1[k] + 0.02));
    }
    ang += K(t, [[10.55, 0], [10.95, -2.6, "inC"]]);
    carrossel.rotation.y = ang;
    const s = K(t, [[7.0, 0], [7.4, 1, "outB"], [10.55, 1], [10.95, 0.01, "inC"]]);
    carrossel.scale.setScalar(s);
    carrossel.position.set(0, CY, -1.2);
    carrossel.rotation.x = 0.16;
    carrossel.children.forEach((sup) => {
      const it = sup.children[0];
      const k = it && it.userData.k;
      if (k === undefined) return;
      // o item encara a câmera; o da palavra atual cresce
      sup.rotation.y = -ang;
      const ini = palavras1[k] - 0.15, fim = k === 4 ? 99 : palavras1[k + 1] - 0.15;
      const on = Math.min(P(t, ini, ini + 0.2), 1 - P(t, fim, fim + 0.2));
      it.scale.setScalar(0.5 + 0.95 * E.outB(on));
      it.rotation.y = 0.5 * Math.sin(t * 1.1 + k) + on * 0.3 * Math.sin(t * 2.2);
      it.rotation.x = 0.1 * Math.sin(t * 0.9 + k * 2);
    });
  });

  // ================================================================= PEÕES (somos parecidos)
  const perfilPeao = [[0, 0], [0.42, 0], [0.44, 0.06], [0.42, 0.12], [0.33, 0.17], [0.3, 0.24], [0.22, 0.38], [0.17, 0.58], [0.15, 0.72], [0.26, 0.78], [0.27, 0.83], [0.14, 0.88], [0.12, 0.92]].map((p) => new THREE.Vector2(p[0], p[1]));
  const geoPeao = new THREE.LatheGeometry(perfilPeao, 48);
  const geoCabeca = new THREE.SphereGeometry(0.2, 32, 20);
  const peoes = [];
  const VOCE = 3;
  const tVoce = W(4, "você"), tDif = W(4, "diferente");
  const corCreme = new THREE.Color(0xf3ebdd), corMost = new THREE.Color(0xe9a513);
  for (let k = 0; k < 7; k++) {
    const mat = new THREE.MeshStandardMaterial({ color: 0xf3ebdd, metalness: 0.15, roughness: 0.3 });
    const g = new THREE.Group();
    const b = new THREE.Mesh(geoPeao, mat);
    const c = new THREE.Mesh(geoCabeca, mat);
    c.position.y = 1.08;
    g.add(b, c);
    g.userData = { mat, k };
    peoes.push(g);
  }
  const grupoPeoes = new THREE.Group();
  peoes.forEach((p) => grupoPeoes.add(p));
  const sombraPeoes = sprite(texSombra, 5.2, 1.0, false);
  sombraPeoes.rotation.x = -Math.PI / 2;
  sombraPeoes.position.y = 0.01;
  grupoPeoes.add(sombraPeoes);
  const PY = U(0, 1140)[1];
  add(grupoPeoes, (t) => {
    grupoPeoes.visible = dentro(t, 10.8, 15.2);
    if (!grupoPeoes.visible) return;
    grupoPeoes.position.set(0, PY, 0);
    grupoPeoes.rotation.x = 0.22;
    grupoPeoes.rotation.y = 0.12 * Math.sin((t - 10.8) * 0.45);
    peoes.forEach((p, k) => {
      const x = (k - 3) * 0.52;
      const tc = 10.95 + 0.085 * k;
      let y = K(t, [[tc - 0.32, 5], [tc, 0, "outBounce"]]);
      if (k === VOCE) y += K(t, [[tVoce, 0], [tVoce + 0.35, 0.35, "outB"], [tDif + 0.4, 0.35], [tDif + 0.8, 0, "ioC"]]);
      p.position.set(x, y, -Math.abs(k - 3) * 0.12);
      p.scale.setScalar(1.05);
      // "VOCÊ" fica mostarda; em "diferente" a cor se espalha (do centro para fora): todos iguais
      let c = 0;
      if (k === VOCE) c = P(t, tVoce, tVoce + 0.25);
      else c = P(t, tDif + 0.12 * Math.abs(k - 3), tDif + 0.12 * Math.abs(k - 3) + 0.3);
      p.userData.mat.color.copy(corCreme).lerp(corMost, c);
      p.userData.mat.emissive.setRGB(0.25 * c * (k === VOCE ? 1 : 0.4) * P(t, tVoce, tVoce + 0.2) * (1 - P(t, tDif + 0.4, tDif + 0.8)), 0.14 * c * (k === VOCE ? 1 : 0.4) * P(t, tVoce, tVoce + 0.2) * (1 - P(t, tDif + 0.4, tDif + 0.8)), 0);
      p.rotation.y = t * 0.3 + k;
    });
  });

  // ================================================================= CASA (motivo 2)
  const casa = new THREE.Group();
  const janelas = [];
  {
    const parede = new THREE.MeshStandardMaterial({ color: 0xf0e4cf, roughness: 0.7 });
    const corpo = new THREE.Mesh(new RoundedBoxGeometry(2.4, 1.45, 1.8, 3, 0.04), parede);
    corpo.position.y = 0.725;
    const tri = new THREE.Shape();
    tri.moveTo(-1.38, 0); tri.lineTo(1.38, 0); tri.lineTo(0, 1.05); tri.closePath();
    const telhado = new THREE.Mesh(new THREE.ExtrudeGeometry(tri, { depth: 2.1, bevelEnabled: true, bevelThickness: 0.04, bevelSize: 0.04, bevelSegments: 2 }), M.preto);
    telhado.position.set(0, 1.45, -1.05);
    const chamine = new THREE.Mesh(new RoundedBoxGeometry(0.3, 0.7, 0.3, 2, 0.03), M.preto);
    chamine.position.set(0.68, 2.05, -0.3);
    const porta = new THREE.Mesh(new RoundedBoxGeometry(0.46, 0.8, 0.06, 2, 0.02), M.mostarda);
    porta.position.set(-0.55, 0.42, 0.91);
    const mac = new THREE.Mesh(new THREE.SphereGeometry(0.035, 12, 8), M.ouro);
    mac.position.set(-0.4, 0.42, 0.95);
    const chao = sprite(texSombra, 4.6, 3.8, false);
    chao.rotation.x = -Math.PI / 2;
    chao.position.y = 0.005;
    casa.add(corpo, telhado, chamine, porta, mac, chao);
    const dourado = brilhoTex("#ffc94a");
    const posJ = [[0.45, 0.85, 0.905, 0], [-0.55, 1.12, 0.905, 0], [1.205, 0.85, 0.3, Math.PI / 2], [1.205, 0.85, -0.45, Math.PI / 2], [0, 1.95, 0.0, 0]];
    posJ.forEach(([x, y, z, ry], i) => {
      const mat = new THREE.MeshStandardMaterial({ color: 0x1c1a17, emissive: 0xffc04a, emissiveIntensity: 0, roughness: 0.3 });
      const j = new THREE.Mesh(new THREE.PlaneGeometry(i === 1 ? 0.0001 : 0.42, i === 1 ? 0.0001 : 0.4), mat);
      const mold = new THREE.Mesh(new THREE.BoxGeometry(0.48, 0.46, 0.03), M.preto);
      const cruz = new THREE.Group();
      const c1 = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.025, 0.02), M.preto);
      const c2 = new THREE.Mesh(new THREE.BoxGeometry(0.025, 0.4, 0.02), M.preto);
      cruz.add(c1, c2);
      const g = new THREE.Group();
      mold.position.z = -0.012;
      cruz.position.z = 0.012;
      g.add(mold, j, cruz);
      const halo = sprite(dourado, 1.3, 1.3);
      halo.position.z = 0.08;
      halo.material.opacity = 0;
      g.add(halo);
      g.position.set(x, y, z);
      g.rotation.y = ry;
      if (i === 1) { g.visible = false; }
      if (i === 4) { g.position.set(0, 1.83, 0.86); g.scale.setScalar(0.75); }
      casa.add(g);
      janelas.push({ g, mat, halo });
    });
  }
  const tJan = [W(6, "vontade"), W(6, "de", 1), W(6, "mudar"), W(6, "coisas"), W(6, "casa")];
  const CASA_Y = U(0, 1290)[1];
  const tEsp = W(7, "esposa"), tEst = W(7, "estranhar");
  const congela2 = (t) => (t > 23.45 ? 23.45 : t);
  add(casa, (t0) => {
    casa.visible = dentro(t0, 17.85, 24.4);
    if (!casa.visible) return;
    const t = congela2(t0);
    casa.position.set(0, K(t, [[17.85, -7], [18.5, CASA_Y, "outB"]]), 0);
    casa.rotation.set(0.2, -0.62 + 0.05 * (t - 18.5) + mola(t, 18.5, 0.1, 9, 4), 0);
    casa.rotation.z = (t > tEst && t < 23.45 ? 0.03 * Math.sin(t * 90) * (1 - P(t, tEst, 23.45)) : 0);
    // janelas acendem uma a uma (frente, laterais, sótão); a 5ª palavra ("casa") acende a porta, abaixo
    [0, 2, 3, 4].forEach((ix, i) => {
      const on = P(t, tJan[i], tJan[i] + 0.07);
      janelas[ix].mat.emissiveIntensity = 2.4 * on;
      janelas[ix].halo.material.opacity = 0.75 * on;
    });
  });
  // porta "acende" em "casa" (usa o halo da janela escondida, reposicionado na porta)
  {
    const hj = janelas[1];
    hj.g.visible = true;
    hj.g.position.set(-0.55, 0.45, 0.95);
    hj.g.children.forEach((c) => (c.visible = c === hj.halo));
    add(new THREE.Group(), (t0) => {
      const t = congela2(t0);
      hj.halo.material.opacity = 0.9 * P(t, tJan[4], tJan[4] + 0.08);
      hj.halo.scale.setScalar(1.5);
    });
  }
  const interroga = new THREE.Group();
  {
    const q = texto3d("?", FA, 1, 0.35, [M.mostarda, M.ouro], 0.04);
    alturaPara(q, 1.55);
    interroga.add(q);
    const b = sprite(brilhoTex("#e9a513"), 3.5, 3.5);
    b.position.z = -0.8; b.material.opacity = 0.5;
    interroga.add(b);
  }
  const QP = U(790, 690);
  add(interroga, (t0) => {
    interroga.visible = dentro(t0, tEsp - 0.05, 24.4);
    if (!interroga.visible) return;
    const t = congela2(t0);
    interroga.scale.setScalar(Math.max(0.001, K(t, [[tEsp, 0], [tEsp + 0.4, 1, "outB2"]])));
    interroga.position.set(QP[0], QP[1] + 0.08 * Math.sin(t * 3), 0.6);
    interroga.rotation.z = K(t, [[tEst, 0], [tEst + 0.3, -0.42, "outB2"]]) + 0.05 * Math.sin(t * 2.4);
    interroga.rotation.y = 0.3 * Math.sin(t * 1.7);
  });

  // ================================================================= GIROFLEX (motivo 3)
  const giroflex = new THREE.Group();
  const feixes = new THREE.Group();
  {
    const base = new THREE.Mesh(new THREE.CylinderGeometry(0.62, 0.68, 0.3, 48), M.preto);
    const cupula = new THREE.Mesh(new THREE.SphereGeometry(0.55, 48, 24, 0, TAU, 0, Math.PI / 2),
      new THREE.MeshPhysicalMaterial({ color: 0xff2a1a, emissive: 0xff1a0a, emissiveIntensity: 1.2, transparent: true, opacity: 0.88, roughness: 0.15, clearcoat: 1 }));
    cupula.position.y = 0.15;
    cupula.scale.y = 1.15;
    giroflex.add(base, cupula);
    const texF = canvasTex(256, 64, (g, w, h) => {
      const gr = g.createLinearGradient(0, 0, w, 0);
      gr.addColorStop(0, "rgba(255,60,40,0.9)"); gr.addColorStop(1, "rgba(255,60,40,0)");
      g.fillStyle = gr; g.fillRect(0, 0, w, h);
    });
    [0, Math.PI].forEach((a) => {
      const f = new THREE.Mesh(new THREE.PlaneGeometry(6, 1.3), new THREE.MeshBasicMaterial({ map: texF, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide }));
      f.position.x = 3;
      const piv = new THREE.Group();
      piv.rotation.y = a;
      piv.add(f);
      feixes.add(piv);
    });
    feixes.position.y = 0.4;
    giroflex.add(feixes);
    const halo = sprite(brilhoTex("#ff3020"), 4, 4);
    halo.position.set(0, 0.45, 0.6);
    giroflex.add(halo);
    giroflex.userData.halo = halo;
  }
  const GY = U(0, 360)[1];
  add(giroflex, (t) => {
    giroflex.visible = dentro(t, 24.4, 27.5);
    luzSirene.intensity = 0;
    if (!giroflex.visible) return;
    giroflex.position.set(0, K(t, [[24.4, 6.5], [24.8, GY, "outB"], [27.0, GY], [27.45, 6.5, "inC"]]), -1.2);
    giroflex.rotation.x = 0.35;
    feixes.rotation.y = t * 8;
    giroflex.userData.halo.material.opacity = 0.55 + 0.45 * Math.abs(Math.sin(t * 8));
    luzSirene.position.set(Math.cos(t * 8) * 3, GY, 2 + Math.sin(t * 8) * 2);
    luzSirene.intensity = 60 * (0.5 + 0.5 * Math.sin(t * 8));
  });

  // ================================================================= CELULAR
  const celular = new THREE.Group();
  const aneis = [];
  {
    const corpo = new THREE.Mesh(new RoundedBoxGeometry(1.7, 3.4, 0.2, 6, 0.2), M.preto);
    const telaTex = canvasTex(520, 1060, (g, w, h) => {
      const gr = g.createLinearGradient(0, 0, 0, h);
      gr.addColorStop(0, "#2a2114"); gr.addColorStop(0.55, "#120e09"); gr.addColorStop(1, "#060505");
      g.fillStyle = gr; g.fillRect(0, 0, w, h);
      g.fillStyle = "#f3ebdd"; g.textAlign = "center";
      g.font = "600 30px Oswald"; g.globalAlpha = 0.7; g.fillText("19:24", w / 2, 70); g.globalAlpha = 1;
      g.font = "600 34px Oswald"; g.fillStyle = "#e9a513"; g.fillText("CHAMANDO…", w / 2, 220);
      g.beginPath(); g.arc(w / 2, 420, 120, 0, TAU); g.fillStyle = "#e9a513"; g.fill();
      g.lineWidth = 10; g.strokeStyle = "#f3ebdd"; g.stroke();
      g.fillStyle = "#0d0d0d"; g.font = "700 170px UnifrakturCook"; g.textBaseline = "middle"; g.fillText("H", w / 2, 432);
      g.textBaseline = "alphabetic"; g.fillStyle = "#f3ebdd"; g.font = "400 76px Anton"; g.fillText("AMIGO DO HERO", w / 2, 640);
      g.font = "600 32px Oswald"; g.globalAlpha = 0.75; g.fillText("quer saber como você tá", w / 2, 700); g.globalAlpha = 1;
      const bot = (x, cor, rot) => {
        g.beginPath(); g.arc(x, 905, 66, 0, TAU); g.fillStyle = cor; g.fill();
        g.save(); g.translate(x, 905); g.rotate(rot); g.fillStyle = "#fff";
        g.beginPath(); g.ellipse(0, 0, 34, 14, 0, Math.PI, TAU); g.fill(); g.fillRect(-36, -4, 18, 16); g.fillRect(18, -4, 18, 16); g.restore();
      };
      bot(140, "#c9302c", Math.PI); bot(380, "#2e9d4f", 0);
    });
    const tela = new THREE.Mesh(new THREE.PlaneGeometry(1.56, 3.2), new THREE.MeshBasicMaterial({ map: telaTex, toneMapped: false }));
    tela.position.z = 0.102;
    const vidroT = new THREE.Mesh(new THREE.PlaneGeometry(1.56, 3.2), new THREE.MeshPhysicalMaterial({ color: 0xffffff, transparent: true, opacity: 0.08, roughness: 0.02, metalness: 0, clearcoat: 1 }));
    vidroT.position.z = 0.104;
    const ilha = new THREE.Mesh(new RoundedBoxGeometry(0.42, 0.1, 0.02, 2, 0.04), M.pretoFosco);
    ilha.position.set(0, 1.47, 0.106);
    celular.add(corpo, tela, vidroT, ilha);
    [[0.86, 0.9, 0.5], [-0.86, 1.0, 0.3], [-0.86, 0.6, 0.3]].forEach(([x, y, h]) => {
      const b = new THREE.Mesh(new RoundedBoxGeometry(0.04, h, 0.08, 2, 0.015), M.aco);
      b.position.set(x, y, 0);
      celular.add(b);
    });
    for (let i = 0; i < 3; i++) {
      const a = new THREE.Mesh(new THREE.TorusGeometry(1.9, 0.025, 8, 96), new THREE.MeshBasicMaterial({ color: 0xe9a513, transparent: true, opacity: 0, depthWrite: false }));
      a.scale.y = 1.6;
      a.position.z = -0.3;
      celular.add(a);
      aneis.push(a);
    }
  }
  const vibrando = (t) => {
    const jan = [[27.75, 29.6], [31.75, 34.6]];
    for (const [a, b] of jan) if (t >= a && t < b) return ((t - a) % 0.7) < 0.42 ? 1 : 0;
    return 0;
  };
  const tocando = (t) => (dentro(t, 27.6, 29.75) || dentro(t, 31.6, 34.75) ? 1 : 0);
  const CEL_Y = U(0, 990)[1];
  const tAmigo = W(10, "Amigo");
  add(celular, (t) => {
    celular.visible = dentro(t, 27.0, 35.4);
    if (!celular.visible) return;
    const v = vibrando(t);
    celular.position.set(0.03 * Math.sin(t * TAU * 27) * v, K(t, [[27.0, -8], [27.55, CEL_Y, "outB"]]), K(t, [[34.95, 0], [35.35, -9, "inC"]]));
    celular.rotation.set(0.08 * Math.sin(t * 0.8), K(t, [[27.0, -1.0], [27.55, -0.3, "outC"], [tAmigo - 0.1, -0.3], [tAmigo + 0.3, 0, "outB"], [31.6, 0], [32.0, 0.22, "ioC"]]) + 0.06 * Math.sin(t * 1.1), 0.025 * Math.sin(t * TAU * 31) * v);
    celular.scale.setScalar(K(t, [[tAmigo - 0.1, 1], [tAmigo + 0.3, 1.08, "outB"], [31.6, 1.08], [32.0, 1, "ioC"]]));
    const on = tocando(t);
    aneis.forEach((a, i) => {
      const ph = (t * 1.3 + i / 3) % 1;
      a.scale.set(0.55 + ph * 0.9, (0.55 + ph * 0.9) * 1.6, 1);
      a.material.opacity = on * (1 - ph) * 0.7;
    });
  });

  // ================================================================= CADEADO
  const cadeado = new THREE.Group();
  const argola = new THREE.Group();
  {
    const corpo = new THREE.Mesh(new RoundedBoxGeometry(1.5, 1.2, 0.55, 5, 0.14), M.mostardaMetal);
    const fur = new THREE.Shape();
    fur.absarc(0, 0.08, 0.13, 0, TAU, false);
    const furo = new THREE.Mesh(new THREE.ExtrudeGeometry(fur, { depth: 0.04, bevelEnabled: false }), M.preto);
    furo.position.z = 0.27;
    const fenda = new THREE.Mesh(new THREE.BoxGeometry(0.09, 0.32, 0.04), M.preto);
    fenda.position.set(0, -0.12, 0.29);
    const arco = new THREE.Mesh(new THREE.TorusGeometry(0.47, 0.11, 20, 48, Math.PI), M.aco);
    arco.position.y = 0.55;
    const pe1 = new THREE.Mesh(new THREE.CylinderGeometry(0.11, 0.11, 0.5, 24), M.aco);
    pe1.position.set(-0.47, 0.3, 0);
    const pe2 = pe1.clone();
    pe2.position.x = 0.47;
    argola.add(arco, pe1, pe2);
    cadeado.add(argola, corpo, furo, fenda);
    const b = sprite(brilhoTex("#e9a513"), 4.5, 4.5);
    b.position.z = -1; b.material.opacity = 0.45;
    cadeado.add(b);
  }
  const tAi = W(12, "Aí"), tEra = W(12, "era");
  const CAD_Y = U(0, 900)[1];
  add(cadeado, (t) => {
    cadeado.visible = dentro(t, tAi - 0.15, 36.75);
    if (!cadeado.visible) return;
    cadeado.position.set(K(t, [[36.35, 0], [36.75, -5, "inC"]]), K(t, [[tAi - 0.15, 7.5], [tAi + 0.3, CAD_Y, "outBounce"]]) + mola(t, tEra, 0.06, 30, 9), 0);
    cadeado.rotation.set(0.12, -0.35 + 0.1 * Math.sin(t * 1.2) + K(t, [[36.35, 0], [36.75, -1.5, "inC"]]), mola(t, tEra, 0.05, 26, 7));
    argola.position.y = K(t, [[tEra - 0.06, 0.5], [tEra + 0.04, 0, "inE"]]);
    cadeado.scale.setScalar(1.05);
  });

  // ================================================================= PLACA DE SAÍDA
  const saida = new THREE.Group();
  let saidaMat, saidaHalo;
  {
    const caixa = new THREE.Mesh(new RoundedBoxGeometry(2.8, 1.18, 0.3, 4, 0.06), M.cinzaEsc);
    const tex = canvasTex(1024, 420, (g, w, h) => {
      g.fillStyle = "#0b9444"; g.fillRect(0, 0, w, h);
      g.fillStyle = "#f4fff6";
      g.font = "400 210px Anton"; g.textBaseline = "middle"; g.textAlign = "left";
      g.fillText("SAÍDA", 330, h / 2 + 10);
      // pictograma: pessoa correndo
      g.save(); g.translate(170, h / 2); g.lineCap = "round"; g.lineJoin = "round"; g.strokeStyle = "#f4fff6"; g.lineWidth = 30;
      g.beginPath(); g.arc(30, -120, 30, 0, TAU); g.fill();
      g.beginPath(); g.moveTo(10, -70); g.lineTo(-20, 30); g.lineTo(-80, 120); g.moveTo(-20, 30); g.lineTo(50, 70); g.lineTo(40, 140);
      g.moveTo(5, -60); g.lineTo(-70, -30); g.lineTo(-100, 20); g.moveTo(5, -60); g.lineTo(60, -10); g.lineTo(110, -40); g.stroke();
      g.restore();
      g.lineWidth = 14; g.strokeStyle = "#f4fff6"; g.strokeRect(14, 14, w - 28, h - 28);
    });
    saidaMat = new THREE.MeshStandardMaterial({ map: tex, emissiveMap: tex, emissive: 0xffffff, emissiveIntensity: 0.55, roughness: 0.4 });
    const frente = new THREE.Mesh(new THREE.PlaneGeometry(2.6, 1.0), saidaMat);
    frente.position.z = 0.152;
    saidaHalo = sprite(brilhoTex("#22e070"), 6, 3.6);
    saidaHalo.position.z = 0.4;
    saida.add(caixa, frente, saidaHalo);
    const haste = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 1.4, 8), M.aco);
    haste.position.set(-0.9, 1.25, -0.05);
    const haste2 = haste.clone(); haste2.position.x = 0.9;
    saida.add(haste, haste2);
  }
  const tNao13 = W(13, "Não"), tSumir = W(13, "sumir");
  const pisca = (t) => {
    // padrão determinístico de falha de energia
    const r = rng(Math.floor(t * 30) + 77)();
    return r > 0.82 ? 0.15 : r > 0.7 ? 0.6 : 1;
  };
  const SAI_Y = U(0, 830)[1];
  add(saida, (t) => {
    saida.visible = dentro(t, 36.3, 38.6);
    if (!saida.visible) return;
    saida.position.set(K(t, [[36.3, 5.5], [36.7, 0, "outB"]]), SAI_Y - (t > tSumir ? 0.12 * E.outBounce(P(t, tSumir, tSumir + 0.4)) : 0), 0);
    saida.rotation.set(0.05, -0.25 + 0.08 * Math.sin(t * 1.4), t > tSumir ? 0.1 * E.outBounce(P(t, tSumir, tSumir + 0.45)) + mola(t, tSumir + 0.45, 0.03, 10, 3) : 0);
    let k = 1;
    if (t >= tNao13 + 0.3 && t < tSumir) k = pisca(t);
    if (t >= tSumir) k = t < tSumir + 0.08 ? 1.6 : 0.0;
    saidaMat.emissiveIntensity = 0.55 * k;
    saidaMat.color.setScalar(0.12 + 0.88 * Math.min(1, k));
    saidaHalo.material.opacity = 0.7 * Math.min(1, k);
  });

  // ================================================================= VIRADA: objetos congelados e sem cor
  const congelados = new THREE.Group();
  {
    const peao = new THREE.Group();
    peao.add(new THREE.Mesh(geoPeao, M.cinza));
    const cab = new THREE.Mesh(geoCabeca, M.cinza); cab.position.y = 1.08; peao.add(cab);
    const cel = new THREE.Mesh(new RoundedBoxGeometry(1.7, 3.4, 0.2, 6, 0.2), M.cinzaEsc);
    const cad = new THREE.Group();
    cad.add(new THREE.Mesh(new RoundedBoxGeometry(1.5, 1.2, 0.55, 5, 0.14), M.cinza));
    const arc2 = new THREE.Mesh(new THREE.TorusGeometry(0.47, 0.11, 20, 48, Math.PI), M.cinzaEsc); arc2.position.y = 0.55; cad.add(arc2);
    const q = texto3d("?", FA, 1, 0.35, M.cinza, 0.04); alturaPara(q, 1.3);
    const casaC = new THREE.Group();
    const cc = new THREE.Mesh(new THREE.BoxGeometry(2.4, 1.45, 1.8), M.cinza); cc.position.y = 0.72; casaC.add(cc);
    const trC = new THREE.Shape(); trC.moveTo(-1.38, 0); trC.lineTo(1.38, 0); trC.lineTo(0, 1.05); trC.closePath();
    const tlc = new THREE.Mesh(new THREE.ExtrudeGeometry(trC, { depth: 2.1, bevelEnabled: false }), M.cinzaEsc); tlc.position.set(0, 1.45, -1.05); casaC.add(tlc);
    const cap = capacete(M.cinza, M.cinzaEsc);
    const lista = [
      [cap, 190, 400, -2.5, 0.95, [0.3, 0.6, 0.1]],
      [cel, 890, 470, -3.5, 0.62, [0.1, -0.5, 0.2]],
      [casaC, 860, 1360, -3.0, 0.62, [0.25, -0.7, 0.0]],
      [cad, 200, 1330, -1.8, 0.9, [0.2, 0.5, -0.15]],
      [q, 560, 1660, -4.0, 0.8, [0, 0.3, 0.25]],
      [peao, 130, 940, -3.5, 1.0, [0.2, 0.3, 0.2]],
    ];
    lista.forEach(([o, x, y, z, s, rot]) => {
      const piv = new THREE.Group();
      piv.add(o);
      const [ux, uy] = U(x, y);
      const f = 14 / (14 - z); // compensa a perspectiva para cair no pixel pedido
      piv.userData = { base: [ux / f, uy / f, z], rot, s };
      congelados.add(piv);
    });
  }
  const tVai = W(15, "vai");
  add(congelados, (t) => {
    congelados.visible = dentro(t, 38.6, 45.4);
    if (!congelados.visible) return;
    const choque = mola(t, tVai + 0.02, 0.35, 9, 3.5);
    congelados.children.forEach((p, i) => {
      const d = p.userData;
      const dir = Math.hypot(d.base[0], d.base[1]) || 1;
      const k = 1 + choque / dir;
      p.position.set(d.base[0] * k, d.base[1] * k + 0.04 * Math.sin(t * 0.4 + i), d.base[2]);
      p.rotation.set(d.rot[0] + 0.02 * (t - 38.6), d.rot[1] + 0.03 * (t - 38.6), d.rot[2]);
      p.scale.setScalar(d.s * K(t, [[38.6, 1.08], [39.4, 1, "outC"]]));
    });
  });
  const placaNV = new THREE.Group();
  {
    const ext = new THREE.Mesh(extr(retArred(3.1, 1.7, 0.18), 0.16, 0.03), M.preto);
    const inn = new THREE.Mesh(extr(retArred(2.82, 1.42, 0.12), 0.05, 0.015), M.mostarda);
    inn.position.z = 0.17;
    const txt = texto3d("NÃO VÁ", FA, 1, 0.12, M.preto, 0.012);
    alturaPara(txt, 0.98);
    txt.position.set(0, -0.02, 0.3);
    const poste = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 7, 20), M.aco);
    poste.position.set(0, -4.3, -0.15);
    const g = new THREE.Group();
    g.add(ext, inn, txt);
    g.position.y = 0;
    placaNV.add(g, poste);
    // centraliza a placa (o ExtrudeGeometry nasce em z>=0)
    ext.position.z = -0.08; inn.position.z = 0.09; txt.position.z = 0.22;
  }
  const NV_Y = U(0, 900)[1];
  add(placaNV, (t) => {
    placaNV.visible = dentro(t, tVai - 0.3, 45.4);
    if (!placaNV.visible) return;
    placaNV.position.set(0, K(t, [[tVai - 0.3, 9], [tVai + 0.02, NV_Y, "inC"]]) + (t > tVai ? -0.18 * Math.exp(-(t - tVai) * 8) * Math.abs(Math.sin((t - tVai) * 22)) : 0), 0.4);
    placaNV.rotation.set(0.04, -0.12 + 0.04 * Math.sin(t), mola(t, tVai + 0.02, 0.1, 13, 3.2));
  });

  // ================================================================= MEDALHÃO "H" (o risco)
  const medalhao = new THREE.Group();
  {
    const disco = new THREE.Mesh(new THREE.CylinderGeometry(1.55, 1.55, 0.24, 96), [M.preto, M.cremeBrilho, M.cremeBrilho]);
    disco.rotation.x = Math.PI / 2;
    const aro = new THREE.Mesh(new THREE.TorusGeometry(1.55, 0.11, 20, 120), M.preto);
    const aroIn = new THREE.Mesh(new THREE.TorusGeometry(1.38, 0.025, 10, 120), M.preto);
    aroIn.position.z = 0.125;
    const geoH = new THREE.ExtrudeGeometry(formasDe(window.FORMAS3D.H.formas), { depth: 0.12, bevelEnabled: true, bevelThickness: 0.02, bevelSize: 0.012, bevelSegments: 2, curveSegments: 6 });
    geoH.center();
    const h1 = new THREE.Mesh(geoH, M.preto);
    h1.scale.setScalar(0.92);
    h1.position.z = 0.17;
    const h2 = h1.clone();
    h2.rotation.y = Math.PI;
    h2.position.z = -0.17;
    const aroIn2 = aroIn.clone(); aroIn2.position.z = -0.125;
    medalhao.add(disco, aro, aroIn, aroIn2, h1, h2);
    const b = sprite(brilhoTex("#fff2c8"), 6, 6);
    b.position.z = -1.2; b.material.opacity = 0.5;
    medalhao.add(b);
  }
  const MED_Y = U(0, 820)[1];
  add(medalhao, (t) => {
    medalhao.visible = dentro(t, 45.4, 48.02);
    if (!medalhao.visible) return;
    medalhao.position.set(0, MED_Y + 0.06 * Math.sin(t * 2), K(t, [[47.55, 0], [48.0, 12.5, "inE"]]));
    medalhao.scale.setScalar(Math.max(0.001, K(t, [[45.4, 0.2], [45.85, 1, "outB"]])));
    medalhao.rotation.y = K(t, [[45.4, 10 * Math.PI], [47.25, 0, "outC"]]) + mola(t, 47.25, 0.12, 14, 5);
    medalhao.rotation.x = 0.08 * Math.sin(t * 1.3);
  });

  // ================================================================= LOGOMARCA HERO (adesivo 3D)
  const logo = new THREE.Group();
  {
    const L = window.FORMAS3D.logo;
    const hh = L.h / L.w;
    const geo = new THREE.ExtrudeGeometry(formasDe(L.formas), { depth: 0.16, bevelEnabled: true, bevelThickness: 0.025, bevelSize: 0.012, bevelSegments: 2, curveSegments: 4 });
    const pos = geo.attributes.position, uv = geo.attributes.uv;
    for (let i = 0; i < pos.count; i++) uv.setXY(i, (pos.getX(i) + 1) / 2, (pos.getY(i) + hh) / (2 * hh));
    uv.needsUpdate = true;
    const tex = await new Promise((ok) => new THREE.TextureLoader().load("assets/brand/logo_hero_face.png", ok));
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.anisotropy = 8;
    const face = new THREE.MeshBasicMaterial({ map: tex, toneMapped: false });
    const m = new THREE.Mesh(geo, [face, M.preto]);
    m.position.z = -0.08;
    logo.add(m);
    logo.userData.larg = 2;
  }
  const LOGO_Y = U(0, 470)[1];
  const tHero = W(17, "Hero");
  add(logo, (t) => {
    logo.visible = dentro(t, 48.0, 56.35);
    if (!logo.visible) return;
    const s = 1.72 * (1 + 0.07 * Math.max(0, Math.sin(P(t, tHero, tHero + 0.3) * Math.PI)));
    logo.scale.setScalar(s);
    logo.position.set(0, LOGO_Y, K(t, [[48.0, 11], [48.32, 0, "outE"]]));
    logo.rotation.set(0.07 * Math.sin(t * 0.7), K(t, [[48.0, -1.2], [48.6, 0, "outC"]]) + 0.16 * Math.sin((t - 48) * 0.9), mola(t, 48.32, 0.05, 16, 5));
  });

  // ================================================================= ÍCONES DO CONVITE: calendário, relógio, pin
  const ICX = U(215, 0)[0];
  // calendário
  const calendario = new THREE.Group();
  const folhas = [];
  {
    const base = new THREE.Mesh(new RoundedBoxGeometry(1.2, 1.25, 0.2, 4, 0.06), M.cremeBrilho);
    const topo = new THREE.Mesh(new RoundedBoxGeometry(1.2, 0.34, 0.24, 4, 0.06), M.preto);
    topo.position.y = 0.46;
    calendario.add(base, topo);
    [-0.32, 0.32].forEach((x) => {
      const a = new THREE.Mesh(new THREE.TorusGeometry(0.09, 0.025, 10, 24), M.aco);
      a.position.set(x, 0.66, 0.06);
      a.rotation.y = Math.PI / 2;
      calendario.add(a);
    });
    const pagina = (dia, sab) => canvasTex(256, 220, (g, w, h) => {
      g.fillStyle = "#f3ebdd"; g.fillRect(0, 0, w, h);
      g.fillStyle = "#0d0d0d"; g.textAlign = "center"; g.textBaseline = "middle";
      g.font = "400 150px Anton"; g.fillText(dia, w / 2, sab ? 128 : 118);
      g.font = "800 40px 'Barlow Condensed'"; g.fillStyle = sab ? "#c98a12" : "#555";
      g.fillText(sab ? "SÁBADO" : "OUT", w / 2, sab ? 30 : 205);
    });
    const topoTex = canvasTex(256, 72, (g, w, h) => {
      g.fillStyle = "#0d0d0d"; g.fillRect(0, 0, w, h);
      g.fillStyle = "#e9a513"; g.font = "400 50px Anton"; g.textAlign = "center"; g.textBaseline = "middle"; g.fillText("OUTUBRO", w / 2, h / 2 + 2);
    });
    const tt = new THREE.Mesh(new THREE.PlaneGeometry(1.1, 0.3), new THREE.MeshBasicMaterial({ map: topoTex, toneMapped: false }));
    tt.position.set(0, 0.46, 0.125);
    calendario.add(tt);
    const fundo = new THREE.Mesh(new THREE.PlaneGeometry(1.08, 0.93), new THREE.MeshStandardMaterial({ map: pagina("24", true), roughness: 0.7 }));
    fundo.position.set(0, -0.15, 0.104);
    calendario.add(fundo);
    ["20", "21", "22", "23"].forEach((d, i) => {
      const piv = new THREE.Group();
      piv.position.set(0, 0.315, 0.106 + (4 - i) * 0.002);
      const f = new THREE.Mesh(new THREE.PlaneGeometry(1.08, 0.93), new THREE.MeshStandardMaterial({ map: pagina(d, false), roughness: 0.7, side: THREE.DoubleSide }));
      f.position.y = -0.465;
      piv.add(f);
      calendario.add(piv);
      folhas.push(piv);
    });
  }
  const tSab = W(18, "Sábado"), t24 = W(18, "24"), tAs = W(18, "às"), tMeia = W(18, "meia"), tAv = W(19, "Avenida");
  const R1 = U(0, 868)[1], R2 = U(0, 1110)[1], R3 = U(0, 1368)[1];
  add(calendario, (t) => {
    calendario.visible = dentro(t, tSab - 0.05, 56.35);
    if (!calendario.visible) return;
    calendario.position.set(ICX, R1 + 0.04 * Math.sin(t * 1.6), K(t, [[tSab - 0.05, 7], [tSab + 0.3, 0, "outB"]]));
    calendario.rotation.set(0.1, K(t, [[tSab - 0.05, 1.3], [tSab + 0.45, 0, "outC"]]) + 0.22 * Math.sin(t * 0.8 + 1), mola(t, t24, 0.08, 18, 6));
    calendario.scale.setScalar(0.74 * (1 + mola(t, t24, 0.08, 20, 7)));
    folhas.forEach((f, i) => {
      const a = tSab + 0.12 + i * 0.13;
      f.rotation.x = -K(t, [[a, 0], [a + 0.22, Math.PI * 0.95, "inC"]]);
      f.visible = t < a + 0.22;
    });
  });
  // relógio
  const relogio = new THREE.Group();
  const ponteiros = {};
  {
    const face = new THREE.Mesh(new THREE.CylinderGeometry(0.62, 0.62, 0.12, 64), [M.preto, M.cremeBrilho, M.cremeBrilho]);
    face.rotation.x = Math.PI / 2;
    const aro = new THREE.Mesh(new THREE.TorusGeometry(0.62, 0.075, 16, 72), M.preto);
    relogio.add(face, aro);
    for (let i = 0; i < 12; i++) {
      const a = (i * TAU) / 12;
      const m = new THREE.Mesh(new THREE.BoxGeometry(i % 3 ? 0.03 : 0.05, i % 3 ? 0.08 : 0.13, 0.02), M.preto);
      m.position.set(Math.sin(a) * 0.49, Math.cos(a) * 0.49, 0.07);
      m.rotation.z = -a;
      relogio.add(m);
    }
    const ph = new THREE.Group(), pmn = new THREE.Group();
    const hm = new THREE.Mesh(new RoundedBoxGeometry(0.06, 0.32, 0.025, 2, 0.01), M.preto); hm.position.y = 0.13;
    const mm = new THREE.Mesh(new RoundedBoxGeometry(0.04, 0.46, 0.025, 2, 0.01), M.preto); mm.position.y = 0.2;
    ph.add(hm); pmn.add(mm);
    ph.position.z = 0.085; pmn.position.z = 0.1;
    const centro = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 0.05, 20), M.ouro);
    centro.rotation.x = Math.PI / 2; centro.position.z = 0.12;
    relogio.add(ph, pmn, centro);
    ponteiros.h = ph; ponteiros.m = pmn;
  }
  add(relogio, (t) => {
    relogio.visible = dentro(t, tAs - 0.1, 56.35);
    if (!relogio.visible) return;
    relogio.position.set(ICX, R2 + 0.04 * Math.sin(t * 1.6 + 1), K(t, [[tAs - 0.1, 7], [tAs + 0.22, 0, "outB"]]));
    relogio.rotation.set(0.12, -0.35 + 0.2 * Math.sin(t * 0.8 + 2), 0);
    relogio.scale.setScalar(0.82 * (1 + mola(t, tMeia + 0.12, 0.08, 20, 7)));
    const u = E.outC(P(t, tAs, tMeia + 0.12));
    ponteiros.m.rotation.z = -(u * (3 * TAU + Math.PI));
    ponteiros.h.rotation.z = -(u * (7.5 / 12) * TAU);
  });
  // pin
  const pin = new THREE.Group();
  let pinSombra;
  {
    // perfil em gota: ponta em y=0, bulbo de raio .42 centrado em y=.92
    const pts = [];
    for (let i = 0; i <= 48; i++) {
      const th = (i / 48) * Math.PI; // 0 = topo, PI = base do bulbo
      if (th < Math.PI * 0.78) pts.push(new THREE.Vector2(Math.sin(th) * 0.42 + 0.0001, 0.92 + Math.cos(th) * 0.42));
    }
    const last = pts[pts.length - 1];
    for (let i = 1; i <= 12; i++) { const u = i / 12; pts.push(new THREE.Vector2(last.x * (1 - u) + 0.0001, last.y * (1 - u))); }
    pts.reverse();
    const corpo = new THREE.Mesh(new THREE.LatheGeometry(pts, 48), M.preto);
    const furo = new THREE.Mesh(new THREE.SphereGeometry(0.16, 24, 16), M.mostarda);
    furo.position.set(0, 0.95, 0.33);
    furo.scale.z = 0.4;
    pin.add(corpo, furo);
    pin.children.forEach((c) => (c.position.y -= 0.68));
    pinSombra = sprite(texSombra, 1.1, 0.4, false);
  }
  cena.add(pinSombra);
  add(pin, (t) => {
    const vis = dentro(t, tAv - 0.1, 56.35);
    pin.visible = vis; pinSombra.visible = vis;
    if (!vis) return;
    const y = K(t, [[tAv - 0.1, 6.5], [tAv + 0.42, 0, "outBounce"]]);
    pin.position.set(ICX, R3 + y + 0.08, 0);
    pin.rotation.y = t * 1.2;
    pin.scale.setScalar(0.66);
    pinSombra.position.set(ICX, R3 - 0.4, -0.05);
    const s = 1 - Math.min(1, y / 3) * 0.6;
    pinSombra.scale.set(s, s, 1);
    pinSombra.material.opacity = s;
  });

  // ================================================================= CARIMBO 3D (final)
  const carimbo = new THREE.Group();
  {
    const madeira = new THREE.MeshStandardMaterial({ color: 0x7a4a22, roughness: 0.55, metalness: 0.05 });
    const base = new THREE.Mesh(new RoundedBoxGeometry(1.9, 0.95, 0.42, 4, 0.06), madeira);
    const borracha = new THREE.Mesh(new RoundedBoxGeometry(1.84, 0.89, 0.08, 2, 0.02), M.pretoFosco);
    borracha.position.z = -0.24;
    const pescoco = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.24, 0.8, 32), madeira);
    pescoco.rotation.x = Math.PI / 2;
    pescoco.position.z = 0.6;
    const pomo = new THREE.Mesh(new THREE.SphereGeometry(0.42, 40, 24), M.preto);
    pomo.position.z = 1.15;
    pomo.scale.z = 0.8;
    const anel = new THREE.Mesh(new THREE.TorusGeometry(0.2, 0.04, 12, 32), M.ouro);
    anel.position.z = 0.82;
    carimbo.add(base, borracha, pescoco, pomo, anel);
  }
  const CAR = U(760, 820);
  const TC = 59.25;
  add(carimbo, (t) => {
    carimbo.visible = dentro(t, 58.85, 59.8);
    if (!carimbo.visible) return;
    const z = K(t, [[58.85, 13], [TC, 0.25, "inC"], [TC + 0.08, 0.25], [59.8, 13.5, "inC"]]);
    const sq = t >= TC && t < TC + 0.1 ? 1 - 0.12 * Math.sin(P(t, TC, TC + 0.1) * Math.PI) : 1;
    carimbo.position.set(CAR[0], CAR[1], z);
    carimbo.scale.set(1, 1, sq);
    carimbo.rotation.set(0.45, -0.3, -0.24);
  });

  // ------------------------------------------------------------------ render
  function render(t) {
    objs.forEach((x) => x.up(t));
    // respiração sutil da câmera
    cam.position.set(0.05 * Math.sin(t * 0.37), 0.04 * Math.sin(t * 0.29), 14);
    cam.lookAt(0, 0, 0);
    // luz de recorte acompanha a cor de cada cena
    const amarelo = t >= 45.4;
    luzRecorte.color.setHex(dentro(t, 24.4, 38.6) ? 0xff3a2a : 0xe9a513);
    hemi.intensity = amarelo ? 1.0 : 0.6;
    luzChave.intensity = amarelo ? 2.6 : 2.2;
    renderer.render(cena, cam);
  }
  return { render };
}
