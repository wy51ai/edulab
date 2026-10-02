export function videoOptions(args) {
  args = [...args];
  const options = { workers: 6, preset: 'fast', fresh: false };
  if (args.length && !args[0].startsWith('--')) options.workers = Number(args.shift());
  if (!Number.isInteger(options.workers) || options.workers < 1 || options.workers > 32) {
    throw new Error('Video workers must be an integer from 1 to 32');
  }
  const presets = new Set(['ultrafast','superfast','veryfast','faster','fast','medium','slow','slower','veryslow']);
  while (args.length) {
    const flag = args.shift();
    if (flag === '--fresh') options.fresh = true;
    else if (flag === '--preset') {
      const preset = args.shift();
      if (!presets.has(preset)) throw new Error('Unknown or missing encoding preset');
      options.preset = preset;
    } else throw new Error('Unknown video option: ' + flag);
  }
  return options;
}
