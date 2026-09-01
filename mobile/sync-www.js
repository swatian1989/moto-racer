// Copies the game out of the repo root into www/, which is what Capacitor
// packs into the APK. The game files stay at the root because that is what
// GitHub Pages serves, so the two builds never diverge.
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const out = path.join(__dirname, 'www');
const ASSETS = ['index.html', 'manifest.json', 'sw.js', 'icon.svg', 'icons', 'vendor'];

fs.rmSync(out, { recursive: true, force: true });
fs.mkdirSync(out, { recursive: true });

let bytes = 0;
for (const name of ASSETS) {
  const src = path.join(root, name);
  if (!fs.existsSync(src)) throw new Error('missing asset: ' + src);
  fs.cpSync(src, path.join(out, name), { recursive: true });
}
for (const dir of [out]) {
  const walk = (d) => fs.readdirSync(d, { withFileTypes: true }).forEach((e) => {
    const p = path.join(d, e.name);
    e.isDirectory() ? walk(p) : (bytes += fs.statSync(p).size);
  });
  walk(dir);
}
console.log('www/ ready: %d assets, %s KB', ASSETS.length, (bytes / 1024).toFixed(0));
