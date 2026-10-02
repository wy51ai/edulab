// Usage:
//   node render.mjs stills auto            -> build/stills/<scene>_<line>.png: one frame near the END of every
//                                             narration line (all of that line's animation should be on screen)
//   node render.mjs stills 5,30.5,60       -> build/stills/t<ms>.png at those seconds
//   node render.mjs motion                 -> build/motion_report.txt: does the FIGURE (left half) actually change
//                                             during every narration line? exit 1 if a line is static or a scene
//                                             never has sustained motion (see reference/visual-design.md)
//   node render.mjs video [workers]        -> ../<output_name>.mp4   (workers = parallel browser pages, NOT fps;
//                                             fps is fixed at 30. 4-8 is sensible.)
//   node render.mjs video 4 --fresh --preset medium  -> force a rebuild with legacy compression
import { chromium } from 'playwright';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import ffmpeg from 'ffmpeg-static';
import { measureMotion } from './motion_measure.mjs';
import { resolveMotionRegions } from './motion_regions.mjs';
import { videoOptions } from './render_options.mjs';
import { inputKey, cacheHit, saveCache } from './render_cache.mjs';

const ROOT = path.dirname(fileURLToPath(import.meta.url));
const BUILD = path.join(ROOT, 'build');
const CONFIG = JSON.parse(fs.readFileSync(path.join(ROOT, 'episode.json'), 'utf8'));
const { figure: FIG, board: BOARD } = resolveMotionRegions(CONFIG);
const mode = process.argv[2] || 'stills';
if (!['stills','motion','video'].includes(mode)) throw new Error('Unknown rendering mode: '+mode);
const OPTIONS = mode === 'video' ? videoOptions(process.argv.slice(3)) : null;
const TL = JSON.parse(fs.readFileSync(path.join(BUILD, 'timeline.json'), 'utf8'));
fs.writeFileSync(path.join(BUILD, 'timeline.js'), 'window.TIMELINE=' + JSON.stringify(TL) + ';');
const URL_ = pathToFileURL(path.join(ROOT, 'index.html')).href + '?render=1';
const FPS = 30;
const FFMPEG = process.env.FFMPEG_BINARY || ffmpeg;
const OUT = path.join(ROOT, '..', CONFIG.output_name + '.mp4');
if (mode === 'video' && TL.preview_only) throw new Error('Preview-only timeline: generate real audio before exporting video.');
const CACHE = path.join(BUILD,'render-cache.json');
const CACHE_SETTINGS = mode === 'video' ? {
  workers:OPTIONS.workers,preset:OPTIONS.preset,fps:FPS,crf:18,jpeg:.93,width:1920,height:1080,
  ffmpeg:FFMPEG,ffmpegSize:fs.statSync(FFMPEG).size,ffmpegModified:fs.statSync(FFMPEG).mtimeMs
} : null;
let KEY = null;
if (OPTIONS) {
  try { KEY = inputKey(ROOT,CACHE_SETTINGS,OUT); }
  catch (error) { console.warn('Render cache disabled: input scan failed:',error.message); }
}
if (OPTIONS && KEY !== null && !OPTIONS.fresh && cacheHit(CACHE,KEY,OUT)) {
  console.log('CACHE HIT: unchanged local inputs; reused verified output',OUT);
  process.exit(0);
}
let ERRORS = 0;  // JS errors in anim.js/engine.js: a frame with an error is silently incomplete

async function openPage(browser) {
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  page.on('pageerror', e => { ERRORS++; console.error('PAGE ERROR', e.message); });
  page.on('console', m => { if (m.type() === 'error') { ERRORS++; console.error('console:', m.text()); } });
  await page.goto(URL_);
  await page.evaluate(() => window.ready);
  return page;
}
// Export the native canvas pixels directly; locator screenshots wait on browser layout each frame.
const canvasShot = async page => Buffer.from(await page.evaluate(() =>
  document.getElementById('c').toDataURL('image/jpeg', .93).split(',')[1]), 'base64');

function run(args) {
  return new Promise((res, rej) => {
    const p = spawn(FFMPEG, args, { stdio: ['pipe', 'inherit', 'inherit'] });
    p.on('close', c => (c === 0 ? res() : rej(new Error('ffmpeg ' + c))));
    p.on('error', rej);
  });
}

async function renderChunk(browser, f0, f1, file, id) {
  const page = await openPage(browser);
  const ff = spawn(FFMPEG, ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', OPTIONS.preset, '-crf', '18', '-pix_fmt', 'yuv420p', '-r', String(FPS), file], { stdio: ['pipe', 'inherit', 'inherit'] });
  const done = new Promise((res, rej) => ff.on('close', c => (c === 0 ? res() : rej(new Error('ffmpeg chunk ' + c)))));
  const t0 = Date.now();
  for (let f = f0; f < f1; f++) {
    await page.evaluate(t => window.renderFrame(t), f / FPS);
    const buf = await canvasShot(page);
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if ((f - f0) % 300 === 0) console.log(`[w${id}] ${f - f0}/${f1 - f0}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
  ff.stdin.end();
  await done;
  await page.close();
}

// file access flags: lets `motion` read pixels of a canvas that has problem.png drawn on it (file:// taints it otherwise)
const ARGS = ['--font-render-hinting=none', '--allow-file-access-from-files', '--disable-web-security'];
let browser;
try {
  browser = await chromium.launch({ channel: 'chrome', args: ARGS });
} catch (e) {  // no Google Chrome installed: use Playwright's own Chromium (npx playwright install chromium)
  browser = await chromium.launch({ args: ARGS });
}
if (mode === 'motion') {
  const page = await openPage(browser);
  await page.evaluate(() => { window.NO_BOIL = true; });  // freeze the hand-drawn wobble so only real changes count
  const exempt = new Set(CONFIG.static_ok || []);
  const first = TL.scenes[0].id, last = TL.scenes[TL.scenes.length - 1].id;
  const rows = [], problems = [];
  for (const sc of TL.scenes) {
    const skip = sc.id === first || sc.id === last || exempt.has(sc.id);
    let moving = 0;
    for (const [k, ln] of sc.lines.entries()) {
      // Sample only speech time; a deliberate thinking pause is allowed to hold still.
      const N = 6, a = ln.start + 0.05, b = Math.max(a + 0.1, ln.end - 0.05);
      const times = Array.from({ length: N }, (_, i) => a + (b - a) * i / (N - 1));
      const { steps, net, board } = await page.evaluate(measureMotion, { times, regions: [FIG, BOARD] });
      const active = steps.filter(v => v > 0.1).length;
      const kind = Math.max(net, ...steps) < 0.15 ? 'STATIC' : active >= 3 ? 'MOVE' : 'POP';
      if (kind === 'MOVE') moving++;
      const key = `${sc.id} ${k}`;
      const bad = !skip && !exempt.has(key) && kind === 'STATIC';
      if (bad) problems.push(`[${key}] figure does not change during this line: "${ln.zh}"`);
      rows.push(`${bad ? '✗' : ' '} [${key}] ${kind.padEnd(6)} figure ${net.toFixed(2).padStart(6)}%  steps ${steps.map(v => v.toFixed(1)).join('/')}  board ${board.toFixed(2)}%${skip ? '  (exempt scene)' : ''}`);
    }
    if (!skip && !moving) problems.push(`[${sc.id}] no line has sustained motion (MOVE): add a slide / morph / camera move / moving point`);
  }
  const rep = rows.join('\n') + '\n\nSTATIC = figure unchanged, POP = things appear, MOVE = continuous motion through the line\n'
    + (problems.length ? 'PROBLEMS:\n' + problems.join('\n') : 'motion check passed') + '\n';
  fs.writeFileSync(path.join(BUILD, 'motion_report.txt'), rep);
  console.log(rep);
  if (problems.length) process.exitCode = 1;
} else if (mode === 'stills') {
  const dir = path.join(BUILD, 'stills');
  fs.mkdirSync(dir, { recursive: true });
  const page = await openPage(browser);
  const arg = process.argv[3] || 'auto';
  const shots = arg === 'auto'
    ? TL.scenes.flatMap((sc, i) => sc.lines.map((ln, k) => [Math.max(ln.start + 0.3, ln.end - 0.15), `${String(i + 1).padStart(2, '0')}_${sc.id}_${k}`]))
      .concat([[TL.duration - 1.6, 'zz_end']])
    : arg.split(',').map(Number).map(t => [t, `t${String(Math.round(t * 1000)).padStart(7, '0')}`]);
  if (arg === 'auto') for (const f of fs.readdirSync(dir)) if (f.endsWith('.png')) fs.rmSync(path.join(dir, f));
  for (const [t, name] of shots) {
    await page.evaluate(tt => window.renderFrame(tt), t);
    const f = path.join(dir, `${name}.png`);
    await page.locator('#c').screenshot({ path: f });
    console.log(f);
  }
} else {
  const workers = OPTIONS.workers;
  console.log(`Video: ${workers} workers, ${OPTIONS.preset} preset, 1080p30, CRF18`);
  const total = Math.ceil(TL.duration * FPS);
  const per = Math.ceil(total / workers);
  const chunks = [];
  for (let i = 0; i < workers; i++) {
    const f0 = i * per, f1 = Math.min(total, (i + 1) * per);
    if (f0 < f1) chunks.push({ f0, f1, file: path.join(BUILD, `chunk${i}.mp4`), id: i });
  }
  const t0 = Date.now();
  await Promise.all(chunks.map(c => renderChunk(browser, c.f0, c.f1, c.file, c.id)));
  console.log('frames done in', ((Date.now() - t0) / 1000).toFixed(0), 's');
  const list = path.join(BUILD, 'chunks.txt');
  // FFmpeg concat syntax uses backslash as an escape, including on Windows.
  fs.writeFileSync(list, chunks.map(c => `file '${c.file.replace(/\\/g, '/').replace(/'/g, "'\\''")}'`).join('\n'));
  await run(['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', list, '-i', path.join(BUILD, 'mix.wav'),
    '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', '-ar', '48000', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart',
    '-metadata', 'title=' + CONFIG.title, OUT]);
  for (const c of chunks) fs.rmSync(c.file, { force: true });  // intermediate chunks are no longer needed
  fs.rmSync(list, { force: true });
  if (!ERRORS && KEY !== null) {
    try {
      if (inputKey(ROOT,CACHE_SETTINGS,OUT) === KEY) saveCache(CACHE,KEY,OUT);
      else console.warn('Render inputs changed during export; output was not cached. Rebuild before delivery.');
    } catch (error) { console.warn('Video exported, but its cache could not be saved:',error.message); }
  }
  console.log('WROTE', OUT);
}
await browser.close();
if (ERRORS) { console.error(`FAILED: ${ERRORS} page error(s) above. Fix anim.js before trusting any frame.`); process.exitCode = 1; }
