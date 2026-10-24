// Gera capa_reel.png (1080x1920) e a prévia do recorte 4:5 do perfil.  Uso: node capa/shot.mjs
import { chromium } from "/opt/node22/lib/node_modules/playwright/index.mjs";
import { fileURLToPath } from "url";
import path from "path";
const dir = path.dirname(fileURLToPath(import.meta.url));
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
await p.goto("file://" + path.join(dir, "capa.html"));
await p.evaluate(() => document.fonts.ready);
await p.waitForTimeout(400);
await p.screenshot({ path: path.join(dir, "../qa/capa_reel.png") });
await p.screenshot({ path: path.join(dir, "../qa/capa_previa_grade_4x5.png"), clip: { x: 0, y: 285, width: 1080, height: 1350 } });
await b.close();
console.log("capa ok");
