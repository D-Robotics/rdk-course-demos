// Install playwright, provide CHROME_PATH if needed, and put ffmpeg on PATH.
// node tools/render-spi-video.cjs en|zh|summary-zh output-directory [--review]
// Each frame is rendered at an explicit time, never captured from a desktop.
const fs = require('fs');
const path = require('path');
const { pathToFileURL } = require('url');
const { once } = require('events');
const { spawn } = require('child_process');
const { chromium } = require('playwright');

async function main() {
  const language = process.argv[2];
  if (!['en', 'zh', 'summary-zh'].includes(language) || !process.argv[3]) throw new Error('Usage: node render-spi-video.cjs en|zh|summary-zh output-directory [--review]');
  const out = path.resolve(process.argv[3]);
  fs.mkdirSync(out, { recursive: true });
  const duration = language === 'summary-zh' ? 41 : language === 'en' ? 55 : 49;
  const stem = language === 'summary-zh' ? 'spi_summary_41s.zh' : `spi_explainer_${duration}s.${language}`;
  const html = path.resolve(__dirname, '..', `${stem}.html`);
  const executablePath = process.env.CHROME_PATH || (process.platform === 'win32' ? 'C:/Program Files/Google/Chrome/Application/chrome.exe' : undefined);
  const browser = await chromium.launch({ executablePath, headless: true, args: ['--hide-scrollbars', '--force-device-scale-factor=1'] });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  page.on('pageerror', error => { throw error; });
  let encoder;
  try {
    await page.goto(pathToFileURL(html).href + '?autoplay=0&export=1', { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    const resources = await page.evaluate(() => [...document.images].every(img => img.complete && img.naturalWidth > 0));
    if (!resources) throw new Error('An image did not load');
    const starts = await page.evaluate(() => window.__spiVideo.starts);
    const actualDuration = await page.evaluate(() => window.__spiVideo.duration);
    if (actualDuration !== duration || starts.at(-1) !== duration) throw new Error('HTML and renderer timing disagree');
    if (process.argv.includes('--review')) {
      const samples = starts.slice(0, -1).map((s, i) => s + (starts[i + 1] - s) * .55);
      // Review all three DC states and both reset/backlight states as well.
      if (language === 'summary-zh') samples.push(.5, 7.5, 9, 16, 18, 22, 24, 30, 31.6, 34.6, 40.9);
      else samples.push(starts[5] + .7, starts[5] + (starts[6] - starts[5]) * .85, starts[6] + .6, starts[6] + (starts[7] - starts[6]) * .85);
      const findings = [];
      for (let i = 0; i < samples.length; i++) {
        await page.evaluate(t => window.__spiVideo.seek(t), samples[i]);
        const issues = await page.evaluate(() => {
          const result = [];
          for (const el of document.querySelectorAll('#title,#sub,#note,#diagram text')) {
            const r = el.getBoundingClientRect();
            if (r.left < 125 || r.right > 1800 || r.top < 100 || r.bottom > 999) result.push({ text: el.textContent, box: r.toJSON() });
          }
          return result;
        });
        findings.push({ time: samples[i], issues });
        await page.screenshot({ path: path.join(out, `review-${language}-${String(i + 1).padStart(2, '0')}.png`) });
      }
      console.log(JSON.stringify({ language, findings }, null, 2));
      if (findings.some(f => f.issues.length)) throw new Error('Layout review found out-of-bounds text');
      return;
    }
    const fps = 30;
    const output = path.join(out, `${stem}.mp4`);
    if (fs.existsSync(output)) throw new Error(`Output already exists: ${output}`);
    encoder = spawn('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-vcodec', 'mjpeg', '-i', 'pipe:0', '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-pix_fmt', 'yuv420p', '-frames:v', String(duration * fps), '-movflags', '+faststart', output], { stdio: ['pipe', 'ignore', 'pipe'] });
    let errors = '';
    encoder.stderr.on('data', data => { errors += data.toString(); });
    const done = once(encoder, 'close');
    encoder.stdin.on('error', () => {});
    for (let i = 0; i < duration * fps; i++) {
      await page.evaluate(t => window.__spiVideo.seek(t), i / fps);
      const frame = await page.screenshot({ type: 'jpeg', quality: 94 });
      if (encoder.exitCode !== null) throw new Error(errors || 'Encoder exited early');
      if (!encoder.stdin.write(frame)) await once(encoder.stdin, 'drain');
      if (i % (fps * 5) === 0) console.log(`${language}: ${i / fps}s / ${duration}s`);
    }
    encoder.stdin.end();
    const [code] = await done;
    if (code !== 0) throw new Error(errors || `ffmpeg exited ${code}`);
    console.log(JSON.stringify({ output, duration, fps, frames: duration * fps, width: 1920, height: 1080 }));
  } finally {
    if (encoder && encoder.exitCode === null) encoder.kill();
    await browser.close();
  }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
