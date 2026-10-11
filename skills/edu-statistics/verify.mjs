// 无头验证（统计）：零依赖 + canvas 非空白 + 拨滑块→绿色 + 拖柱顶→绿色 + 播放/暂停。
// 运行：node verify.mjs
import { createRequire } from 'module';
import { readdirSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const OUT = join(__dirname, 'output');
const SHOT = join(OUT, '_verify');

const require = createRequire('F:/desktop/PlayFamGo/.edulab-ws/package.json');
const { chromium } = require('playwright');

mkdirSync(SHOT, { recursive: true });

const files = readdirSync(OUT).filter(f => f.endsWith('.html')).sort();
if (!files.length) {
  console.error('没有找到 output/*.html，先运行 `python -B scripts/generate.py all`');
  process.exit(1);
}

let failures = 0;
const browser = await chromium.launch();

for (const f of files) {
  const url = 'file:///' + join(OUT, f).replace(/\\/g, '/');
  const page = await browser.newPage({ viewport: { width: 1200, height: 980 } });
  const errors = [];
  page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text().slice(0, 160)); });
  page.on('pageerror', e => errors.push('pageerror: ' + e.message.slice(0, 160)));
  page.on('requestfailed', r => errors.push('reqfail: ' + r.url().slice(0, 120)));

  let data;
  try {
    await page.goto(url, { waitUntil: 'load', timeout: 20000 });
    await page.waitForTimeout(600);
    data = await page.evaluate(() => JSON.parse(document.getElementById('lesson-data').textContent.trim()));
  } catch (e) {
    errors.push('goto/parse: ' + e.message.slice(0, 160));
  }

  const reqFails = errors.filter(e => e.startsWith('reqfail'));
  const ans = data ? data.scene.param.answer : null;

  // 1) canvas 非空白
  let nonBlank = null;
  if (data) {
    nonBlank = await page.evaluate(() => {
      const cv = document.getElementById('scene');
      const d = cv.getContext('2d').getImageData(0, 0, cv.width, cv.height).data;
      let n = 0;
      for (let i = 3; i < d.length; i += 4) if (d[i] > 0) n++;
      return n;
    });
  }

  // 2) 滑块 → 答案：状态变绿
  let meetOk = false, statusAt = '';
  if (data) {
    await page.evaluate(t => {
      const s = document.getElementById('slider');
      s.value = t; s.dispatchEvent(new Event('input'));
    }, ans);
    await page.waitForTimeout(120);
    statusAt = await page.evaluate(() => document.getElementById('status').className);
    meetOk = statusAt.includes('green');
  }

  // 3) 拖柱顶到答案：竖向拖（v-line）+ 读数正确 + 变绿
  let dragOk = null;
  if (data && data.scene.kind === 'chart') {
    const W = data.scene.world;
    const box = await (await page.$('#scene')).boundingBox();
    const pad = W.pad != null ? W.pad : 40;
    const u = Math.min((box.width - 2 * pad) / W.xMax, (box.height - 2 * pad) / W.yMax);
    const ox = (box.width - u * W.xMax) / 2, oy = (box.height - u * W.yMax) / 2;
    const X = x => ox + x * u, Y = y => oy + (W.yMax - y) * u;
    const barD = (data.scene.points || []).find(p => p.name === 'barD');
    await page.evaluate(() => { const s = document.getElementById('slider'); s.value = 0; s.dispatchEvent(new Event('input')); });
    await page.waitForTimeout(60);
    const from = { x: box.x + X(barD.x), y: box.y + Y(0) };
    const to = { x: box.x + X(barD.x), y: box.y + Y(ans) };
    await page.mouse.move(from.x, from.y);
    await page.mouse.down();
    await page.mouse.move(to.x, to.y, { steps: 8 });
    await page.mouse.up();
    await page.waitForTimeout(120);
    const dVal = await page.evaluate(() => {
      const els = document.querySelectorAll('#readouts .r-value');
      return els[3] ? els[3].textContent.trim() : '';
    });
    const st = await page.evaluate(() => document.getElementById('status').className);
    dragOk = dVal.startsWith(String(ans)) && st.includes('green');
    console.log(`  拖柱顶: 跑步读数 "${dVal}"（答案 ${ans}），状态 ${st}`);
  }

  // 3b) 树状图：拖手柄 cnt 到答案（横向 h-line）→ 变绿
  let treeOk = null;
  if (data && data.scene.kind === 'tree') {
    const W = data.scene.world;
    const box = await (await page.$('#scene')).boundingBox();
    const pad = W.pad != null ? W.pad : 40;
    const u = Math.min((box.width - 2 * pad) / W.xMax, (box.height - 2 * pad) / W.yMax);
    const ox = (box.width - u * W.xMax) / 2, oy = (box.height - u * W.yMax) / 2;
    const X = x => ox + x * u, Y = y => oy + (W.yMax - y) * u;
    const cnt = (data.scene.points || []).find(p => p.name === 'cnt');
    await page.evaluate(() => { const s = document.getElementById('slider'); s.value = s.min; s.dispatchEvent(new Event('input')); });
    await page.waitForTimeout(60);
    const from = { x: box.x + X(cnt.x), y: box.y + Y(cnt.y) };
    const to = { x: box.x + X(ans), y: box.y + Y(cnt.y) };
    await page.mouse.move(from.x, from.y);
    await page.mouse.down();
    await page.mouse.move(to.x, to.y, { steps: 8 });
    await page.mouse.up();
    await page.waitForTimeout(120);
    const st = await page.evaluate(() => document.getElementById('status').className);
    treeOk = st.includes('green');
    console.log(`  拖手柄→答案: 状态 ${st}`);
  }

  // 4) 播放 → 前进 → 暂停停住
  let playOk = false;
  if (data) {
    await page.evaluate(() => { const s = document.getElementById('slider'); s.value = 0; s.dispatchEvent(new Event('input')); });
    await page.click('#play');
    await page.waitForTimeout(900);
    const v1 = await page.evaluate(() => parseFloat(document.getElementById('slider').value));
    await page.click('#play');
    await page.waitForTimeout(150);
    const v2 = await page.evaluate(() => parseFloat(document.getElementById('slider').value));
    const v3 = await page.evaluate(() => parseFloat(document.getElementById('slider').value));
    playOk = v1 > 0 && v3 === v2;
  }

  const blankOk = nonBlank && nonBlank > 100;
  const ok = reqFails.length === 0 && blankOk && meetOk && playOk &&
             (dragOk === null || dragOk === true) && (treeOk === null || treeOk === true);
  if (!ok) failures++;

  await page.screenshot({ path: join(SHOT, f.replace('.html', '.png')) });

  console.log('=== ' + f + ' ===');
  console.log('  请求失败:', reqFails.length ? reqFails : '无');
  console.log('  canvas 非空白:', nonBlank, blankOk ? 'OK' : 'FAIL');
  console.log('  滑块→答案 状态:', statusAt, meetOk ? 'OK' : 'FAIL');
  if (dragOk !== null) console.log('  拖柱顶→答案:', dragOk ? 'OK' : 'FAIL');
  if (treeOk !== null) console.log('  拖手柄→答案:', treeOk ? 'OK' : 'FAIL');
  console.log('  播放/暂停:', playOk ? 'OK' : 'FAIL');
  if (errors.length) console.log('  其它错误:', errors.slice(0, 4));
  await page.close();
}

await browser.close();
console.log('\n' + (failures === 0 ? '✅ 全部 ' + files.length + ' 个 HTML 验证通过' : `❌ ${failures}/${files.length} 失败`));
process.exit(failures === 0 ? 0 : 1);
