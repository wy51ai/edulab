// 无头验证：零依赖（requestfailed=0）+ canvas 非空白 + 红/蓝实体存在 + 滑块交互。
// 运行：node verify.mjs   （依赖 .edulab-ws/node_modules 里的 playwright）
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

const RED = [226, 85, 63], BLUE = [59, 125, 216], TOL = 42;

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
  const hasDiagram = data && !!data.diagram;
  const targetT = data ? data.scene.param.answer : null;

  // 1) canvas 非空白（scene 必查，graph 仅在有 diagram 时查）
  let nonBlank = null;
  if (data) {
    nonBlank = await page.evaluate((hasDiagram) => {
      const ids = hasDiagram ? ['scene', 'graph'] : ['scene'];
      return ids.map(id => {
        const cv = document.getElementById(id);
        const d = cv.getContext('2d').getImageData(0, 0, cv.width, cv.height).data;
        let n = 0;
        for (let i = 3; i < d.length; i += 4) if (d[i] > 0) n++;
        return n;
      });
    }, hasDiagram);
  }

  // 2) 红/蓝实体存在（线段图两色块 / 运动两车）——在「分离」时刻采样，避开相遇重叠
  let colorOk = false;
  if (data) {
    const tSample = data.scene.param.min + (data.scene.param.answer - data.scene.param.min) * 0.4;
    await page.evaluate(t => {
      const s = document.getElementById('slider');
      s.value = t; s.dispatchEvent(new Event('input'));
    }, tSample);
    await page.waitForTimeout(80);
    colorOk = await page.evaluate(([RED, BLUE, TOL]) => {
      const cv = document.getElementById('scene');
      const d = cv.getContext('2d').getImageData(0, 0, cv.width, cv.height).data;
      let nr = 0, nb = 0;
      for (let i = 0; i < d.length; i += 4) {
        if (Math.abs(d[i] - RED[0]) < TOL && Math.abs(d[i + 1] - RED[1]) < TOL && Math.abs(d[i + 2] - RED[2]) < TOL) nr++;
        if (Math.abs(d[i] - BLUE[0]) < TOL && Math.abs(d[i + 1] - BLUE[1]) < TOL && Math.abs(d[i + 2] - BLUE[2]) < TOL) nb++;
      }
      return nr > 30 && nb > 30;
    }, [RED, BLUE, TOL]);
  }

  // 3) 滑块 → 答案：状态变绿
  let statusAt = '', meetOk = false;
  if (data) {
    await page.evaluate(t => {
      const s = document.getElementById('slider');
      s.value = t; s.dispatchEvent(new Event('input'));
    }, targetT);
    await page.waitForTimeout(120);
    statusAt = await page.evaluate(() => document.getElementById('status').className);
    meetOk = statusAt.includes('green');
  }

  // 4) 播放 → 前进 → 暂停停住
  let playOk = false;
  if (data) {
    await page.evaluate(() => { const s = document.getElementById('slider'); s.value = 0; s.dispatchEvent(new Event('input')); });
    await page.click('#play');
    await page.waitForTimeout(500);
    const v1 = await page.evaluate(() => parseFloat(document.getElementById('slider').value));
    await page.click('#play');
    await page.waitForTimeout(150);
    const v2 = await page.evaluate(() => parseFloat(document.getElementById('slider').value));
    const v3 = await page.evaluate(() => parseFloat(document.getElementById('slider').value));
    playOk = v1 > 0 && v3 === v2;
  }

  // 5) 拖拽交互（scene.dragToT 存在时）：真鼠标把手柄从 min 拖到答案，断言变绿
  //    h-line 沿水平拖（x 轴），v-line 沿竖直拖（y 轴）。
  let dragOk = null;
  if (data && data.scene.dragToT) {
    const W = data.scene.world;
    const hpt = (data.scene.points || []).find(p => p.name === data.scene.dragToT);
    if (W && hpt) {
      const ans = data.scene.param.answer;
      const vertical = hpt.constraint === "v-line";
      const box = await (await page.$('#scene')).boundingBox();
      const pad = W.pad != null ? W.pad : 40;
      const u = Math.min((box.width - 2 * pad) / W.xMax, (box.height - 2 * pad) / W.yMax);
      const ox = (box.width - u * W.xMax) / 2, oy = (box.height - u * W.yMax) / 2;
      const X = x => ox + x * u, Y = y => oy + (W.yMax - y) * u;
      await page.evaluate(() => { const s = document.getElementById('slider'); s.value = s.min; s.dispatchEvent(new Event('input')); });
      await page.waitForTimeout(60);
      const from = vertical
        ? { x: box.x + X(hpt.x), y: box.y + Y(parseFloat(data.scene.param.min)) }
        : { x: box.x + X(parseFloat(data.scene.param.min)), y: box.y + Y(hpt.y) };
      const to = vertical
        ? { x: box.x + X(hpt.x), y: box.y + Y(ans) }
        : { x: box.x + X(ans), y: box.y + Y(hpt.y) };
      await page.mouse.move(from.x, from.y);
      await page.mouse.down();
      await page.mouse.move(to.x, to.y, { steps: 6 });
      await page.mouse.up();
      await page.waitForTimeout(120);
      dragOk = await page.evaluate(() => document.getElementById('status').className.includes('green'));
    }
  }

  // 5b) 多点拖拽（logic-table / tianji 等多 point 且无 dragToT）：逐点拖到 ax/ay，断言变绿
  let multiDragOk = null;
  if (data && !data.scene.dragToT && (data.scene.points || []).length) {
    const pts = data.scene.points;
    if (pts.length && pts[0].ax != null) {
      await page.reload({ waitUntil: 'load', timeout: 20000 });
      await page.waitForTimeout(600);
      await page.evaluate(() => {
        const s = document.getElementById('slider');
        s.value = s.min; s.dispatchEvent(new Event('input'));
      });
      await page.waitForTimeout(60);
      const W = data.scene.world;
      const box = await (await page.$('#scene')).boundingBox();
      const pad = W.pad != null ? W.pad : 40;
      const u = Math.min((box.width - 2 * pad) / W.xMax, (box.height - 2 * pad) / W.yMax);
      const ox = (box.width - u * W.xMax) / 2, oy = (box.height - u * W.yMax) / 2;
      const X = x => ox + x * u, Y = y => oy + (W.yMax - y) * u;
      for (const p of pts) {
        const from = { x: box.x + X(p.x), y: box.y + Y(p.y) };
        const to = { x: box.x + X(p.ax), y: box.y + Y(p.ay) };
        await page.mouse.move(from.x, from.y);
        await page.mouse.down();
        await page.mouse.move(to.x, to.y, { steps: 4 });
        await page.mouse.up();
        await page.waitForTimeout(80);
      }
      multiDragOk = await page.evaluate(() => document.getElementById('status').className.includes('green'));
    }
  }

  const blankOk = nonBlank && nonBlank[0] > 100 && (!hasDiagram || nonBlank[1] > 100);
  const ok = reqFails.length === 0 && blankOk && meetOk && colorOk && playOk &&
             (dragOk === null || dragOk === true) &&
             (multiDragOk === null || multiDragOk === true);
  if (!ok) failures++;

  await page.screenshot({ path: join(SHOT, f.replace('.html', '.png')) });

  console.log('=== ' + f + ' ===');
  console.log('  请求失败:', reqFails.length ? reqFails : '无');
  console.log('  canvas 非空白:', nonBlank, blankOk ? 'OK' : 'FAIL');
  console.log('  红/蓝实体:', colorOk ? 'OK' : 'FAIL');
  console.log('  滑块→答案 状态:', statusAt, meetOk ? 'OK' : 'FAIL');
  console.log('  播放/暂停:', playOk ? 'OK' : 'FAIL');
  if (dragOk !== null) console.log('  拖拽→答案:', dragOk ? 'OK' : 'FAIL');
  if (multiDragOk !== null) console.log('  多点拖拽→答案:', multiDragOk ? 'OK' : 'FAIL');
  if (errors.length) console.log('  其它错误:', errors.slice(0, 4));
  await page.close();
}

await browser.close();
console.log('\n' + (failures === 0 ? '✅ 全部 ' + files.length + ' 个 HTML 验证通过' : `❌ ${failures}/${files.length} 失败`));
process.exit(failures === 0 ? 0 : 1);
