<?php
/**
 * Приватный консультационный эндпоинт для платных моделей OpenRouter.
 * Проект: книга «Место Республики Беларусь в системе мирового империализма».
 *
 * ОТЛИЧИЕ от публичного /api/llm.php:
 *  - доступ только с секретом, разбитым на две половины в полях consult_token /
 *    consult_token2 тела запроса (ModSecurity хостинга блокирует длинные hex-строки
 *    и кастомные заголовки; секрет не публикуется в UI ассистента);
 *  - разрешены ТОЛЬКО платные топ-модели из $CONSULT_MODELS;
 *  - лимиты под консультации: max_tokens 16000, промпт до 300 000 знаков, таймаут 240 с;
 *  - каждый вызов логируется С ТОКЕНАМИ usage в admin/llm-usage/consult-usage.log
 *    (контроль бюджета: цель ≤ $10 на весь проект);
 *  - СУЩЕСТВУЕТ ВРЕМЕННО: удалить файл после завершения книги.
 *
 * Ключ переиспользуется из admin/llm-config.php и наружу не отдаётся.
 *
 * @package ThinkRed\BookConsult
 */

declare(strict_types=1);

header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');
header('Cache-Control: no-store');

/** Секрет доступа (генерируется при создании, хранится только здесь и у инициатора). */
$CONSULT_TOKEN = '{{CONSULT_TOKEN}}';

/** Разрешённые платные модели (цены OpenRouter проверяются при добавлении). */
$CONSULT_MODELS = [
    'anthropic/claude-sonnet-4.5',   // ~$3/$15 за 1M токенов
];

$LIMITS = ['max_tokens' => 16000, 'max_prompt_chars' => 300000, 'timeout_s' => 240];

$raw = file_get_contents('php://input', false, null, 0, 600000);
$req = json_decode((string) $raw, true);
if (!is_array($req)) {
    fail(400, 'Ожидается JSON с полями model и messages');
}

// Каналы секрета (WAF хостинга непредсказуемо режет X-* заголовки и длинные hex в теле,
// поэтому — стандартные механизмы): 1) Basic Auth (пароль = секрет), 2) cookie tk,
// 3) заголовок X-Consult-Token, 4) тело (две половины).
$token = '';
if (isset($_SERVER['PHP_AUTH_PW']) && $_SERVER['PHP_AUTH_USER'] === 'consult') {
    $token = (string) $_SERVER['PHP_AUTH_PW'];
} elseif (isset($_COOKIE['tk'])) {
    $token = (string) $_COOKIE['tk'];
} elseif (isset($_SERVER['HTTP_X_CONSULT_TOKEN'])) {
    $token = (string) $_SERVER['HTTP_X_CONSULT_TOKEN'];
} else {
    $token = (string) (($req['consult_token'] ?? '') . ($req['consult_token2'] ?? ''));
}
if ($token === '' || !hash_equals($CONSULT_TOKEN, $token)) {
    fail(403, 'Доступ запрещён');
}

require __DIR__ . '/../admin/llm-config.php'; // $LLM_API_KEY

if (($_SERVER['REQUEST_METHOD'] ?? 'GET') !== 'POST') {
    fail(405, 'Только POST');
}

$model = (string) ($req['model'] ?? '');
if (!in_array($model, $CONSULT_MODELS, true)) {
    fail(403, 'Модель не из консультационного списка: ' . implode(', ', $CONSULT_MODELS));
}

$messages = $req['messages'] ?? null;
if (!is_array($messages) || $messages === []) {
    fail(400, 'Поле messages обязательно');
}
$chars = 0;
$clean = [];
foreach ($messages as $m) {
    if (!is_array($m)) {
        continue;
    }
    $role = (string) ($m['role'] ?? 'user');
    if (!in_array($role, ['system', 'user', 'assistant'], true)) {
        $role = 'user';
    }
    $content = (string) ($m['content'] ?? '');
    $chars += strlen($content);
    $clean[] = ['role' => $role, 'content' => $content];
}
if ($chars > $LIMITS['max_prompt_chars']) {
    fail(413, 'Слишком длинный запрос: ' . $chars);
}

$maxTokens = (int) ($req['max_tokens'] ?? 8000);
$maxTokens = max(256, min($maxTokens, $LIMITS['max_tokens']));

$payload = json_encode([
    'model' => $model,
    'messages' => $clean,
    'temperature' => isset($req['temperature']) ? (float) $req['temperature'] : 0.4,
    'max_tokens' => $maxTokens,
], JSON_UNESCAPED_UNICODE);

$ch = curl_init('https://openrouter.ai/api/v1/chat/completions');
curl_setopt_array($ch, [
    CURLOPT_POST => true,
    CURLOPT_POSTFIELDS => $payload,
    CURLOPT_HTTPHEADER => [
        'Authorization: Bearer ' . $LLM_API_KEY,
        'Content-Type: application/json',
        'HTTP-Referer: https://thinkred.ru/',
        'X-Title: ThinkRed Book Consult',
    ],
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_TIMEOUT => $LIMITS['timeout_s'],
    CURLOPT_CONNECTTIMEOUT => 15,
]);
$body = curl_exec($ch);
$code = (int) curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
curl_close($ch);

if ($body === false || $code !== 200) {
    fail(502, 'OpenRouter ' . $code . ': ' . substr((string) $body, 0, 500));
}

// Лог с токенами — контроль бюджета проекта.
$u = json_decode((string) $body, true);
$usage = $u['usage'] ?? [];
$store = __DIR__ . '/../admin/llm-usage';
if (!is_dir($store)) {
    @mkdir($store, 0770, true);
}
@file_put_contents($store . '/consult-usage.log',
    sprintf("%s model=%s prompt_tokens=%s completion_tokens=%s total_tokens=%s\n",
        gmdate('c'), $model,
        (string) ($usage['prompt_tokens'] ?? '?'),
        (string) ($usage['completion_tokens'] ?? '?'),
        (string) ($usage['total_tokens'] ?? '?')),
    FILE_APPEND | LOCK_EX);

http_response_code(200);
echo $body;

function fail(int $code, string $msg): void
{
    http_response_code($code);
    echo json_encode(['error' => ['message' => $msg, 'type' => 'thinkred_consult']],
        JSON_UNESCAPED_UNICODE);
    exit;
}
