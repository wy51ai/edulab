import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

const template = fileURLToPath(new URL('../skills/edu-math-video/template/', import.meta.url));
const testsRoot = fileURLToPath(new URL('./', import.meta.url));

async function withVideo(config, movingSide, check) {
  const directory = await fs.mkdtemp(path.join(testsRoot, '.motion-regions-'));
  try {
    await fs.cp(template, directory, { recursive: true });
    await fs.mkdir(path.join(directory, 'build'), { recursive: true });
    await fs.writeFile(path.join(directory, 'episode.json'), JSON.stringify({ title: 'Fixture', output_name: 'fixture', ...config }));
    const timeline = { duration: 3, preview_only: true, scenes: ['intro', 'lesson', 'end'].map((id, index) => ({
      id, start: index, end: index + 1,
      lines: [{ zh: 'Observe the moving structure.', en: '', start: index + .1, end: index + .9 }]
    })) };
    await fs.writeFile(path.join(directory, 'build', 'timeline.json'), JSON.stringify(timeline));
    const x = movingSide === 'right' ? 1200 : 160;
    await fs.writeFile(path.join(directory, 'index.html'), `<!doctype html><canvas id="c" width="1920" height="1080"></canvas>
      <script>window.ready = Promise.resolve(); window.renderFrame = t => {
        const context = document.getElementById('c').getContext('2d');
        context.fillStyle = 'white'; context.fillRect(0, 0, 1920, 1080);
        context.fillStyle = 'black'; context.fillRect(${x} + t * 80, 200, 200, 100);
      };</script>`);
    const result = spawnSync(process.execPath, [path.join(directory, 'render.mjs'), 'motion'], {
      encoding: 'utf8', timeout: 30000
    });
    assert.equal(result.error, undefined, result.error?.message);
    await check(result, directory);
  } finally {
    // Only remove the uniquely created fixture below this test directory.
    assert.equal(path.dirname(directory), path.resolve(testsRoot));
    await fs.rm(directory, { recursive: true, force: true });
  }
}

// Catches a renderer that still measures the old left-hand region after configuration.
test('motion CLI measures a configured right-hand figure on the real canvas', async () => {
  await withVideo({ motion_regions: { figure: [925, 110, 995, 770], board: [0, 110, 925, 770] } }, 'right', async (result, directory) => {
    assert.equal(result.status, 0, result.stdout + result.stderr);
    const report = await fs.readFile(path.join(directory, 'build', 'motion_report.txt'), 'utf8');
    assert.match(report, /\[lesson 0\] MOVE/);
    assert.match(report, /board 0\.00%/);
  });
});

// Catches a change that accidentally stops legacy episodes from inspecting the left figure.
test('motion CLI keeps the legacy figure when motion_regions is omitted', async () => {
  await withVideo({}, 'left', async result => {
    assert.equal(result.status, 0, result.stdout + result.stderr);
    assert.match(result.stdout, /\[lesson 0\] MOVE/);
  });
});

// Catches an unspecified board being lost when an episode sets only its figure.
test('motion CLI accepts a figure override with the default board', async () => {
  await withVideo({ motion_regions: { figure: [925, 110, 995, 770] } }, 'right', async result => {
    assert.equal(result.status, 0, result.stdout + result.stderr);
    assert.match(result.stdout, /\[lesson 0\] MOVE/);
    assert.doesNotMatch(result.stdout, /board 0\.00%/);
  });
});

// Each malformed input must fail before browser startup or any generated timeline write.
const invalidRegions = [
  ['null configuration', null],
  ['array configuration', []],
  ['non-object configuration', 1],
  ['wrong rectangle length', { figure: [0, 0, 100] }],
  ['non-array rectangle', { figure: { x: 0, y: 0, width: 100, height: 100 } }],
  ['negative origin', { figure: [-1, 0, 100, 100] }],
  ['fractional origin', { figure: [0.5, 0, 100, 100] }],
  ['zero width', { figure: [0, 0, 0, 100] }],
  ['negative height', { figure: [0, 0, 100, -1] }],
  ['non-finite coordinate', { figure: [0, 0, Infinity, 100] }],
  ['numeric string', { figure: ['0', 0, 100, 100] }],
  ['right overflow', { figure: [1900, 0, 21, 100] }],
  ['bottom overflow', { board: [0, 1000, 100, 81] }],
  ['null board', { board: null }]
];
for (const [description, motion_regions] of invalidRegions) {
  test(`motion CLI rejects ${description} before rendering`, async () => {
    await withVideo({ motion_regions }, 'left', async (result, directory) => {
      assert.notEqual(result.status, 0, 'Invalid motion region was silently accepted.');
      assert.match(result.stderr, /motion_regions/);
      await assert.rejects(fs.access(path.join(directory, 'build', 'timeline.js')), { code: 'ENOENT' });
      await assert.rejects(fs.access(path.join(directory, 'build', 'motion_report.txt')), { code: 'ENOENT' });
    });
  });
}
