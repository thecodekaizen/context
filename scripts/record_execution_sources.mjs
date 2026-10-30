import { chromium } from '../web/node_modules/playwright/index.mjs';
import { mkdir, access, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { execFileSync } from 'node:child_process';

const root = resolve(fileURLToPath(new URL('..', import.meta.url)));
const base = resolve(root, 'eval/execution-v1');
const output = resolve(base, 'sources');
await mkdir(output, { recursive: true });
const browser = await chromium.launch({ headless: true });
try {
  for (const name of ['sort', 'cache', 'serialize']) {
    const target = resolve(output, `${name}.mp4`);
    try { await access(target); continue; } catch {}
    const context = await browser.newContext({ viewport: { width: 960, height: 640 },
      recordVideo: { dir: resolve(root, 'data/execution-recordings'), size: { width: 960, height: 640 } } });
    const page = await context.newPage();
    await page.goto(`${pathToFileURL(resolve(base, 'benchmark.html'))}?benchmark=${name}`);
    await page.waitForTimeout(19000);
    const measurements = await page.evaluate(() => window.measurements);
    const video = page.video();
    await context.close();
    const recording = await video.path();
    execFileSync('ffmpeg', ['-v', 'error', '-n', '-i', recording, '-f', 'lavfi', '-i',
      "aevalsrc=0.08*sin(2*PI*(170*t+23*t*t+2*sin(7*t))):s=16000:d=18",
      '-t', '18', '-vf', 'fps=24,format=yuv420p', '-c:v', 'libx264', '-crf', '20',
      '-c:a', 'aac', '-movflags', '+faststart', target]);
    await writeFile(resolve(output, `${name}-measurements.json`), JSON.stringify({
      benchmark: name, measurements_ms: measurements, provenance: 'Actual Chromium execution recorded by Playwright',
      soundtrack: 'Synthetic frequency sweep for audio-alignment diagnostics; not speech', license: 'CC0-1.0'
    }, null, 2));
    console.log(`Recorded ${name}`);
  }
} finally { await browser.close(); }
