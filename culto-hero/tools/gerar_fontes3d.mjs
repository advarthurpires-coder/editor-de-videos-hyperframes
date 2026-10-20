// Converte as fontes (WOFF, licença OFL) para o formato "typeface" do Three.js (FontLoader/TextGeometry),
// só com os caracteres usados no reel. Gera assets/fontes3d.js (window.FONTES3D = {...}).
// Uso: node tools/gerar_fontes3d.mjs <pasta_node_modules_com_opentype_e_@fontsource>
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";

const nm = process.argv[2];
const require = createRequire(path.join(nm, "x.js"));
const opentype = require("opentype.js");

const FONTES = {
  gotica: { arq: "@fontsource/unifrakturcook/files/unifrakturcook-latin-700-normal.woff", chars: "0123456789H" },
  anton: {
    arq: "@fontsource/anton/files/anton-latin-400-normal.woff",
    chars: "ABCDEFGHIJKLMNOPQRSTUVWXYZÁÃÂÉÊÍÓÕÔÚÇ0123456789!?:.,-/ ",
  },
};

function typeface(font, chars) {
  const escala = 1000 / font.unitsPerEm;
  const r = (v) => Math.round(v * escala);
  const glyphs = {};
  for (const ch of chars) {
    const g = font.charToGlyph(ch);
    const cmds = g.getPath(0, 0, font.unitsPerEm).commands;
    // opentype devolve y para baixo (coordenadas de tela): inverter
    const o = [];
    for (const c of cmds) {
      if (c.type === "M") o.push("m", r(c.x), r(-c.y));
      else if (c.type === "L") o.push("l", r(c.x), r(-c.y));
      else if (c.type === "Q") o.push("q", r(c.x), r(-c.y), r(c.x1), r(-c.y1));
      else if (c.type === "C") o.push("b", r(c.x), r(-c.y), r(c.x1), r(-c.y1), r(c.x2), r(-c.y2));
    }
    const bb = g.getBoundingBox();
    glyphs[ch] = { ha: r(g.advanceWidth), x_min: r(bb.x1), x_max: r(bb.x2), o: o.join(" ") };
  }
  return {
    glyphs,
    familyName: font.names.fontFamily.en,
    ascender: r(font.ascender),
    descender: r(font.descender),
    underlinePosition: r(font.tables.post.underlinePosition),
    underlineThickness: r(font.tables.post.underlineThickness),
    boundingBox: { xMin: r(font.tables.head.xMin), yMin: r(font.tables.head.yMin), xMax: r(font.tables.head.xMax), yMax: r(font.tables.head.yMax) },
    resolution: 1000,
    original_font_information: { format: 0, copyright: font.names.copyright?.en || "", license: "SIL Open Font License 1.1" },
  };
}

const saida = {};
for (const [nome, f] of Object.entries(FONTES)) {
  const buf = fs.readFileSync(path.join(nm, f.arq));
  const font = opentype.parse(buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength));
  saida[nome] = typeface(font, f.chars);
  console.log(nome, Object.keys(saida[nome].glyphs).length, "glifos");
}
fs.writeFileSync("assets/fontes3d.js", "window.FONTES3D = " + JSON.stringify(saida) + ";\n");
