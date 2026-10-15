// Gera saida/legendas.srt com os MESMOS blocos das legendas queimadas.
import fs from "node:fs";
import { buildBlocks } from "../src/captionBlocks.ts";

const words = JSON.parse(fs.readFileSync("src/data/words.json", "utf8"));
const blocks = buildBlocks(words);
const ts = (s: number) => {
  const ms = Math.round(s * 1000);
  const h = Math.floor(ms / 3600000), m = Math.floor((ms % 3600000) / 60000), sec = Math.floor((ms % 60000) / 1000);
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(sec).padStart(2, "0")},${String(ms % 1000).padStart(3, "0")}`;
};
const out = blocks.map((b, i) => `${i + 1}\n${ts(b.start)} --> ${ts(b.end)}\n${b.idx.map((k: number) => words[k].word).join(" ")}\n`).join("\n");
fs.writeFileSync("saida/legendas.srt", out);
console.log(blocks.length, "blocos");
