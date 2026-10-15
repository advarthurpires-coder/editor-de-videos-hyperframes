// uso: node tools/stills.mjs <saida> <t1> <t2> ...   (segundos)  [env PROPS='{"captions":true}']
import { bundle } from "@remotion/bundler";
import { openBrowser, renderStill, selectComposition } from "@remotion/renderer";
import path from "node:path";
import fs from "node:fs";

const [out, ...times] = process.argv.slice(2);
fs.mkdirSync(out, { recursive: true });
const comp = process.env.COMP ?? "Reel";
const inputProps = JSON.parse(process.env.PROPS ?? '{"captions":true,"audio":false}');
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts"), publicDir: path.resolve("public") });
const browser = await openBrowser("chrome", {
  browserExecutable: "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell",
  chromiumOptions: { gl: "swangle" },
});
const composition = await selectComposition({ serveUrl, id: comp, inputProps, puppeteerInstance: browser });
const queue = times.map((s) => Math.round(parseFloat(s) * 30));
const worker = async () => {
  while (queue.length) {
    const frame = queue.shift();
    const file = path.join(out, `f${String(frame).padStart(4, "0")}_${(frame / 30).toFixed(2)}s.png`);
    await renderStill({ serveUrl, composition, frame, output: file, inputProps, puppeteerInstance: browser, chromiumOptions: { gl: "swangle" } });
    console.log(file);
  }
};
await Promise.all([worker(), worker(), worker()]);
await browser.close({ silent: true });
