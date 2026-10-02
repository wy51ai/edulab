/** Resolve validated canvas regions without changing the episode configuration. */
export function resolveMotionRegions(episode) {
  const configured = episode.motion_regions;
  if (configured !== undefined && (configured === null || typeof configured !== 'object' || Array.isArray(configured))) {
    throw new Error('episode.motion_regions must be an object with optional figure and board rectangles.');
  }
  const regions = { figure: [0, 110, 925, 770], board: [925, 110, 995, 770] };
  for (const name of ['figure', 'board']) {
    const rectangle = configured?.[name];
    if (rectangle === undefined) continue;
    if (!Array.isArray(rectangle) || rectangle.length !== 4
        || !rectangle.every(value => Number.isFinite(value) && Number.isInteger(value))) {
      throw new Error(`episode.motion_regions.${name} must be [x, y, width, height] with finite integers.`);
    }
    const [x, y, width, height] = rectangle;
    if (x < 0 || y < 0 || width <= 0 || height <= 0 || x + width > 1920 || y + height > 1080) {
      throw new Error(`episode.motion_regions.${name} must have positive width and height and fit inside the 1920x1080 canvas.`);
    }
    regions[name] = rectangle.slice();
  }
  return regions;
}
