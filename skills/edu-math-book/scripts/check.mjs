#!/usr/bin/env node
/* Open a generated lesson page headless, collect errors / [lesson] warnings and screenshot every view.
   usage: node check.mjs out.html [--out shots_dir] [--only home|steps] [--w 1600 --h 1000]
   Needs `playwright` (or playwright-core) resolvable from the cwd, this skill, or a sibling edulab skill. */
import {createRequire} from 'node:module';
import {existsSync, mkdirSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf('--' + k); return i >= 0 ? args[i + 1] : d; };
const html = args.find(a => !a.startsWith('--') && !args[args.indexOf(a) - 1]?.startsWith('--'));
if (!html) { console.error('usage: node check.mjs out.html [--out dir] [--only home|steps]'); process.exit(2); }
const file = path.resolve(html), outDir = path.resolve(opt('out', path.join(path.dirname(file), '_check')));
const W = +opt('w', 1600), H = +opt('h', 1000), only = opt('only', 'all');

const here = path.dirname(fileURLToPath(import.meta.url));
const roots = [process.cwd(), path.join(here, '..'), path.join(here, '../../edu-math-video/lesson'), path.join(here, '../../edu-physics-video/lesson')];
let pw = null;
for (const r of roots) for (const name of ['playwright', 'playwright-core']) {
  if (pw) break;
  try { pw = createRequire(path.join(r, 'noop.js'))(name); } catch (e) {}
}
if (!pw) { console.error('playwright not found. Install it in the working directory:  npm i -D playwright-core  (and have Google Chrome, or run: npx playwright install chromium)'); process.exit(2); }

// --headless=new + Metal ANGLE: the old headless compositor drops parts of the CSS-3D book (stray cover-coloured patches)
const ARGS = ['--autoplay-policy=no-user-gesture-required', '--headless=new', ...(process.platform === 'darwin' ? ['--use-angle=metal'] : [])];
let browser;
try { browser = await pw.chromium.launch({channel: 'chrome', args: ARGS}); } catch (e) { browser = await pw.chromium.launch({args: ARGS}); }
const ctx = await browser.newContext({viewport: {width: W, height: H}, deviceScaleFactor: 1});
const page = await ctx.newPage();
const logs = [];
page.on('console', m => { if (['error', 'warning'].includes(m.type()) || m.text().startsWith('[lesson]')) logs.push(`${m.type()}: ${m.text()}`); });
page.on('pageerror', e => logs.push('pageerror: ' + e.message));
mkdirSync(outDir, {recursive: true});
const url = pathToFileURL(file).href, wait = ms => page.waitForTimeout(ms), shots = [], perf = [];

async function open(hash) {
  await page.goto('about:blank');
  await page.goto(url + hash, {waitUntil: 'load'});
  await page.evaluate(() => document.fonts && document.fonts.ready);
}
await open('');
const info = await page.evaluate(() => { const L = typeof LESSON !== 'undefined' ? LESSON : {}; return {parts: (L.parts || []).map(p => p.steps.length), intro: !!document.getElementById('introUi'), fig: L.figure?.type}; });
if (only !== 'steps') {
  if (info.intro) {
    await wait(1200); await page.screenshot({path: path.join(outDir, '00_intro.png')}); shots.push('00_intro.png');
    await page.evaluate(() => document.getElementById('introSkip')?.click()); await wait(3600);
  } else await wait(1500);
  await page.screenshot({path: path.join(outDir, '01_home.png')}); shots.push('01_home.png');
  // hover each question to see the figure preview, then flip the answer flap
  const flap = await page.$('#seg1');
  if (flap) { await page.evaluate(() => { document.querySelector('.opt')?.click(); }); await flap.click({force: true}).catch(() => {}); await wait(900);
    await page.screenshot({path: path.join(outDir, '02_flap.png')}); shots.push('02_flap.png'); }
}
if (only !== 'home') {
  for (let p = 0; p < info.parts.length; p++) for (let s = 0; s < info.parts[p]; s++) {
    const step = `#demo${p + 1}-${s + 1}`;
    await open(step);
    await wait(+opt('wait', 7000));
    const name = `p${p + 1}_s${s + 1}.png`;
    await page.screenshot({path: path.join(outDir, name)}); shots.push(name);
    // flicker probe: circle the mouse so the parallax camera wobbles; a face near edge-on would toggle solid/dashed
    const emb = () => page.evaluate(() => ({...window.__emb, t: performance.now()}));
    const b = await emb();
    for (let k = 0; k <= 32; k++) { const t = k / 32 * 2 * Math.PI; await page.mouse.move(W / 2 + W * .45 * Math.cos(t), H / 2 + H * .45 * Math.sin(t)); await wait(60); }
    const e = await emb(), fps = (e.frames - b.frames) / ((e.t - b.t) / 1000);
    perf.push({step, fps: Math.round(fps)});
    if (e.flips > b.flips) logs.push(`[flicker] ${step}: ${e.flips - b.flips} edge visibility flips while the camera wobbled — a face is almost edge-on; turn spec.view by 10–20°`);
    if (fps < 15) logs.push(`[slow] ${step}: ~${Math.round(fps)} fps — heavy model()/curves (n) or too many marks`);
    // slider steps: sweep the whole parameter range to surface render errors
    const swept = await page.evaluate(async () => {
      const r = document.getElementById('range'), sl = document.getElementById('slider');
      if (!sl.classList.contains('show')) return false;
      const lo = +r.min, hi = +r.max, v0 = r.value;
      for (let i = 0; i <= 40; i++) { r.value = lo + (hi - lo) * i / 40; r.dispatchEvent(new Event('input')); await new Promise(f => setTimeout(f, 40)); }
      r.value = v0; r.dispatchEvent(new Event('input'));
      return true;
    });
    if (swept) await wait(400);
  }
}
await browser.close();
console.log(JSON.stringify({file, outDir, figure: info.fig, intro: info.intro, steps: info.parts, shots, fps: perf.map(x => `${x.step}:${x.fps}`).join(' '), problems: [...new Set(logs)]}, null, 2));
process.exit(logs.some(l => /^(pageerror|error)|\[(lesson|flicker|slow|render)\]/.test(l)) ? 1 : 0);
