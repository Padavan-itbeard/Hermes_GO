// Ivy — local server. No dependencies. node server.js [studyDir] [port]
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path'; import { fileURLToPath } from 'node:url';
const HERE = path.dirname(fileURLToPath(import.meta.url));
let ROOT = path.resolve(process.argv[2] || process.env.IVY_DIR || path.join(HERE, 'study'));
const PORT = +(process.argv[3] || process.env.IVY_PORT || 4317);
const clients = new Set(); let state = { mode: 'empty', path: null, history: [], pos: -1 };
const SERVER_ID = Date.now().toString(36) + Math.random().toString(36).slice(2);
const send = (ev, data) => {
  const s = `event: ${ev}\ndata: ${JSON.stringify(data)}\n\n`;
  for (const client of [...clients]) {
    try { client.write(s); } catch { clients.delete(client); }
  }
};
let watcher = null;
function startWatcher() {
  if (watcher) { try { watcher.close(); } catch {} }
  try {
    watcher = fs.watch(ROOT, { recursive: true }, (_, f) => f && send('change', { path: f.split(path.sep).join('/') }));
  } catch {}
}
startWatcher();
const safe = p => { const f = path.resolve(ROOT, p || ''); if (!f.startsWith(ROOT)) throw new Error('outside study dir'); return f; };
const modeOf = p => {
  if (!p) return 'lecture';
  if (p.endsWith('.md')) return 'lecture';
  if (/quiz/i.test(p)) return 'quiz';
  if (/card/i.test(p)) return 'cards';
  try {
    const raw = fs.readFileSync(safe(p), 'utf-8');
    const parsed = JSON.parse(raw);
    if (parsed.questions) return 'quiz';
    if (parsed.cards || Array.isArray(parsed)) return 'cards';
  } catch {}
  return 'lecture';
};
function tree(dir = ROOT) {
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir, { withFileTypes: true })
    .filter(d => !d.name.startsWith('.'))
    .sort((a, b) => a.name.localeCompare(b.name))
    .map(d => {
      const fullPath = path.join(dir, d.name);
      if (d.isDirectory()) {
        const children = tree(fullPath);
        return children.length ? { name: d.name, type: 'dir', children } : null;
      }
      if (/\.(md|json)$/i.test(d.name)) {
        const rel = path.relative(ROOT, fullPath).split(path.sep).join('/');
        const kind = d.name.endsWith('.md') ? 'lecture' : modeOf(rel);
        return { name: d.name, path: rel, type: 'file', kind };
      }
      return null;
    }).filter(Boolean);
}
function open(p, mode) {
  if (!p) return { ok: false, error: 'path is required' };
  let abs;
  try { abs = safe(p); } catch (e) { return { ok: false, error: e.message }; }
  if (!fs.existsSync(abs) || fs.statSync(abs).isDirectory()) return { ok: false, error: `not found: ${p}` };
  const rel = path.relative(ROOT, abs).split(path.sep).join('/');
  state.lastResult = null;
  state.history = state.history.slice(0, state.pos + 1);
  state.history.push({ path: rel, mode: mode || modeOf(rel) });
  state.history = state.history.slice(-10);
  state.pos = state.history.length - 1;
  Object.assign(state, state.history[state.pos]);
  send('state', state);
  return { ok: true, path: rel, mode: state.mode };
}
function move(d) { const n = state.pos + d; if (n < 0 || n >= state.history.length) return { ok: false, error: 'no history' };
  state.pos = n; Object.assign(state, state.history[n]); send('state', state); return { ok: true }; }
const body = req => new Promise(r => { let b = ''; req.on('data', c => b += c); req.on('end', () => { try { r(JSON.parse(b || '{}')) } catch { r({}) } }); });
http.createServer(async (req, res) => {
  const u = new URL(req.url, 'http://x');
  const j = (o, c = 200) => {
    if (res.headersSent) return;
    res.writeHead(c, { 'content-type': 'application/json' });
    res.end(JSON.stringify(o));
  };
  try {
    if (u.pathname === '/events') {
      res.writeHead(200, { 'content-type': 'text/event-stream', 'cache-control': 'no-cache', 'connection': 'keep-alive' });
      clients.add(res);
      res.write(`event: hello\ndata: ${JSON.stringify({ serverId: SERVER_ID, root: ROOT, name: path.basename(ROOT) })}\n\n`);
      res.write(`event: state\ndata: ${JSON.stringify({ ...state, workspace: ROOT, workspaceName: path.basename(ROOT) })}\n\n`);
      req.on('close', () => clients.delete(res));
      return;
    }
    if (u.pathname === '/api/tree') return j(tree());
    if (u.pathname === '/api/state') return j({ ...state, workspace: ROOT, workspaceName: path.basename(ROOT), clients: clients.size });
    if (u.pathname === '/api/workspace') {
      if (req.method === 'POST') {
        const { path: p } = await body(req);
        if (!p) return j({ ok: false, error: 'path required' }, 400);
        const target = path.resolve(p);
        if (!fs.existsSync(target) || !fs.statSync(target).isDirectory()) {
          return j({ ok: false, error: `directory not found: ${p}` }, 400);
        }
        ROOT = target;
        startWatcher();
        state = { mode: 'empty', path: null, history: [], pos: -1, lastResult: null };
        send('workspace', { root: ROOT, name: path.basename(ROOT) });
        send('state', { ...state, workspace: ROOT, workspaceName: path.basename(ROOT) });
        send('change', { path: '' });
        return j({ ok: true, root: ROOT, name: path.basename(ROOT) });
      }
      return j({ ok: true, root: ROOT, name: path.basename(ROOT) });
    }
    if (u.pathname === '/api/file') {
      const p = u.searchParams.get('p');
      if (!p) return j({ ok: false, error: 'param p required' }, 400);
      const target = safe(p);
      if (!fs.existsSync(target) || fs.statSync(target).isDirectory()) {
        return j({ ok: false, error: `not found: ${p}` }, 404);
      }
      const content = fs.readFileSync(target);
      res.writeHead(200, { 'content-type': 'text/plain; charset=utf-8' });
      return res.end(content);
    }
    if (u.pathname === '/api/cmd' && req.method === 'POST') {
      const { cmd, path: p } = await body(req);
      if (cmd === 'open' || cmd === 'quiz' || cmd === 'cards') return j(open(p, cmd === 'open' ? null : cmd));
      if (cmd === 'back') return j(move(-1)); if (cmd === 'forward') return j(move(1));
      return j({ ok: false, error: 'unknown cmd' }, 400);
    }
    if (u.pathname === '/api/result' && req.method === 'POST') { state.lastResult = await body(req); return j({ ok: true }); }
    if (u.pathname === '/api/notify' && req.method === 'POST') {
      const data = await body(req);
      send('notify', data);
      return j({ ok: true });
    }
    const UI = path.join(HERE, 'ui'), f = path.resolve(UI, '.' + (u.pathname === '/' ? '/index.html' : decodeURIComponent(u.pathname)));
    if (!f.startsWith(UI)) throw new Error('forbidden');
    const content = fs.readFileSync(f);
    const T = { html: 'text/html; charset=utf-8', js: 'text/javascript', css: 'text/css', woff2: 'font/woff2' };
    res.writeHead(200, { 'content-type': T[f.split('.').pop()] || 'application/octet-stream' });
    res.end(content);
  } catch (e) {
    if (!res.headersSent) j({ ok: false, error: e.message }, 404);
  }
}).listen(PORT, '127.0.0.1', () => console.log(`Ivy → http://localhost:${PORT}  (study: ${ROOT})`));
