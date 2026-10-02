import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

const optionsURL = new URL('../skills/edu-math-video/template/render_options.mjs', import.meta.url);
const cacheURL = new URL('../skills/edu-math-video/template/render_cache.mjs', import.meta.url);

test('video options use fast encoding without changing frame quality and retain medium', async () => {
  const { videoOptions } = await import(optionsURL);
  assert.deepEqual(videoOptions([]), { workers: 6, preset: 'fast', fresh: false });
  assert.deepEqual(videoOptions(['4', '--preset', 'medium', '--fresh']), { workers: 4, preset: 'medium', fresh: true });
  for (const args of [['0'], ['1.5'], ['NaN'], ['33'], ['--preset'], ['--preset', 'typo'], ['--unknown']]) {
    assert.throws(() => videoOptions(args));
  }
});

function fixture(check) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'edulab-render-cache-'));
  try {
    fs.mkdirSync(path.join(root, 'build'));
    fs.mkdirSync(path.join(root, 'fonts'));
    fs.writeFileSync(path.join(root, 'anim.js'), 'original animation');
    fs.writeFileSync(path.join(root, 'fonts', 'local.ttf'), 'font data');
    fs.writeFileSync(path.join(root, 'custom.data'), 'custom scene data');
    fs.writeFileSync(path.join(root, 'build', 'timeline.json'), '{"duration":1}');
    fs.writeFileSync(path.join(root, 'build', 'mix.wav'), 'original speech');
    fs.writeFileSync(path.join(root, 'output.mp4'), 'completed output');
    return check(root);
  } finally {
    assert.equal(path.dirname(root), path.resolve(os.tmpdir()));
    fs.rmSync(root, {recursive:true,force:true});
  }
}

test('unchanged local lesson can reuse output after storing a successful render', async () => {
  const { inputKey, cacheHit, saveCache } = await import(cacheURL);
  fixture(root => {
    const output = path.join(root,'output.mp4'), cache = path.join(root,'build','render-cache.json');
    const key = inputKey(root, {preset:'fast',fps:30}, output);
    assert.equal(cacheHit(cache,key,output),false);
    saveCache(cache,key,output);
    assert.equal(inputKey(root,{preset:'fast',fps:30},output),key);
    assert.equal(cacheHit(cache,key,output),true);
    // Generated checks and voice-clip caches are already represented by the real inputs.
    fs.mkdirSync(path.join(root,'build','stills'));
    fs.mkdirSync(path.join(root,'build','tts'));
    fs.writeFileSync(path.join(root,'build','stills','review.png'),'review');
    fs.writeFileSync(path.join(root,'build','tts','cached.wav'),'clip');
    assert.equal(inputKey(root,{preset:'fast',fps:30},output),key);
  });
});

test('visual assets, timing, speech and encoding changes invalidate an existing render', async () => {
  const { inputKey, cacheHit, saveCache } = await import(cacheURL);
  for (const name of ['anim.js','fonts/local.ttf','custom.data','build/timeline.json','build/mix.wav']) {
    fixture(root => {
      const output = path.join(root,'output.mp4'), cache = path.join(root,'build','render-cache.json');
      const old = inputKey(root,{preset:'fast'},output);
      saveCache(cache,old,output);
      fs.appendFileSync(path.join(root,name),'changed');
      const changed = inputKey(root,{preset:'fast'},output);
      assert.notEqual(changed,old,name);
      assert.equal(cacheHit(cache,changed,output),false);
    });
  }
  fixture(root => {
    const output=path.join(root,'output.mp4');
    assert.notEqual(inputKey(root,{preset:'fast'},output),inputKey(root,{preset:'medium'},output));
  });
});

test('missing or corrupted output and manifest never count as cached success', async () => {
  const { inputKey, cacheHit, saveCache } = await import(cacheURL);
  fixture(root => {
    const output=path.join(root,'output.mp4'),cache=path.join(root,'build','render-cache.json');
    const key=inputKey(root,{preset:'fast'},output);
    saveCache(cache,key,output);
    fs.writeFileSync(output,'changed contents');
    assert.equal(cacheHit(cache,key,output),false);
    fs.unlinkSync(output);
    assert.equal(cacheHit(cache,key,output),false);
    fs.writeFileSync(cache,'{broken');
    assert.equal(cacheHit(cache,key,output),false);
  });
});

test('retargeting a directory alias invalidates cached content even when both targets were visited', async () => {
  const { inputKey, cacheHit, saveCache } = await import(cacheURL);
  fixture(root => {
    const a=path.join(root,'a'),b=path.join(root,'b'),alias=path.join(root,'z');
    fs.mkdirSync(a);fs.mkdirSync(b);
    fs.writeFileSync(path.join(a,'asset.data'),'red');
    fs.writeFileSync(path.join(b,'asset.data'),'blue');
    fs.symlinkSync(a,alias,'junction');
    // A link back to the root must terminate without losing other aliases.
    fs.symlinkSync(root,path.join(a,'loop'),'junction');
    const output=path.join(root,'output.mp4'),cache=path.join(root,'build','render-cache.json');
    const old=inputKey(root,{preset:'fast'},output);
    saveCache(cache,old,output);
    fs.unlinkSync(alias);fs.symlinkSync(b,alias,'junction');
    assert.equal(fs.readFileSync(path.join(alias,'asset.data'),'utf8'),'blue');
    const changed=inputKey(root,{preset:'fast'},output);
    assert.notEqual(changed,old);
    assert.equal(cacheHit(cache,changed,output),false);
  });
});

test('real export reuses unchanged video, rebuilds edited input and honors --fresh', {timeout:60000}, () => {
  const testsRoot = fileURLToPath(new URL('./',import.meta.url));
  const directory = fs.mkdtempSync(path.join(testsRoot,'.render-speed-'));
  const output = path.join(testsRoot,path.basename(directory)+'.mp4');
  try {
    fs.cpSync(fileURLToPath(new URL('../skills/edu-math-video/template/',import.meta.url)),directory,{recursive:true});
    fs.mkdirSync(path.join(directory,'build'),{recursive:true});
    fs.writeFileSync(path.join(directory,'episode.json'),JSON.stringify({title:'Fixture',output_name:path.basename(directory)}));
    fs.writeFileSync(path.join(directory,'build','timeline.json'),JSON.stringify({duration:.3,fps:30,scenes:[{id:'intro',start:0,end:.3,lines:[]}]}));
    fs.writeFileSync(path.join(directory,'index.html'),`<canvas id="c" width="1920" height="1080"></canvas><script>
      window.ready=Promise.resolve();window.renderFrame=t=>{const ctx=document.getElementById('c').getContext('2d');
      ctx.fillStyle='white';ctx.fillRect(0,0,1920,1080);ctx.fillStyle='black';ctx.fillRect(t*600,150,80,80);};</script>`);
    const wave = Buffer.alloc(44 + 48000*.3*2);
    wave.write('RIFF');wave.writeUInt32LE(wave.length-8,4);wave.write('WAVEfmt ',8);
    wave.writeUInt32LE(16,16);wave.writeUInt16LE(1,20);wave.writeUInt16LE(1,22);
    wave.writeUInt32LE(48000,24);wave.writeUInt32LE(96000,28);wave.writeUInt16LE(2,32);wave.writeUInt16LE(16,34);
    wave.write('data',36);wave.writeUInt32LE(wave.length-44,40);
    for (let i=0;i<48000*.3;i++) wave.writeInt16LE(Math.round(1600*Math.sin(2*Math.PI*440*i/48000)),44+i*2);
    fs.writeFileSync(path.join(directory,'build','mix.wav'),wave);
    const run = (...args) => {
      const result=spawnSync(process.execPath,[path.join(directory,'render.mjs'),'video','1',...args],{encoding:'utf8',timeout:20000});
      assert.equal(result.error,undefined,result.error?.message);
      assert.equal(result.status,0,result.stdout+result.stderr);
      return result.stdout;
    };
    assert.doesNotMatch(run(),/CACHE HIT/);
    const modified=fs.statSync(output).mtimeMs;
    assert.match(run(),/CACHE HIT/);
    assert.equal(fs.statSync(output).mtimeMs,modified);
    fs.appendFileSync(path.join(directory,'index.html'),'<!-- changed local source -->');
    assert.doesNotMatch(run(),/CACHE HIT/);
    assert.doesNotMatch(run('--fresh'),/CACHE HIT/);
    fs.appendFileSync(output,'corrupted output');
    assert.doesNotMatch(run(),/CACHE HIT/);
    const broken=path.join(directory,'unrelated-broken-link');
    fs.symlinkSync(path.join(directory,'missing-target'),broken,'junction');
    assert.doesNotMatch(run('--fresh'),/CACHE HIT/);
    assert.doesNotMatch(run(),/CACHE HIT/);
    fs.unlinkSync(broken);
  } finally {
    assert.equal(path.dirname(directory),path.resolve(testsRoot));
    assert.equal(path.dirname(output),path.resolve(testsRoot));
    fs.rmSync(output,{force:true});
    fs.rmSync(directory,{recursive:true,force:true});
  }
});
