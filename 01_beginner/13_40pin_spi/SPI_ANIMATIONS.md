# SPI signal explainer animations

Silent animations for the Lesson 13 voice-over, using the Lesson 12 paper-grid template.

| Version | HTML | Duration |
| --- | --- | --- |
| English | [Open animation](spi_explainer_55s.en.html) | 55 seconds |
| 中文 | [打开动画](spi_explainer_49s.zh.html) | 49 秒 |
| 中文课堂总结与排查 | [打开动画](spi_summary_41s.zh.html) | 41 秒 |

The 41-second recap uses `spi_summary.js` and the shared `spi_explainer.css`. It follows the supplied Chinese narration: recap (0–8s), missing device node (8–17s), backlight off (17–23s), blank image (23–31s), color test (31–35s), and animation settings/speed (35–41s). There is no burned-in timeline or time counter. It is silent, for editing underneath the recorded voice-over; timings can be adjusted in `spi_summary.js`.

Open either HTML file in a browser. Keep `spi_explainer.css`, `spi_explainer.js` and the repository logo available at their relative paths. The 1920×1080 design scales uniformly to fit the window; it does not reflow at smaller sizes.

Space pauses or resumes, arrow keys seek by two seconds, Home restarts, and End jumps to the end. Hover near the bottom to reveal the playback controls. URL parameters support `?autoplay=0&t=35` for a paused frame and `&export=1` to hide controls.

## Narration timing

| Scene | English | 中文 |
| --- | --- | --- |
| X5 generates SCLK | 0–11 s | 0–5 秒 |
| MOSI and MISO directions | 11–18 s | 5–12 秒 |
| Leave MISO disconnected | 18–22 s | 12–16 秒 |
| CS goes LOW to select the display | 22–31 s | 16–25 秒 |
| DC, RST and BL overview | 31–35 s | 25–29 秒 |
| DC LOW: command; HIGH: parameters and pixels | 35–46 s | 29–41 秒 |
| Reset pulse and backlight | 46–50 s | 41–45 秒 |
| SPI transfer and GPIO control recap | 50–55 s | 45–49 秒 |

Timing follows the supplied narration text. These files do not contain recorded speech; adjust the `starts` arrays in `spi_explainer.js` if a later recording needs different cue points. Signal waveforms are explanatory illustrations, not a measured logic-analyzer capture.

## Render MP4 directly from code

Requirements: Node.js, Playwright, Chrome or Chromium, and `ffmpeg` on PATH. Install Playwright in your rendering environment. Set `NODE_PATH` if using an existing installation and `CHROME_PATH` if the browser is not at the default Windows Chrome location.

Run from this lesson directory, using a new output directory or filenames that do not already exist:

```bash
node tools/render-spi-video.cjs en /path/to/output
node tools/render-spi-video.cjs zh /path/to/output
node tools/render-spi-video.cjs summary-zh /path/to/output
```

Outputs are H.264 MP4, 1920×1080, 30 fps, without audio. Every frame renders at an explicit timeline timestamp before encoding. Export does not record the desktop, depend on real-time playback, or rescale the video after capture. The English explainer contains exactly 1,650 frames; the Chinese explainer contains 1,470 frames; the Chinese recap contains 1,230 frames.

Add `--review` to render scene and signal-state previews instead of a video. The renderer also checks text bounds and logo loading.
