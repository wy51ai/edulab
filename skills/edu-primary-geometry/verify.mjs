// 无头验证（几何）：零依赖 + canvas 非空白 + 剪拼阶段→绿色 + 等积变形拖拽（面积不变）。
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
  const targetT = data ? data.scene.param.answer : null;

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

  // 2) 滑块 → 阶段 2（结论）：状态变绿（拖点答题类无滑块答案，跳过）
  let meetOk = null, statusAt = '';
  const isDragAnswer = data && (data.scene.points || []).some(p => !p.fixed && p.ax != null && p.ay != null);
  if (data && !isDragAnswer) {
    await page.evaluate(t => {
      const s = document.getElementById('slider');
      s.value = t; s.dispatchEvent(new Event('input'));
    }, targetT);
    await page.waitForTimeout(120);
    statusAt = await page.evaluate(() => document.getElementById('status').className);
    meetOk = statusAt.includes('green');
  }

  // 共享几何变换（世界坐标 → 画布像素），与前端 geomTransform 一致
  function geomOf(box, W) {
    const pad = W.pad != null ? W.pad : 40;
    const u = Math.min((box.width - 2 * pad) / W.xMax, (box.height - 2 * pad) / W.yMax);
    const ox = (box.width - u * W.xMax) / 2, oy = (box.height - u * W.yMax) / 2;
    return { X: x => ox + x * u, Y: y => oy + (W.yMax - y) * u };
  }
  async function dragPoint(page, box, W, fromWorld, toWorld) {
    const G = geomOf(box, W);
    const from = { x: box.x + G.X(fromWorld.x), y: box.y + G.Y(fromWorld.y) };
    const to = { x: box.x + G.X(toWorld.x), y: box.y + G.Y(toWorld.y) };
    await page.mouse.move(from.x, from.y);
    await page.mouse.down();
    await page.mouse.move(to.x, to.y, { steps: 6 });
    await page.mouse.up();
    await page.waitForTimeout(120);
  }

  // 3) 等积变形：拖 D 顶点，面积读数保持不变（好数=面积恒定整数）
  let dragOk = null;
  if (data && data.scene.kind === 'cut-rearrange') {
    const W = data.scene.world;
    const D = (data.scene.points || []).find(p => p.name === 'D');
    if (D) {
      const box = await (await page.$('#scene')).boundingBox();
      const readArea = () => page.evaluate(() => {
        const els = document.querySelectorAll('#readouts .r-value');
        return els[2] ? els[2].textContent.trim() : '';
      });
      await page.evaluate(() => { const s = document.getElementById('slider'); s.value = 0; s.dispatchEvent(new Event('input')); });
      await page.waitForTimeout(60);
      const areaBefore = await readArea();
      await dragPoint(page, box, W, { x: D.x, y: D.y }, { x: D.max, y: D.y });
      const areaAfter = await readArea();
      dragOk = areaBefore === areaAfter && areaBefore.length > 0;
      console.log(`  等积变形: 拖 D 前后面积 "${areaBefore}" == "${areaAfter}"`);
    }
  }

  // 3b) dragToT：拖辅助点/手柄到答案 x，状态变绿（如组合图形分割）
  let dragToTOk = null;
  if (data && data.scene.dragToT) {
    const W = data.scene.world;
    const box = await (await page.$('#scene')).boundingBox();
    const p = (data.scene.points || []).find(pt => pt.name === data.scene.dragToT);
    if (p) {
      await page.evaluate(() => { const s = document.getElementById('slider'); s.value = s.min; s.dispatchEvent(new Event('input')); });
      await page.waitForTimeout(60);
      await dragPoint(page, box, W, { x: data.scene.param.min, y: p.y }, { x: data.scene.param.answer, y: p.y });
      const cls = await page.evaluate(() => document.getElementById('status').className);
      dragToTOk = cls.includes('green');
      console.log(`  拖手柄→答案: ${dragToTOk ? 'OK' : 'FAIL'}`);
    }
  }

  // 3c) 点落答案：可拖点带 ax/ay（平移/轴对称），拖到答案坐标变绿
  let pointAnsOk = null;
  if (data) {
    const movable = (data.scene.points || []).filter(pt => !pt.fixed && pt.ax != null && pt.ay != null);
    if (movable.length) {
      const W = data.scene.world;
      const box = await (await page.$('#scene')).boundingBox();
      let allGreen = true;
      for (const p of movable) {
        await dragPoint(page, box, W, { x: p.x, y: p.y }, { x: p.ax, y: p.ay });
        const cls = await page.evaluate(() => document.getElementById('status').className);
        if (!cls.includes('green')) allGreen = false;
      }
      pointAnsOk = allGreen;
      console.log(`  拖点到答案: ${pointAnsOk ? 'OK' : 'FAIL'}`);
    }
  }

  // 4) 播放 → 前进 → 暂停停住
  let playOk = false;
  if (data) {
    await page.evaluate(() => { const s = document.getElementById('slider'); s.value = 0; s.dispatchEvent(new Event('input')); });
    await page.click('#play');
    await page.waitForTimeout(600);
    const v1 = await page.evaluate(() => parseFloat(document.getElementById('slider').value));
    await page.click('#play');
    await page.waitForTimeout(150);
    const v2 = await page.evaluate(() => parseFloat(document.getElementById('slider').value));
    const v3 = await page.evaluate(() => parseFloat(document.getElementById('slider').value));
    playOk = v1 > 0 && v3 === v2;
  }

  const blankOk = nonBlank && nonBlank > 100;
  const ok = reqFails.length === 0 && blankOk && (meetOk === null || meetOk === true) && playOk &&
             (dragOk === null || dragOk === true) &&
             (dragToTOk === null || dragToTOk === true) &&
             (pointAnsOk === null || pointAnsOk === true);
  if (!ok) failures++;

  await page.screenshot({ path: join(SHOT, f.replace('.html', '.png')) });

  console.log('=== ' + f + ' ===');
  console.log('  请求失败:', reqFails.length ? reqFails : '无');
  console.log('  canvas 非空白:', nonBlank, blankOk ? 'OK' : 'FAIL');
  if (meetOk !== null) console.log('  剪拼→结论 状态:', statusAt, meetOk ? 'OK' : 'FAIL');
  if (dragOk !== null) console.log('  等积变形:', dragOk ? 'OK' : 'FAIL');
  if (dragToTOk !== null) console.log('  拖手柄→答案:', dragToTOk ? 'OK' : 'FAIL');
  if (pointAnsOk !== null) console.log('  拖点到答案:', pointAnsOk ? 'OK' : 'FAIL');
  console.log('  播放/暂停:', playOk ? 'OK' : 'FAIL');
  if (errors.length) console.log('  其它错误:', errors.slice(0, 4));
  await page.close();
}

await browser.close();
console.log('\n' + (failures === 0 ? '✅ 全部 ' + files.length + ' 个 HTML 验证通过' : `❌ ${failures}/${files.length} 失败`));
process.exit(failures === 0 ? 0 : 1);
