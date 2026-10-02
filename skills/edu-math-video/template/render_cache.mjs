import fs from 'node:fs';
import path from 'node:path';
import { createHash } from 'node:crypto';

function fileHash(file) {
  const hash = createHash('sha256'), buffer = Buffer.allocUnsafe(1024 * 1024);
  const fd = fs.openSync(file,'r');
  try {
    let length;
    while ((length = fs.readSync(fd,buffer,0,buffer.length,null))) hash.update(buffer.subarray(0,length));
    return hash.digest('hex');
  } finally { fs.closeSync(fd); }
}

export function inputKey(root, settings, output) {
  const hash = createHash('sha256').update(JSON.stringify(settings));
  const excluded = new Set(['node_modules','.git','__pycache__','.venv']);
  const visited = new Set();
  function visit(folder, relative = '') {
    const real = fs.realpathSync(folder);
    // Aliases must keep their own identity even if the target was already visited.
    hash.update('directory\0').update(relative).update('\0').update(real).update('\0');
    if (visited.has(real)) return;
    visited.add(real);
    for (const entry of fs.readdirSync(folder,{withFileTypes:true}).sort((a,b)=>a.name<b.name?-1:1)) {
      const name = relative ? relative+'/'+entry.name : entry.name;
      if (excluded.has(entry.name) || ['build/stills','build/tts'].includes(name)) continue;
      const file = path.join(folder,entry.name), stat = fs.statSync(file);
      if (stat.isDirectory()) visit(file,name);
      else if (stat.isFile() && path.resolve(file) !== path.resolve(output)) {
        if (/^build\/(?:render-cache\.json|timeline\.js|chunk\d+\.mp4|chunks\.txt|(?:pron|teaching|motion|asr)_report\.txt|asr\.json)$/.test(name)) continue;
        hash.update(name).update('\0').update(fileHash(file)).update('\0');
      }
    }
  }
  visit(root);
  return hash.digest('hex');
}

export function cacheHit(manifest, key, output) {
  try {
    const saved = JSON.parse(fs.readFileSync(manifest,'utf8'));
    return saved.version === 1 && saved.key === key && saved.output === path.resolve(output)
      && saved.size > 0 && fs.statSync(output).size === saved.size && fileHash(output) === saved.sha256;
  } catch { return false; }
}

export function saveCache(manifest, key, output) {
  const saved = {version:1,key,output:path.resolve(output),size:fs.statSync(output).size,sha256:fileHash(output)};
  const temporary = manifest+'.tmp';
  fs.writeFileSync(temporary,JSON.stringify(saved));
  fs.renameSync(temporary,manifest);
}
