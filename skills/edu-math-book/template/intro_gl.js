/* ---------- the classroom in WebGL ----------
   Three.js coordinates are room centimetres with Y up: X right, Y up, Z toward the reader (room y).
   The reader sits in the front row, so only the platform, blackboard and the two neighbouring desks are ahead. */
import * as THREE from 'three';
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';

const canvas = document.getElementById('gl');
const renderer = new THREE.WebGLRenderer({canvas, antialias: true});
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
const scene = new THREE.Scene();
scene.background = new THREE.Color('#efe2cc');
scene.environment = new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(), .04).texture;
scene.environmentIntensity = .35;
const ANISO = renderer.capabilities.getMaxAnisotropy();

const R = {xl: -450, xr: 450, zf: -340, zb: 420, h: 320, t: 20};     // room box; zf is the blackboard wall
const WINS = [[-320, -190], [-140, -10], [40, 170], [220, 350]], WY = [95, 285];

/* ---- helpers ---- */
let seed = 7;
const rand = () => ((seed = (seed * 16807) % 2147483647) - 1) / 2147483646;
const std = o => new THREE.MeshStandardMaterial({roughness: .8, ...o});
function box(x0, x1, y0, y1, z0, z1, mat, cast = true) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(x1 - x0, y1 - y0, z1 - z0), mat);
  m.position.set((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2);
  m.castShadow = cast; m.receiveShadow = true;
  scene.add(m); return m;
}
function quad(w, h, mat, pos, rotY = 0) {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), mat);
  m.position.set(...pos); m.rotation.y = rotY; m.receiveShadow = true;
  scene.add(m); return m;
}
function canvasTex(w, h, draw, repeat) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = ANISO;
  if (repeat) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(...repeat); }
  t.redraw = () => { draw(c.getContext('2d'), w, h); t.needsUpdate = true; };
  t.redraw();
  return t;
}
const loader = new THREE.TextureLoader();
function imgTex(url, repeat) {
  const t = loader.load(url, () => dirty = true);
  t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = ANISO;
  t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(...repeat);
  return t;
}

/* ---- floor: clean, lightly polished 60 cm tiles ---- */
const floorTex = canvasTex(1024, 1024, (g, w) => {
  const n = 4, s = w / n;
  for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) {
    g.fillStyle = `hsl(36 ${14 + rand() * 4}% ${88 + rand() * 3}%)`; g.fillRect(i * s, j * s, s, s);
  }
  for (let k = 0; k < 9000; k++) {               // faint terrazzo flecks
    g.fillStyle = rand() < .5 ? 'rgba(150,135,115,.10)' : 'rgba(255,255,255,.25)';
    g.beginPath(); g.arc(rand() * w, rand() * w, .5 + rand() * 1.4, 0, 6.3); g.fill();
  }
  g.fillStyle = 'rgba(165,152,132,.55)';
  for (let i = 0; i <= n; i++) { g.fillRect(i * s - 1.5, 0, 3, w); g.fillRect(0, i * s - 1.5, w, 3); }
}, [(R.xr - R.xl) / 240, (R.zb - R.zf) / 240]);
const floor = new THREE.Mesh(new THREE.PlaneGeometry(R.xr - R.xl, R.zb - R.zf),
  new THREE.MeshPhysicalMaterial({map: floorTex, roughness: .34, clearcoat: .35, clearcoatRoughness: .3}));
floor.rotation.x = -Math.PI / 2; floor.position.set(0, 0, (R.zf + R.zb) / 2); floor.receiveShadow = true;
scene.add(floor);

/* ---- walls: cream plaster above a sage-green dado ---- */
const plaster = std({color: '#f1e9d8', roughness: .95}), dado = std({color: '#93b7a3', roughness: .6}),
  trim = std({color: '#6f9483', roughness: .5}), skirting = std({color: '#56635b', roughness: .6}),
  alu = std({color: '#eeebe4', roughness: .45, metalness: .25});
const dadoRun = (x0, x1, z0, z1, top = 100) => {          // a 1 cm proud panel along a wall face
  box(x0, x1, 0, top, z0, z1, dado, false);
  box(x0, x1, top, top + 4, z0, z1, trim, false);
};
// front (blackboard) wall, right wall, back wall, ceiling
box(R.xl - R.t, R.xr + R.t, 0, R.h, R.zf - R.t, R.zf, plaster);
dadoRun(R.xl, R.xr, R.zf, R.zf + 1);
box(R.xl, R.xr, 0, 12, R.zf, R.zf + 1.8, skirting, false);
box(R.xr, R.xr + R.t, 0, R.h, R.zf, R.zb, plaster);
dadoRun(R.xr - 1, R.xr, R.zf, R.zb);
box(R.xr - 1.8, R.xr, 0, 12, R.zf, R.zb, skirting, false);
box(R.xl - R.t, R.xr + R.t, 0, R.h, R.zb, R.zb + R.t, plaster);
box(R.xl - R.t, R.xr + R.t, R.h, R.h + 12, R.zf - R.t, R.zb + R.t, std({color: '#f5f1e8', roughness: 1}));
// left wall: real openings, so the sun comes through the windows and the frames cast shadows
const xw0 = R.xl - R.t, xw1 = R.xl;
box(xw0, xw1, 0, WY[0], R.zf, R.zb, plaster);
box(xw0, xw1, WY[1], R.h, R.zf, R.zb, plaster);
[[R.zf, WINS[0][0]], ...WINS.slice(1).map((w, i) => [WINS[i][1], w[0]]), [WINS[WINS.length - 1][1], R.zb]]
  .forEach(([a, b]) => box(xw0, xw1, WY[0], WY[1], a, b, plaster));
box(xw1, xw1 + 1, 0, 88, R.zf, R.zb, dado, false);
box(xw1, xw1 + 1.8, 0, 12, R.zf, R.zb, skirting, false);
WINS.forEach(([z0, z1]) => {
  box(xw0 - 2, xw1 + 9, WY[0] - 6, WY[0], z0 - 6, z1 + 6, std({color: '#f4f2ec', roughness: .4}));    // sill
  const fx0 = xw0 + 6, fx1 = xw0 + 12, zm = (z0 + z1) / 2;
  box(fx0, fx1, WY[0], WY[0] + 5, z0, z1, alu); box(fx0, fx1, WY[1] - 5, WY[1], z0, z1, alu);
  box(fx0, fx1, WY[0], WY[1], z0, z0 + 5, alu); box(fx0, fx1, WY[0], WY[1], z1 - 5, z1, alu);
  box(fx0, fx1, WY[0], WY[1], zm - 2, zm + 2, alu); box(fx0, fx1, 218, 222, z0, z1, alu);
});
// sheer curtains gathered between the windows, glowing a little in the backlight
const curtainTex = canvasTex(256, 512, (g, w, h) => {
  for (let x = 0; x < w; x++) {
    const v = .5 + .5 * Math.sin(x / w * Math.PI * 9 + Math.sin(x * .07) * .8);
    g.fillStyle = `rgba(255,252,246,${(.55 + .4 * v).toFixed(3)})`; g.fillRect(x, 0, 1, h);
  }
});
const curtain = std({map: curtainTex, transparent: true, side: THREE.DoubleSide, emissive: '#fff1dc', emissiveIntensity: .25, roughness: 1});
WINS.forEach(([z0, z1]) => [z0 - 14, z1 + 14].forEach(z => quad(34, 225, curtain, [xw1 + 6, 190, z], Math.PI / 2)));
box(xw1 + 4, xw1 + 7, 302, 305, R.zf, R.zb, alu, false);
// what's outside: sky, a few pale buildings and blossoming trees
const outside = canvasTex(2048, 1024, (g, w, h) => {
  const sky = g.createLinearGradient(0, 0, 0, h);
  sky.addColorStop(0, '#7fb6e6'); sky.addColorStop(.45, '#cfe5f2'); sky.addColorStop(.7, '#fff0d6'); sky.addColorStop(1, '#ffe2b8');
  g.fillStyle = sky; g.fillRect(0, 0, w, h);
  g.filter = 'blur(18px)';
  for (let k = 0; k < 14; k++) { g.fillStyle = 'rgba(255,255,255,.75)'; g.beginPath(); g.ellipse(rand() * w, 80 + rand() * 260, 120 + rand() * 160, 30 + rand() * 30, 0, 0, 6.3); g.fill(); }
  g.filter = 'blur(2px)';
  for (let k = 0; k < 9; k++) { g.fillStyle = `hsl(30 20% ${84 + rand() * 6}%)`; const bw = 120 + rand() * 160, bh = 120 + rand() * 180, bx = rand() * w; g.fillRect(bx, 640 - bh, bw, bh + 400); }
  g.filter = 'none';
  for (let k = 0; k < 7; k++) {
    const cx = 150 + k * 290 + rand() * 80, cy = 520 + rand() * 80;
    g.fillStyle = '#6b4a3a'; g.fillRect(cx - 8, cy, 16, 400);
    for (let p = 0; p < 420; p++) {
      const a = rand() * 6.3, r = Math.sqrt(rand()) * 210;
      g.fillStyle = ['#f8cddb', '#f3b2c8', '#fde4ec', '#ffffff', '#eda0ba'][p % 5];
      g.globalAlpha = .55 + rand() * .4;
      g.beginPath(); g.arc(cx + Math.cos(a) * r * 1.3, cy - 40 + Math.sin(a) * r * .8, 8 + rand() * 16, 0, 6.3); g.fill();
    }
    g.globalAlpha = 1;
  }
});
quad(2600, 1100, new THREE.MeshBasicMaterial({map: outside}), [-950, 220, 0], Math.PI / 2);

/* ---- front of the room: blackboard, slogan, clock, timetable, speaker, platform ---- */
const wood = std({color: '#8a6a43', roughness: .6});
const oak = std({map: imgTex(TEX.oak, [1, 1]), roughness: .5});
const bbTex = canvasTex(2048, 612, (g, w, h) => {
  const bg = g.createLinearGradient(0, 0, w, h); bg.addColorStop(0, '#2f5444'); bg.addColorStop(.6, '#203d31'); bg.addColorStop(1, '#1b3429');
  g.fillStyle = bg; g.fillRect(0, 0, w, h);
  for (let k = 0; k < 60; k++) { g.fillStyle = `rgba(255,255,255,${.012 + rand() * .02})`; g.fillRect(rand() * w, 0, 30 + rand() * 90, h); }   // eraser smears
  const s = w / 418, chalk = 'rgba(244,244,234,.88)';
  g.fillStyle = chalk; g.strokeStyle = chalk; g.lineCap = 'round'; g.lineWidth = 5;
  const txt = (t, x, y, size, c = chalk) => { g.fillStyle = c; g.font = `${size * s}px "Long Cang", "Ma Shan Zheng", cursive`; g.fillText(t, x * s, y * s); };
  // problem text from the lesson (BOARD.lines: [text, size, colour?]) and a chalk copy of the figure on the right
  let y = 28;
  BOARD.lines.forEach(([t, size, c]) => { txt(t, 18, y, size, c || chalk); y += size * 1.75; });
  if (window.boardImg && boardImg.complete && boardImg.naturalWidth) g.drawImage(boardImg, 238 * s, 4 * s, 130 * s, 114 * s);
  const d = new Date();
  txt(`${d.getMonth() + 1}月${d.getDate()}日`, 372, 24, 10, 'rgba(244,244,234,.6)'); txt(BOARD.duty || '值日：王', 372, 38, 10, 'rgba(244,244,234,.6)');
});
quad(418, 125, std({map: bbTex, roughness: .9}), [0, 152.5, R.zf + 1.4]);
box(-215, 215, 215, 221, R.zf, R.zf + 4, wood); box(-215, 215, 84, 90, R.zf, R.zf + 4, wood);
box(-215, -209, 84, 221, R.zf, R.zf + 4, wood); box(209, 215, 84, 221, R.zf, R.zf + 4, wood);
box(-212, 212, 82, 86, R.zf, R.zf + 9, wood);                                    // chalk tray
box(120, 128, 86, 88, R.zf + 3, R.zf + 7, std({color: '#fffdf4'})); box(140, 146, 86, 88, R.zf + 2, R.zf + 6, std({color: '#f2c9d6'}));
const plaque = canvasTex(1024, 168, (g, w, h) => {
  g.fillStyle = '#fbf6ea'; g.fillRect(0, 0, w, h); g.strokeStyle = '#a07a4a'; g.lineWidth = 12; g.strokeRect(6, 6, w - 12, h - 12);
  g.fillStyle = '#c23a2b'; g.font = '900 96px "Noto Serif SC", "Songti SC", serif'; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.fillText('好好学习　天天向上', w / 2, h / 2 + 4);
});
quad(190, 31, std({map: plaque, roughness: .7}), [0, 262, R.zf + 1.5]);
const clockTex = canvasTex(256, 256, (g, w) => {
  const d = new Date(), c = w / 2;
  g.clearRect(0, 0, w, w);
  g.fillStyle = '#2b2a28'; g.beginPath(); g.arc(c, c, c, 0, 6.3); g.fill();
  g.fillStyle = '#fbfaf4'; g.beginPath(); g.arc(c, c, c - 14, 0, 6.3); g.fill();
  g.fillStyle = '#2b2a28';
  for (let k = 0; k < 12; k++) { g.save(); g.translate(c, c); g.rotate(k * Math.PI / 6); g.fillRect(-3, -c + 22, 6, k % 3 ? 10 : 20); g.restore(); }
  const hand = (a, len, wd) => { g.save(); g.translate(c, c); g.rotate(a); g.fillRect(-wd / 2, -len, wd, len + 10); g.restore(); };
  hand((d.getHours() % 12 + d.getMinutes() / 60) * Math.PI / 6, 60, 9); hand(d.getMinutes() * Math.PI / 30, 88, 6);
});
setInterval(() => { clockTex.redraw(); dirty = true; }, 30000);
quad(40, 40, new THREE.MeshStandardMaterial({map: clockTex, transparent: true, roughness: .4}), [310, 262, R.zf + 2]);
const timetable = canvasTex(300, 400, (g, w, h) => {
  g.fillStyle = '#f7f2e4'; g.fillRect(0, 0, w, h); g.strokeStyle = '#b9ad92'; g.lineWidth = 8; g.strokeRect(4, 4, w - 8, h - 8);
  g.fillStyle = '#c23a2b'; g.font = '900 40px "Noto Serif SC", serif'; g.textAlign = 'center'; g.fillText('课 程 表', w / 2, 62);
  g.fillStyle = '#5a5246'; g.font = '600 28px "Noto Serif SC", serif';
  ['一  数学  语文', '二  英语  物理', '三  数学  化学', '四  语文  生物', '五  物理  数学'].forEach((t, i) => g.fillText(t, w / 2, 130 + i * 52));
});
quad(54, 72, std({map: timetable}), [-330, 205, R.zf + 1.5]);
box(-400, -368, 268, 302, R.zf, R.zf + 16, std({color: '#5b4632', roughness: .5}));
box(-300, 300, 0, 20, R.zf, R.zf + 80, std({color: '#cdbfa3', roughness: .75}));
// lectern, off to the side: an inset body under an overhanging oak top
box(205, 285, 20, 100, R.zf + 14, R.zf + 50, std({color: '#9a6e46', roughness: .55}));
box(199, 291, 100, 104, R.zf + 10, R.zf + 54, oak);
// ceiling lights
const tube = std({color: '#ffffff', emissive: '#fff8e8', emissiveIntensity: 2.2});
[-250, 0, 250].forEach(x => [-180, 80, 320].forEach(z => {
  box(x - 62, x + 62, R.h - 6, R.h - 2, z - 9, z + 9, std({color: '#e8e4da', metalness: .3, roughness: .4}), false);
  box(x - 58, x + 58, R.h - 8, R.h - 6, z - 5, z + 5, tube, false);
}));

/* ---- desks: the reader's (walnut, under the CSS book and props) and the two neighbours in the front row ---- */
const walnut = new THREE.MeshPhysicalMaterial({map: imgTex(TEX.walnut, [1, .55]), color: '#c7a184', roughness: .42, clearcoat: .3, clearcoatRoughness: .35});
const walnutDark = std({color: '#5b3a24', roughness: .55});
const [dx0, dx1, dz0, dz1] = [DESK.x0, DESK.x1, DESK.y0, DESK.y1].map(v => v / CM);
box(dx0, dx1, 72, 75, dz0, dz1, walnut);
box(dx0 + 5, dx1 - 5, 61, 72, dz0 + 5, dz1 - 5, walnutDark);
[[dx0 + 3, dz0 + 3], [dx1 - 8, dz0 + 3], [dx0 + 3, dz1 - 8], [dx1 - 8, dz1 - 8]].forEach(([x, z]) => box(x, x + 5, 0, 72, z, z + 5, walnutDark));
const steel = std({color: '#7a8794', metalness: .55, roughness: .4});
function studentDesk(cx, cz, books) {
  box(cx - 60, cx + 60, 72, 75, cz - 25, cz + 25, oak);
  box(cx - 57, cx + 57, 58, 72, cz - 23, cz + 22, steel);
  [[-58, -24], [55, -24], [-58, 21], [55, 21]].forEach(([x, z]) => box(cx + x, cx + x + 3, 0, 72, cz + z, cz + z + 3, steel));
  // chair tucked in on the student's side
  const c = cz + 48;
  box(cx - 20, cx + 20, 43, 46, c - 19, c + 19, oak);
  box(cx - 20, cx + 20, 64, 90, c + 17, c + 19.5, oak);
  [[-19, -18], [16, -18], [-19, 15], [16, 15]].forEach(([x, z]) => box(cx + x, cx + x + 3, 0, 43, c + z, c + z + 3, steel));
  [[-19, 15], [16, 15]].forEach(([x, z]) => box(cx + x, cx + x + 3, 43, 90, c + z + 1, c + z + 3.5, steel));
  if (books) [['#c0392b', 0], ['#2c5aa0', 3], ['#e1a83a', 6]].forEach(([col, y], k) =>
    box(cx - 30 + k * 2, cx - 4 + k * 2, 75 + y, 78 + y, cz - 12 - k, cz + 7 - k, std({color: col, roughness: .6})));
}
studentDesk(-215, -6, true);
studentDesk(215, -6, false);
// soft contact shadow under her feet (she's a CSS video plane above this layer)
const blob = canvasTex(128, 64, (g, w, h) => {
  const r = g.createRadialGradient(w / 2, h / 2, 0, w / 2, h / 2, w / 2); r.addColorStop(0, 'rgba(40,25,10,.5)'); r.addColorStop(1, 'rgba(40,25,10,0)');
  g.setTransform(1, 0, 0, .5, 0, h / 4); g.fillStyle = r; g.fillRect(0, 0, w, w);
});
const blobM = new THREE.Mesh(new THREE.PlaneGeometry(70, 30), new THREE.MeshBasicMaterial({map: blob, transparent: true, depthWrite: false}));
blobM.rotation.x = -Math.PI / 2; blobM.position.set(GIRL.x, .3, GIRL.y); scene.add(blobM);

/* ---- light: low afternoon sun through the left windows, warm sky fill, a cool bounce ---- */
const sun = new THREE.DirectionalLight('#ffd29a', 5.5);
sun.position.set(-.75, .4, .5).normalize().multiplyScalar(1500);   // from behind-left, so window patches land on the front wall and floor
sun.castShadow = true;
Object.assign(sun.shadow.camera, {left: -700, right: 700, top: 700, bottom: -700, near: 300, far: 3200});
sun.shadow.mapSize.set(2048, 2048); sun.shadow.bias = -.0004; sun.shadow.normalBias = .6; sun.shadow.radius = 4;
scene.add(sun, sun.target);
scene.add(new THREE.HemisphereLight('#fff3e2', '#cbb79c', .8));
const fill = new THREE.DirectionalLight('#dfe7ff', .35); fill.position.set(400, 300, 500); scene.add(fill);

/* ---- camera: reproduce the CSS camera exactly ----
   CSS world px = W · room cm; CSS camera space = cw · world; three view space flips y and moves the viewer to the origin. */
const W = new THREE.Matrix4().set(CM, 0, 0, 0, 0, 0, CM, 0, 0, CM, 0, -DESK_Z * CM - 3, 0, 0, 0, 1);
const cam = new THREE.PerspectiveCamera();
cam.matrixAutoUpdate = false; cam.matrixWorldAutoUpdate = false;
const Fy = new THREE.Matrix4().makeScale(1, -1, 1), T = new THREE.Matrix4(), Cw = new THREE.Matrix4();
let dirty = true, lastKey = '';
window.glFrame = ({cw, P, poY, vw, vh}) => {
  const size = renderer.getSize(new THREE.Vector2());
  if (size.x !== vw || size.y !== vh) { renderer.setSize(vw, vh, false); dirty = true; }
  const key = cw.toString() + P + poY;
  if (!dirty && key === lastKey) return;
  dirty = false; lastKey = key;
  const ey = (poY - .57) * vh;                            // the CSS viewer sits at (0, ey, P) in camera space
  cam.matrixWorldInverse.copy(Fy).multiply(T.makeTranslation(0, -ey, -P)).multiply(Cw.fromArray(cw.toFloat64Array())).multiply(W);
  cam.matrixWorld.copy(cam.matrixWorldInverse).invert();
  const n = 40;
  cam.projectionMatrix.makePerspective(-n * vw / 2 / P, n * vw / 2 / P, n * poY * vh / P, -n * (1 - poY) * vh / P, n, 3e5);
  cam.projectionMatrixInverse.copy(cam.projectionMatrix).invert();
  renderer.render(scene, cam);
};
document.body.classList.add('gl');
// canvas textures drawn with web fonts get redrawn once the fonts arrive
document.fonts.ready.then(() => { [bbTex, plaque, timetable].forEach(t => t.redraw()); dirty = true; });
window.boardReady = () => { bbTex.redraw(); dirty = true; };
