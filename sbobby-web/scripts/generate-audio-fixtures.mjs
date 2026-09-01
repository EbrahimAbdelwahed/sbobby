import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { spawn } from 'node:child_process';

const appRoot = resolve(dirname(new URL(import.meta.url).pathname), '..');
const outputDir = resolve(process.argv[2] ?? join(appRoot, 'tests/fixtures/audio/generated'));
const manifestPath = resolve(process.argv[3] ?? join(appRoot, '..', 'specs/audio-to-sbobina-web/assets/audio-fixtures-manifest.json'));
const duration = 90 * 60;

await mkdir(outputDir, { recursive: true });

function run(args) {
  return new Promise((resolvePromise, reject) => {
    const child = spawn('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-nostdin', '-y', ...args], { stdio: 'inherit' });
    child.once('error', reject);
    child.once('exit', (code) => code === 0 ? resolvePromise() : reject(new Error(`ffmpeg exited with ${code}`)));
  });
}

const base = ['-f', 'lavfi', '-i', `sine=frequency=440:sample_rate=16000:duration=${duration}`, '-ac', '1', '-ar', '16000', '-map_metadata', '-1'];
const mp3Path = join(outputDir, 'lecture-90m.mp3');
const m4aPath = join(outputDir, 'lecture-90m.m4a');
await run([...base, '-c:a', 'libmp3lame', '-b:a', '48k', '-write_xing', '0', mp3Path]);
await run([...base, '-c:a', 'aac', '-b:a', '48k', '-movflags', '+faststart', m4aPath]);

async function sha256(path) {
  const hash = createHash('sha256');
  hash.update(await readFile(path));
  return hash.digest('hex');
}

const manifest = {
  version: 1,
  generator: 'scripts/generate-audio-fixtures.mjs',
  durationSeconds: duration,
  source: 'lavfi sine 440Hz, mono, 16kHz',
  encoding: { mp3: 'libmp3lame CBR 48k, no Xing', m4a: 'AAC CBR 48k, faststart' },
  fixtures: [
    { id: 'lecture-90m-mp3', path: 'sbobby-web/tests/fixtures/audio/generated/lecture-90m.mp3', extension: '.mp3', mediaType: 'audio/mpeg', sha256: await sha256(mp3Path) },
    { id: 'lecture-90m-m4a', path: 'sbobby-web/tests/fixtures/audio/generated/lecture-90m.m4a', extension: '.m4a', mediaType: 'audio/mp4', sha256: await sha256(m4aPath) }
  ],
  hostileFixtures: [
    { id: 'truncated-mp3', construction: 'first 128 bytes of lecture-90m.mp3' },
    { id: 'mime-lie', construction: 'valid MP3 bytes named .m4a and audio/mp4' },
    { id: 'malformed-container', construction: 'random bytes with .mp3 extension' },
    { id: 'metadata-bomb', construction: 'oversized ID3/APIC metadata beyond source cap' },
    { id: 'expansion-bomb', construction: 'valid container whose decoded duration exceeds 180 minutes' },
    { id: 'cap-boundaries', construction: 'buffers at 3,499,999 / 3,500,000 / 3,500,001 bytes' },
    { id: 'worker-crash-repeat', construction: 'same invalid input submitted repeatedly' }
  ]
};
await mkdir(dirname(manifestPath), { recursive: true });
await writeFile(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`);
console.log(`Generated deterministic fixtures and manifest at ${manifestPath}`);
