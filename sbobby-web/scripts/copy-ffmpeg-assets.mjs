import { cp, mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = dirname(fileURLToPath(import.meta.url));
const appRoot = dirname(root);
const coreRoot = join(appRoot, 'node_modules', '@ffmpeg', 'core', 'dist', 'esm');
const publicRoot = join(appRoot, 'public', 'ffmpeg');

await mkdir(publicRoot, { recursive: true });
const copyJavaScript = async (source, destination) => {
  const contents = await readFile(source, 'utf8');
  await writeFile(destination, contents.replace(/[ \t]+$/gm, ''));
};

await copyJavaScript(join(coreRoot, 'ffmpeg-core.js'), join(publicRoot, 'ffmpeg-core.esm.js'));
await cp(join(coreRoot, 'ffmpeg-core.wasm'), join(publicRoot, 'ffmpeg-core.esm.wasm'));
await cp(join(appRoot, 'node_modules', '@ffmpeg', 'ffmpeg', 'dist', 'esm', 'worker.js'), join(publicRoot, 'ffmpeg-worker.js'));
const ffmpegConst = await readFile(join(appRoot, 'node_modules', '@ffmpeg', 'ffmpeg', 'dist', 'esm', 'const.js'), 'utf8');
await writeFile(join(publicRoot, 'const.js'), ffmpegConst
  .replace('export const CORE_VERSION = "0.12.9";', 'export const CORE_VERSION = "0.12.10";')
  .replace(/export const CORE_URL = `[^`]+`;/, "export const CORE_URL = '/ffmpeg/ffmpeg-core.esm.js';"));
await cp(join(appRoot, 'node_modules', '@ffmpeg', 'ffmpeg', 'dist', 'esm', 'errors.js'), join(publicRoot, 'errors.js'));

console.log('Copied pinned FFmpeg core assets to public/ffmpeg.');
