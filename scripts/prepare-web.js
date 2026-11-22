const fs = require('node:fs');
const path = require('node:path');
const root = process.cwd();
const out = path.join(root, 'www');
fs.rmSync(out, { recursive: true, force: true });
fs.mkdirSync(out, { recursive: true });
fs.copyFileSync(path.join(root, 'index.html'), path.join(out, 'index.html'));
for (const name of ['manifest.webmanifest', 'sw.js']) {
  const source = path.join(root, name);
  if (fs.existsSync(source)) fs.copyFileSync(source, path.join(out, name));
}
const assets = path.join(root, 'assets');
if (fs.existsSync(assets)) fs.cpSync(assets, path.join(out, 'assets'), { recursive: true });
console.log('Prepared web assets in www/');
