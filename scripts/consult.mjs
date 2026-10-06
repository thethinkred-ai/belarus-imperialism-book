#!/usr/bin/env node
/* consult.mjs — консультация топ-моделью OpenRouter для книги (бюджет $10, контролируем).
   Использование:
     node scripts/consult.mjs consultations/request.md consultations/answer-<метка>.md [max_tokens]
   Ключ — в .env книги (OPENROUTER_KEY), в git не попадает.
   Запрос выполняется через curl (в локальной сети Node-fetch блокируется MITM-прокси).
   Каждая консультация логируется в consultations/LOG.md с токенами и ценой. */
import { readFileSync, writeFileSync, appendFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const [, , reqPath, outPath, maxTokensArg] = process.argv;
if (!reqPath || !outPath) {
  console.error("использование: node scripts/consult.mjs <request.md> <answer.md> [max_tokens]");
  process.exit(2);
}
const env = readFileSync(join(root, ".env"), "utf8");
const key = (env.match(/^OPENROUTER_KEY=(.*)$/m) || [])[1]?.trim();
if (!key) { console.error("нет OPENROUTER_KEY в .env"); process.exit(2); }

const prompt = readFileSync(join(root, reqPath), "utf8");
const MODEL = process.env.CONSULT_MODEL || "openai/gpt-6-astra-pro";
const maxTokens = Number(maxTokensArg || 12000);

const payload = JSON.stringify({
  model: MODEL,
  max_tokens: maxTokens,
  temperature: 0.4,
  messages: [
    { role: "system", content:
      "Ты — научный консультант марксистско-ленинского образовательного проекта ThinkRed. " +
      "Работаешь с исследовательским планом книги о месте современной Республики Беларусь " +
      "в системе мирового империализма. Строго по трудовой теории стоимости и «Империализму…» Ленина. " +
      "Не выдумывай цитат и статистики; непроверяемое помечай [источник]. Отвечай по-русски, структурно, по делу." },
    { role: "user", content: prompt },
  ],
});
const bodyFile = join(tmpdir(), "consult-body-" + Date.now() + ".json");
const resFile = bodyFile + ".res";
writeFileSync(bodyFile, payload);

const t0 = Date.now();
let raw;
try {
  raw = execFileSync("curl", [
    "-sS", "-X", "POST", "https://openrouter.ai/api/v1/chat/completions",
    "-H", "Content-Type: application/json",
    "-H", "Authorization: Bearer " + key,
    "-H", "HTTP-Referer: https://thinkred.ru/",
    "-H", "X-Title: ThinkRed Book Consult",
    "--data-binary", "@" + bodyFile,
    "--max-time", "600",
    "-o", resFile,
    "-w", "%{http_code}",
  ], { encoding: "utf8", maxBuffer: 64e6 });
} finally {
  try { writeFileSync(bodyFile + ".gone", ""); } catch (e) {}
}
const http = (raw || "").trim();
const body = readFileSync(resFile, "utf8");
const data = JSON.parse(body);
if (http !== "200" || !data.choices) {
  console.error("ОШИБКА OpenRouter HTTP " + http + ":", JSON.stringify(data).slice(0, 500));
  process.exit(1);
}
const text = data.choices[0].message.content;
const u = data.usage || {};
const logLine = [
  new Date().toISOString(), MODEL,
  "prompt=" + (u.prompt_tokens ?? "?"),
  "completion=" + (u.completion_tokens ?? "?"),
  "cost=$" + (u.cost ?? "?"),
  (Date.now() - t0) + "ms",
].join(" ");
appendFileSync(join(root, "consultations", "LOG.md"), logLine + "\n");
writeFileSync(join(root, outPath),
  `<!-- консультация ${new Date().toISOString()} · ${MODEL} · ${logLine} -->\n\n` + text + "\n");
console.log(logLine);
console.log("ответ:", outPath, "(" + text.length + " знаков)");
