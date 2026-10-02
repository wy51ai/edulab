import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { chromium } from 'playwright';
import { measureMotion } from '../skills/edu-math-video/template/motion_measure.mjs';

const template = fileURLToPath(new URL('../skills/edu-math-video/template/', import.meta.url));

test('motion metrics count changed pixels and preserve the original thresholds', () => {
  let frame = 0;
  globalThis.window = { renderFrame(t) { frame = t; } };
  globalThis.document = { getElementById: () => ({ getContext: () => ({
    getImageData(x) {
      const data = new Uint8ClampedArray(6 * 3 * 4);
      const value = x === 0 ? (frame >= 1 && frame < 3 || frame >= 5 ? 80 : 0) : frame * 30;
      for (let pixel = 0; pixel < 18; pixel++) {
        const v = x === 0 && pixel % 6 >= 3 ? 0 : value;
        data.set([v, v, v, 255], pixel * 4);
      }
      return { data };
    }
  }) }) };
  try {
    const actual = measureMotion({ times: [0, 1, 2, 3, 4, 5], regions: [[0, 0, 6, 3], [6, 0, 6, 3]] });
    assert.deepEqual(actual, { steps: [50, 0, 50, 0, 50], net: 50, board: 100 });
  } finally {
    delete globalThis.window;
    delete globalThis.document;
  }
});

test('real canvas retains the question subtitle through a thinking pause', async () => {
  const dir = await fs.mkdtemp(path.join(os.tmpdir(), 'edulab-render-'));
  let browser;
  try {
    await fs.cp(template, dir, { recursive: true });
    await fs.mkdir(path.join(dir, 'build'), { recursive: true });
    const tl = { preview_only: true, duration: 20, scenes: [
      { id: 'intro', start: 0, end: 20, lines: [
        { zh: '先想一想：为什么？', en: 'Think: why?', start: .2, end: 1.2, hold_end: 4.2 },
        { zh: '两条直角边。', en: 'Two legs.', start: 4.8, end: 6 },
        { zh: '斜边中点。', en: 'Midpoint.', start: 6.5, end: 8 },
        { zh: '求中线。', en: 'Find the median.', start: 8.5, end: 10 }
      ] }
    ] };
    await fs.writeFile(path.join(dir, 'build', 'timeline.js'), 'window.TIMELINE=' + JSON.stringify(tl));
    const args = ['--allow-file-access-from-files', '--disable-web-security'];
    try { browser = await chromium.launch({ channel: 'chrome', args }); }
    catch { browser = await chromium.launch({ args }); }
    const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(pathToFileURL(path.join(dir, 'index.html')).href + '?render=1');
    await page.evaluate(() => window.ready);
    const samples = await page.evaluate(() => {
      window.NO_BOIL = true;
      const sample = t => {
        window.renderFrame(t);
        const pixels = document.getElementById('c').getContext('2d').getImageData(0, 914, 1920, 130).data;
        let hash = 2166136261;
        for (const value of pixels) hash = Math.imul(hash ^ value, 16777619);
        return hash >>> 0;
      };
      return [.8, 3.5, 4.6].map(sample);
    });
    assert.deepEqual(errors, []);
    assert.deepEqual(samples[0], samples[1], 'question disappears during the pause');
    assert.notDeepEqual(samples[1], samples[2], 'question never disappears after the pause');
  } finally {
    if (browser) await browser.close();
    await fs.rm(dir, { recursive: true, force: true });
  }
});
