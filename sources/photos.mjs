import { chromium } from 'playwright-core';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const racine = process.cwd();
const types = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.glb': 'model/gltf-binary' };
const srv = http.createServer((q, r) => {
  const f = path.join(racine, decodeURIComponent(new URL(q.url, 'http://x').pathname));
  if (!f.startsWith(racine) || !fs.existsSync(f)) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { 'content-type': types[path.extname(f)] || 'application/octet-stream' }); fs.createReadStream(f).pipe(r);
}).listen(8765, '127.0.0.1');
const vues = JSON.parse(process.argv[2]);
const [L, H] = (process.argv[3] || '2400x1600').split('x').map(Number);
// Chrome à utiliser : CHROME=… (sur Mac : "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome").
// Sous Linux sans carte graphique, rendu logiciel SwiftShader : lancer avec AA=0 et une taille double, puis réduire (voir README).
const CHROME = process.env.CHROME || '/opt/pw-browsers/chromium';
const nav = await chromium.launch({ executablePath: CHROME, args: process.platform === 'linux' ? ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] : [] });
const page = await nav.newPage({ viewport: { width: L, height: H } });
page.on('console', m => { if (m.type() === 'error') console.log('console:', m.text()); });
page.on('pageerror', e => console.log('pageerror:', e.message));
await page.goto('http://127.0.0.1:8765/scene.html' + (process.env.AA === '0' ? '?aa=0' : ''));
await page.waitForFunction(() => window.pret === true, null, { timeout: 180000 });
const DOS = process.env.DOS || 'photos'; fs.mkdirSync(DOS, { recursive: true });
for (const [nom, v] of Object.entries(vues)) {
  const t = Date.now();
  await page.evaluate(v => window.rendre(v), v);
  await page.locator('canvas').screenshot({ path: `${DOS}/${nom}.png` });
  console.log(nom, ((Date.now() - t) / 1000).toFixed(1) + ' s');
}
await nav.close(); srv.close();
