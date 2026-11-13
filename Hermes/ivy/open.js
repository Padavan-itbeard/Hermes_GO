// Ядро открытия карточек в Ivy. Общее для всех агентов: Hermes, Athena, Chiron.
// Каждый агент зовёт openCards() из своего тонкого show.js, отличаются только папка карточек и имя в уведомлении.
//
// Ivy один на всех: сервер на порту 4317 обслуживает одну папку карточек за раз (workspace).
// Поэтому агент при открытии ВСЕГДА переключает workspace на свой: иначе второй агент за сессию
// падал бы с «port is busy with another Ivy workspace» уже после того, как записал файл карточек.
import { spawn, spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const PORT = +(process.env.IVY_PORT || 4317);
const BASE = `http://127.0.0.1:${PORT}`;

/**
 * @param {object} o
 * @param {string} o.anki    папка карточек этого агента (абсолютный путь)
 * @param {string} o.ivyDir  папка Ivy с server.js (абсолютный путь)
 * @param {string} o.agent   имя агента для заголовка уведомления
 * @param {string} o.dryEnv  имя переменной окружения для сухого прогона (стенд)
 */
export async function openCards({ anki, ivyDir, agent, dryEnv }) {
  const tag = agent.toLowerCase();
  const fail = msg => { console.error(`${tag}: ${msg}`); process.exit(1); };

  // --- Валидация файла ---
  const arg = process.argv[2];
  if (!arg) fail(`usage: node ${path.relative(process.cwd(), process.argv[1]).split(path.sep).join('/')} anki/<file>.json`);
  const file = path.resolve(arg);
  if (!file.startsWith(anki + path.sep)) fail(`file must be inside ${anki}`);
  if (!fs.existsSync(file)) fail(`not found: ${arg}`);

  let data;
  try { data = JSON.parse(fs.readFileSync(file, 'utf-8')); } catch (e) { fail(`invalid JSON: ${e.message}`); }
  const cards = data.cards;
  if (!Array.isArray(cards) || !cards.length) fail('JSON must have a non-empty "cards" array');
  const bad = cards.findIndex(c => !c.n || !c.question || !c.answer);
  if (bad !== -1) fail(`card #${bad + 1} must have "n", "question" and "answer"`);
  // Нумерация внутри файла должна идти по порядку и без повторов.
  const wrong = cards.findIndex((c, i) => i && c.n <= cards[i - 1].n);
  if (wrong !== -1) fail(`card "n" must increase: card #${wrong + 1} has n=${cards[wrong].n} after ${cards[wrong - 1].n}`);
  // Новые файлы нумеруются с 1: колоду ученик нумерует сам при переносе в Anki.
  // Старые файлы со сквозной нумерацией открываются как есть, только с пометкой.
  const legacy = cards[0].n !== 1 ? ` (сквозная нумерация, старый файл)` : '';
  const summary = `${cards.length} cards, ${cards[0].n}-${cards[cards.length - 1].n}${legacy}`;

  if (dryEnv && process.env[dryEnv]) { console.log(`ok (dry run): ${summary}`); process.exit(0); }
  if (process.env.IVY_DRY) { console.log(`ok (dry run): ${summary}`); process.exit(0); }

  // --- Сервер ---
  const state = async () => {
    try { return await (await fetch(`${BASE}/api/state`)).json(); } catch { return null; }
  };

  let st = await state();

  // Сервер не запущен — поднимаем сразу со своим workspace.
  if (!st) {
    const serverJs = path.join(ivyDir, 'server.js');
    if (!fs.existsSync(serverJs)) fail(`Ivy server not found: ${serverJs}`);
    launch([process.execPath, serverJs, anki, String(PORT)], ivyDir, fail);
    for (let i = 0; i < 50 && !(st = await state()); i++) await new Promise(r => setTimeout(r, 100));
    if (!st) fail('server did not start');
  }

  // Сервер занят чужой папкой карточек (другой агент в этой же сессии) — переключаем на свою.
  if (path.resolve(st.workspace) !== anki) {
    const r = await (await fetch(`${BASE}/api/workspace`, {
      method: 'POST', headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ path: anki }),
    })).json();
    if (!r.ok) fail(`cannot switch workspace to ${anki}: ${r.error}`);
    st = await state();
  }

  // --- Открыть файл ---
  const rel = path.relative(anki, file).split(path.sep).join('/');
  const r = await (await fetch(`${BASE}/api/cmd`, {
    method: 'POST', headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ cmd: 'cards', path: rel }),
  })).json();
  if (r.ok === false) fail(r.error);

  const url = `http://localhost:${PORT}`;
  // Вкладка Ivy уже открыта: сервер сам переключил её на карточки, новую не открываем.
  if (!st.clients) {
    launch(process.platform === 'win32' ? ['cmd', '/c', 'start', '', url]
      : process.platform === 'darwin' ? ['open', url] : ['xdg-open', url], ivyDir, fail);
  }

  // Звуковой сигнал на странице и системное уведомление Windows (клик открывает Ivy).
  await fetch(`${BASE}/api/notify`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: '{}' });
  const topic = data.topic || data.deck || 'Карточки';
  const message = `${cards.length} карточек готовы в Ivy`;
  let toast = 'skipped (not Windows)';
  if (process.platform === 'win32') toast = showToast(`${agent} · ${topic}`, message, url);
  console.log(`ok: opened in Ivy (${summary}), notification: ${toast}`);
}

// Запуск процесса, который переживёт завершение этой команды.
// Агенты (agy) держат команду в Windows Job и после её выхода убивают всё дерево, даже detached-процессы.
// Процесс, созданный через WMI, принадлежит службе WMI, а не нам, и в это задание не попадает.
function launch(argv, cwd, fail) {
  if (process.platform !== 'win32') {
    spawn(argv[0], argv.slice(1), { detached: true, stdio: 'ignore' }).unref();
    return;
  }
  const q = a => (/[\s"]/.test(a) || a === '' ? `"${a.replace(/"/g, '\\"')}"` : a);
  const ps = `$r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = '${argv.map(q).join(' ').replace(/'/g, "''")}'; CurrentDirectory = '${cwd.replace(/'/g, "''")}' }; exit $r.ReturnValue`;
  const r = spawnSync('powershell', ['-NoProfile', '-NonInteractive', '-EncodedCommand', Buffer.from(ps, 'utf16le').toString('base64')],
    { timeout: 20000, encoding: 'utf-8' });
  if (r.status !== 0) fail(`cannot launch ${argv[0]}: ${(r.stderr || r.error?.message || `code ${r.status}`).trim().split('\n')[0]}`);
}

function showToast(title, text, launchUrl) {
  const x = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  // scenario="reminder" держит баннер на экране, пока его не закроют (требует хотя бы одну кнопку).
  const xml = `<toast scenario="reminder" activationType="protocol" launch="${x(launchUrl)}"><visual><binding template="ToastGeneric">`
    + `<text>${x(title)}</text><text>${x(text)}</text></binding></visual>`
    + `<actions><action content="Открыть Ivy" activationType="protocol" arguments="${x(launchUrl)}"/>`
    + `<action content="Закрыть" activationType="system" arguments="dismiss"/></actions></toast>`;
  const ps = [
    '$null = [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime]',
    '$null = [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime]',
    '$xml = New-Object Windows.Data.Xml.Dom.XmlDocument',
    `$xml.LoadXml('${xml.replace(/'/g, "''")}')`,
    "$appId = '{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\\WindowsPowerShell\\v1.0\\powershell.exe'",
    '[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($appId).Show([Windows.UI.Notifications.ToastNotification]::new($xml))',
  ].join('\n');
  const r = spawnSync('powershell', ['-NoProfile', '-NonInteractive', '-EncodedCommand', Buffer.from(ps, 'utf16le').toString('base64')],
    { timeout: 15000, encoding: 'utf-8' });
  return r.status === 0 ? 'shown' : `failed (${(r.stderr || r.error?.message || '').trim().split('\n')[0]})`;
}
