# PRD: Automated Mobile Demo Recording for Monster Generator

## Summary
Create a one-command script `record_monster.sh` that:
- Launches a scripted, *mobile-sized* Playwright run of the generator at `/generate/?monster-key=<monster_key>`.
- Waits briefly for hydration and lazy assets.
- Records a smooth demo: pick the first power dropdown, select a “random dice” option, then open the statblock.
- Produces a compressed MP4 (optionally a GIF) suitable for web and social.

## Goals
- Zero-manual, repeatable video capture for any `monster_key`.
- Mobile-first framing (iPhone-like viewport) since most viewers are on phones.
- Human-like cursor motion and gentle scrolls so it doesn’t look like a glitchy QA bot.
- Deterministic output filenames for automation.

## Non-Goals
- Full E2E correctness testing.
- Multi-step scripted tours across many powers or filters.
- Audio capture or VO mixing.

## Inputs
- Required CLI arg: `monster_key`
- Optional env/config:
  - `BASE_URL` (default `https://foefoundry.com`)
  - `DEVICE_NAME` (default Playwright device `iPhone 15 Pro`)
  - `PREROLL_SEC` (default `2`)
  - `DURATION_SEC` (default `15`)
  - `OUT_DIR` (default `./out`)
  - `FFMPEG_FLAGS` (default tuned for web)

## User Stories
- As a GM-toolmaker, I can run `./record_monster.sh assassin` and get a polished phone-format demo video without touching a mouse.

## Flow Narrative (Mobile)
1. Launch Playwright with `iPhone 15 Pro` emulation, video recording on.
2. Navigate to `${BASE_URL}/generate/?monster-key=${monster_key}`.
3. Wait:
   - network idle or DOM hydration signal,
   - critical selectors present.
4. Short pause (pre-roll to trim).
5. Smooth cursor glide to the first power dropdown; open it.
6. Select the “random dice” option in the dropdown.
7. Soft scroll to the statblock area if offscreen.
8. Smooth tap/click to open the statblock.
9. Hold for a beat to let the viewer actually read something.
10. Close and write video; postprocess via ffmpeg to trim pre-roll and compress.

## UX/Choreography Requirements
- **Smoothness**: All mouse moves use multi-step interpolation (`page.mouse.move(..., { steps: 20–40 })`).
- **Timing**: Human-like pauses: 300–600ms between steps, 800–1200ms after major UI changes.
- **Scroll**: Use `element.scrollIntoView` plus a small incremental scroll for natural motion.
- **Visibility**: Ensure the dropdown and statblock are within viewport before interacting.

## Technical Requirements

### Tech Stack
- **Playwright** (Node/TS) with built-in video recording.
- **ffmpeg** for trimming and compression.
- Bash wrapper `record_monster.sh`.

### Device Profile
- Playwright device: `iPhone 15 Pro`  
  - Viewport ~ 393x852, DPR ~ 3, mobile UA, touch enabled.

### Selectors (Component-based, override via config)
Use the following selectors based on the current implementation:
  - **Root container for hydration:** `.pamphlet-main`
  - **First power dropdown:** `.power-button` inside the first `power-loadout` element
  - **Random dice option:** `.dropdown-item` with text matching `/Randomize/i` and a dice icon (SVG)
  - **Statblock open:** Switch to the statblock tab/panel; ensure `.statblock-wrapper` is visible (no button required)

Fallbacks:
  - `.power-row select, .power-row [role="button"]` first match
  - Dropdown option containing text `/random/i` and dice icon text if present
  - Button containing text `/statblock/i`

Provide overrides via a JSON config file (`selectors.json`) if your DOM differs.

### Resilience
- Wait for hydrated root: `[data-testid="generator-root"]`.
- Guard for lazy content: `await page.waitForLoadState('networkidle')` and explicit selectors.
- Retry significant clicks up to 2 times if not visible or detached.
- Timeouts: default 20s for page load, 3–5s for element waits.

### Video Handling
- Playwright records from context start. We include 2s pre-roll, then **ffmpeg** trims `PREROLL_SEC` from head.
- Output:
  - Raw webm: `${OUT_DIR}/${monster_key}/raw.webm`
  - Final mp4: `${OUT_DIR}/${monster_key}/demo.mp4`
  - Optional gif: `${OUT_DIR}/${monster_key}/demo.gif`

## Acceptance Criteria
- Running `./record_monster.sh assassin` yields `/cache/record-monster/assassin.mp4`.
- Video shows: page load → dropdown open → random dice select → statblock open.
- Movements are smooth, no frantic flickers, text is legible, no cut-off UI.
- Script exits non-zero if any required element is missing, with readable stderr.

## Risks & Mitigations
- **Selector drift**: Mitigate via `selectors.json` overrides and stable data-testids in the app.
- **Hydration lag on slow net**: generous timeouts + networkidle + required selector waits.
- **Mobile layout variance**: test across `iPhone 15 Pro` and `iPhone SE` if needed; keep one default.

## Implementation Plan

### 1) Repo Structure
```
/scripts
  /record-monster
      record_monster.sh
      playwright-demo.ts
      package.json
      playwright.config.ts
/cache
   /record-monster
      <monster_key>.mp4
```

### 2) Bash Wrapper (`record_monster.sh`)
- Validate args and prerequisites (node, npx, ffmpeg).
- Export env vars (BASE_URL, DEVICE_NAME, etc).
- `npx playwright install --with-deps` on first run.
- `node scripts/playwright-demo.js --monster <key> ...`
- Run `ffmpeg` to trim and compress.
- Print final path.

### 3) Playwright Script (`playwright-demo.ts`)
- Parse CLI args.
- Load device descriptor.
- Create context with `recordVideo`.
- Navigate, wait, perform choreography with smooth mouse moves and scrolls.
- Close to finalize video.

### 4) ffmpeg Postprocess
- Trim first `PREROLL_SEC` seconds.
- Re-encode H.264, AAC (even if silent), fast-start for web.
- Optional GIF with palette for small social previews.

## Configuration
`selectors.json` (optional):
```json
{
  "root": "[data-testid=\"generator-root\"]",
  "firstPowerDropdown": "[data-testid=\"power-0-dropdown\"]",
  "randomDiceOption": "[data-testid=\"power-random-dice\"]",
  "openStatblock": "[data-testid=\"open-statblock\"]"
}
```

## Example Code

### `record_monster.sh`
```bash
#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <monster_key> [base_url]" >&2
  exit 2
fi

MONSTER_KEY="$1"
BASE_URL="${2:-https://foefoundry.com}"
DEVICE_NAME="${DEVICE_NAME:-iPhone 15 Pro}"
PREROLL_SEC="${PREROLL_SEC:-2}"
DURATION_SEC="${DURATION_SEC:-15}"
OUT_DIR="${OUT_DIR:-./out}"
FFMPEG_FLAGS="${FFMPEG_FLAGS:--movflags +faststart -preset veryfast -crf 23 -pix_fmt yuv420p}"

RAW_DIR="${OUT_DIR}/${MONSTER_KEY}"
RAW_WEBM="${RAW_DIR}/raw.webm"
FINAL_MP4="${RAW_DIR}/demo.mp4"

mkdir -p "$RAW_DIR"

command -v node >/dev/null || { echo "node is required"; exit 3; }
command -v npx  >/dev/null || { echo "npx is required"; exit 3; }
command -v ffmpeg >/dev/null || { echo "ffmpeg is required"; exit 3; }

# Install browsers if missing
npx playwright install --with-deps >/dev/null

# Run Playwright demo
node scripts/playwright-demo.js \
  --monster "$MONSTER_KEY" \
  --base "$BASE_URL" \
  --device "$DEVICE_NAME" \
  --out "$RAW_DIR" \
  --duration "$DURATION_SEC"

# Post-process with ffmpeg: trim preroll and compress
ffmpeg -y -i "$RAW_WEBM" -ss "$PREROLL_SEC" -t "$DURATION_SEC" \
  -c:v libx264 -r 30 $FFMPEG_FLAGS -an "$FINAL_MP4"

echo "✅ Demo ready: $FINAL_MP4"
```

### `playwright-demo.ts`
```ts
import { chromium, devices } from 'playwright';
import fs from 'fs';
import path from 'path';

type Sel = { root: string; firstPowerDropdown: string; randomDiceOption: string; openStatblock: string; };

function arg(name: string, def?: string) {
  const idx = process.argv.indexOf(`--${name}`);
  if (idx > -1 && process.argv[idx + 1]) return process.argv[idx + 1];
  if (def !== undefined) return def;
  throw new Error(`Missing --${name}`);
}

(async () => {
  const monster = arg('monster');
  const base = arg('base', 'https://foefoundry.com');
  const deviceName = arg('device', 'iPhone 15 Pro');
  const outDir = arg('out', './out');
  const duration = parseInt(arg('duration', '15'), 10);

  const url = `${base.replace(/\/$/, '')}/generate/?monster-key=${encodeURIComponent(monster)}`;
  const device = (devices as any)[deviceName] || devices['iPhone 15 Pro'];

  const selDefaults: Sel = {
  // Root container for hydration (MonsterBuilder's shadowRoot)
  root: '.pamphlet-main',
  // First power dropdown: find MonsterBuilder > MonsterCard > first power-loadout, then its shadowRoot .power-button
  firstPowerDropdown: 'monster-builder >>> monster-card >>> power-loadout:first-of-type >>> .power-button',
  // Random dice option: inside the open dropdown in first power-loadout's shadowRoot, .dropdown-item with text /Randomize/i and dice icon
  randomDiceOption: 'monster-builder >>> monster-card >>> power-loadout:first-of-type >>> .dropdown-menu .dropdown-item:has(svg[src*="dice"])',
  // Statblock open: MonsterCard's shadowRoot, click tab with text /Statblock/i, then ensure .statblock-wrapper is visible
  openStatblock: 'monster-builder >>> monster-card >>> .content-tab:has-text("Statblock")'
  };

  const browser = await chromium.launch({ headless: true, slowMo: 100 });
  const context = await browser.newContext({
    ...device,
    recordVideo: { dir: outDir, size: device.viewport },
    viewport: device.viewport,
    userAgent: device.userAgent
  });

  const page = await context.newPage();

  // Helper: smooth move
  async function glideTo(x: number, y: number, steps = 30) {
    const box = await page.viewportSize();
    if (!box) return;
    // Clamp-ish for safety
    const cx = Math.max(1, Math.min(box.width - 1, x));
    const cy = Math.max(1, Math.min(box.height - 1, y));
    await page.mouse.move(cx, cy, { steps });
  }

  // Helper: focus + smooth click
  async function smoothClick(locator: string) {
    const el = page.locator(locator);
    await el.waitFor({ state: 'visible', timeout: 8000 });
    const box = await el.boundingBox();
    if (box) {
      await glideTo(box.x + box.width / 2, box.y + box.height / 2, 35);
    } else {
      await el.scrollIntoViewIfNeeded();
    }
    await page.waitForTimeout(300);
    await el.click({ delay: 50 });
  }

  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForLoadState('networkidle', { timeout: 20000 });
    await page.locator(sel.root).waitFor({ state: 'visible', timeout: 20000 });

    // Pre-roll pause for later trim
    await page.waitForTimeout(2000);

    // 1) Open the first power dropdown
    const power = page.locator(sel.firstPowerDropdown).first();
    await power.scrollIntoViewIfNeeded();
    {
      const box = await power.boundingBox();
      if (box) await glideTo(box.x + box.width / 2, box.y + box.height / 2, 40);
    }
    await page.waitForTimeout(300);
    await power.click({ delay: 50 });

    // 2) Select the random dice option
    const randomOpt = page.locator(sel.randomDiceOption);
    await randomOpt.waitFor({ state: 'visible', timeout: 8000 });
    {
      const box = await randomOpt.boundingBox();
      if (box) await glideTo(box.x + box.width / 2, box.y + box.height / 2, 28);
    }
    await page.waitForTimeout(250);
    await randomOpt.click({ delay: 50 });

    // 3) Show the statblock
    const sb = page.locator(sel.openStatblock);
    await sb.scrollIntoViewIfNeeded();
    {
      const box = await sb.boundingBox();
      if (box) await glideTo(box.x + box.width / 2, box.y + box.height / 2, 30);
    }
    await page.waitForTimeout(350);
    await sb.click({ delay: 60 });

    // Let people actually see it
    await page.waitForTimeout(Math.max(3000, duration * 1000 - 6000));
  } finally {
    await context.close(); // finalizes video to outDir
    await browser.close();
  }

  // Rename the last recorded webm to raw.webm for predictability
  const vids = fs.readdirSync(outDir).filter(f => f.endsWith('.webm')).map(f => path.join(outDir, f));
  vids.sort((a, b) => fs.statSync(b).mtimeMs - fs.statSync(a).mtimeMs);
  if (vids[0]) {
    const raw = path.join(outDir, 'raw.webm');
    fs.renameSync(vids[0], raw);
  }
})();
```

### `package.json` (scripts)
```json
{
  "name": "foe-foundry-demo-recorder",
  "private": true,
  "type": "module",
  "scripts": {
    "record": "ts-node scripts/playwright-demo.ts"
  },
  "dependencies": {
    "playwright": "^1.46.0"
  },
  "devDependencies": {
    "ts-node": "^10.9.2",
    "typescript": "^5.5.4"
  }
}
```

### `playwright.config.ts` (minimal)
```ts
import { defineConfig } from '@playwright/test';
export default defineConfig({ timeout: 60000 });
```

## QA Checklist
- [ ] `record_monster.sh goblin` runs without interactive prompts.
- [ ] Video shows all three actions in order with smooth motion.
- [ ] Works on local dev and prod URL (use `BASE_URL=http://localhost:8000`).
- [ ] Fails fast with readable errors if selectors are missing.
- [ ] Output lands in `./out/<monster_key>/demo.mp4`.

## Future Enhancements
- Watermark/bug overlay, intro/outro bumpers.
- Multiple takes: fast, slow, alt paths (filters, reroll).
- Automatic caption burn-in.