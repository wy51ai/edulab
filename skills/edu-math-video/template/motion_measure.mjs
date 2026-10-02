/** Runs inside the browser via page.evaluate: return metrics, not six huge pixel arrays. */
export function measureMotion({ times, regions }) {
  const grab = t => {
    window.renderFrame(t);
    const context = document.getElementById('c').getContext('2d');
    return regions.map(([x, y, width, height]) => {
      const data = context.getImageData(x, y, width, height).data;
      const output = [];
      for (let row = 0; row < height; row += 3) for (let column = 0; column < width; column += 3) {
        const index = (row * width + column) * 4;
        output.push((data[index] + data[index + 1] + data[index + 2]) / 3);
      }
      return output;
    });
  };
  const diff = (a, b) => {
    let changed = 0;
    for (let index = 0; index < a.length; index++) if (Math.abs(a[index] - b[index]) > 24) changed++;
    return 100 * changed / a.length;
  };
  const first = grab(times[0]);
  let previous = first;
  const steps = [];
  for (const time of times.slice(1)) {
    const current = grab(time);
    steps.push(diff(previous[0], current[0]));
    previous = current;
  }
  return { steps, net: diff(first[0], previous[0]), board: diff(first[1], previous[1]) };
}
