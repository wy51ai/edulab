import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

function load() {
  const file = new URL('../skills/edu-math-video/lib/biology-model.js', import.meta.url);
  assert.ok(fs.existsSync(file), 'Reusable cell model is present');
  const context = vm.createContext({ Math, Object, Number, Error });
  vm.runInContext(fs.readFileSync(file, 'utf8'), context);
  return context.BiologyModel;
}
const cues = {
  focus: [2, 6], wrap: [10, 16], transport: [17, 22],
  fuse: [23, 28], digest: [29, 35], return: [36, 40],
};

test('a damaged mitochondrion cannot degrade before membrane closure and lysosomal fusion', () => {
  const model = load();
  for (const t of [0, 10, 13, 16, 20, 25, 28]) {
    const state = model.sample(t, cues);
    assert.equal(state.digest, 0);
  }
  assert.equal(model.sample(13, cues).closed, false);
  assert.equal(model.sample(16, cues).closed, true);
  assert.ok(model.sample(32, cues).digest > 0);
  assert.equal(model.sample(40, cues).digest, 1);
});

test('seeking backward and rendering out of order returns exactly the same model state', () => {
  const model = load();
  const original = JSON.stringify(model.sample(14.25, cues));
  for (const t of [40, 32, 0, 28, 10]) model.sample(t, cues);
  assert.equal(JSON.stringify(model.sample(14.25, cues)), original);
});

test('the final camera returns to the original cell and clears only the damaged cargo', () => {
  const model = load();
  const start = model.sample(0, cues), end = model.sample(40, cues);
  assert.equal(end.camera.x, start.camera.x);
  assert.equal(end.camera.y, start.camera.y);
  assert.equal(end.camera.zoom, start.camera.zoom);
  assert.equal(end.cargoOpacity, 0);
  assert.equal(end.healthyOpacity, 1);
});

test('invalid stage order fails instead of showing degradation before fusion', () => {
  const model = load();
  assert.throws(() => model.sample(12, { ...cues, digest: [20, 24] }), /order/);
  assert.throws(() => model.sample(12, { ...cues, wrap: [10, 10] }), /interval/);
  assert.throws(() => model.sample(Number.NaN, cues), /time/);
});

test('a fully degraded mitochondrion leaves no opaque crack or highlight', () => {
  const painted = [], stack = [];
  const ctx = {
    globalAlpha: 0,
    save() { stack.push(this.globalAlpha); },
    restore() { this.globalAlpha = stack.pop(); },
    translate() {}, rotate() {}, scale() {}, beginPath() {}, moveTo() {},
    bezierCurveTo() {}, lineTo() {}, closePath() {}, ellipse() {},
    createLinearGradient() { return { addColorStop() {} }; },
    fill() { painted.push(this.globalAlpha); },
    stroke() { painted.push(this.globalAlpha); },
  };
  load().mitochondrion(ctx, 0, 0, 0, 1, true, 35);
  assert.ok(painted.length > 0);
  assert.ok(painted.every(alpha => alpha === 0), 'all organelle details respect its zero opacity');
  assert.equal(ctx.globalAlpha, 0);
});
