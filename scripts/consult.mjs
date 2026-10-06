#!/usr/bin/env node
/* consult.mjs — консультация топ-моделью OpenRouter для книги (бюджет $10, контролируем).
   Использование:
     node scripts/consult.mjs consultations/request.md consultations/answer-<метка>.md [max_tokens]
   Ключ — в .env книги (OPENROUTER_KEY), в git не попадает.
   Каждая консультация дописывается в consultations/LOG.md с токенами и ценой. */
import { readFileSync, writeFileSync, appendFileSync, existsSync } from "node:fs";
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
const MODEL = "anthropic/claude-sonnet-4.5";
const maxTokens = Number(maxTokensArg || 12000);

const t0 = Date.now();
const res = await fetch("https://openrouter.ai/api/v1/chat/completions", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + key,
    "HTTP-Referer": "https://thinkred.ru/",
    "X-Title": "ThinkRed Book Consult",
  },
  body: JSON.stringify({
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
  }),
});
const data = await res.json();
if (!res.ok || !data.choices) {
  console.error("ОШИБКА OpenRouter:", JSON.stringify(data).slice(0, 500));
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
