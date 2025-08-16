import { chromium, devices } from 'playwright';
import fs from 'fs';
import path from 'path';

// Top-level error handlers for visibility
process.on('uncaughtException', (err) => {
    console.error('[record-monster] Uncaught Exception:', err);
    process.exit(1);
});
process.on('unhandledRejection', (reason, promise) => {
    console.error('[record-monster] Unhandled Rejection:', reason);
    process.exit(1);
});

console.log('[record-monster] Script started');

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
    const outDir = arg('out', './cache/record-monster');
    const duration = parseInt(arg('duration', '15'), 10);

    const url = `${base.replace(/\/$/, '')}/generate/?monster-key=${encodeURIComponent(monster)}`;
    const device = (devices as any)[deviceName] || devices['iPhone 15 Pro'];

    const selDefaults = {
        root: '.pamphlet-main',
    };

    console.log(`[record-monster] Starting demo for monster: ${monster}`);
    console.log(`[record-monster] URL: ${url}`);
    console.log(`[record-monster] Device: ${deviceName}`);
    console.log(`[record-monster] Output directory: ${outDir}`);

    let browser: import('playwright').Browser | undefined;
    let context: import('playwright').BrowserContext | undefined;
    let page: import('playwright').Page | undefined;
    try {
        browser = await chromium.launch({ headless: true, slowMo: 100 });
        context = await browser.newContext({
            ...device,
            recordVideo: { dir: outDir, size: device.viewport },
            viewport: device.viewport,
            userAgent: device.userAgent
        });
        page = await context.newPage();

        async function glideTo(x: number, y: number, steps = 30) {
            const box = await page!.viewportSize();
            if (!box) return;
            const cx = Math.max(1, Math.min(box.width - 1, x));
            const cy = Math.max(1, Math.min(box.height - 1, y));
            await page!.mouse.move(cx, cy, { steps });
        }

        async function smoothClick(locator: string) {
            const el = page!.locator(locator);
            await el.waitFor({ state: 'visible', timeout: 8000 });
            const box = await el.boundingBox();
            if (box) {
                await glideTo(box.x + box.width / 2, box.y + box.height / 2, 35);
            } else {
                await el.scrollIntoViewIfNeeded();
            }
            await page!.waitForTimeout(300);
            await el.click({ delay: 50 });
        }

        // hide the beta banner
        await page.addInitScript(() => {
            localStorage.setItem("hideBetaBanner", "true");
            localStorage.setItem('foe-foundry-power-tutorial-seen', 'true');
        });

        console.log(`[record-monster] Navigating to page...`);
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
        console.log(`[record-monster] Waiting for network idle...`);
        await page.waitForLoadState('networkidle', { timeout: 20000 });
        console.log(`[record-monster] Waiting for root selector: ${selDefaults.root}`);
        await page.locator(selDefaults.root).waitFor({ state: 'visible', timeout: 20000 });
        await page.waitForTimeout(2000);

        console.log(`[record-monster] Opening first power dropdown...`);

        // Enhanced locator logic: check for each item and print status
        const selectors = [
            'monster-builder',
            'monster-builder >>> .pamphlet-main >>> .panels-container >>> .card-panel >>> monster-card',
            'monster-builder >>> .pamphlet-main >>> .panels-container >>> .card-panel >>> monster-card >>> .monster-card >>> .tab-content-container >>> div[data-content="powers"] >>> power-loadout'
        ];

        for (const sel of selectors) {
            const el = page.locator(sel);
            const count = await el.count();
            if (count > 0) {
                console.log(`[record-monster] Found element(s) for selector: ${sel} (count: ${count})`);
                // const innerContent = await el.evaluate(el => el.shadowRoot ? el.shadowRoot.innerHTML : '[no shadowRoot]');
                // console.log('[record-monster] Inner Content:\n', innerContent)
            } else {
                throw new Error(`[record-monster] ERROR: Could not find element for selector: ${sel}`);
            }
        }
        // Now wait for each to be visible
        for (const sel of selectors) {
            await page.locator(sel).first().waitFor({ state: 'visible', timeout: 20000 });
        }

        //Select a random power-loadout
        const powerLoadouts = await page.locator(selectors[2]).all();
        const randomPowerLoadout = powerLoadouts[Math.floor(Math.random() * powerLoadouts.length)];

        // Open the dropdown for a random power-loadout
        const powerButton = randomPowerLoadout.locator('.power-slot-block >>> .dropdown-container >>> .power-button');
        await powerButton.waitFor({ state: 'visible', timeout: 20000 });
        await powerButton.scrollIntoViewIfNeeded();
        {
            const box = await powerButton.boundingBox();
            if (box) await glideTo(box.x + box.width / 2, box.y + box.height / 2, 40);
        }
        await page.waitForTimeout(300);
        await powerButton.click({ delay: 50 });

        // Select the random dice option
        console.log(`[record-monster] Selecting random dice option...`);
        const individualPowers = await randomPowerLoadout.locator('.power-slot-block >>> .dropdown-container >>> .dropdown-menu >>> .dropdown-item').all();
        const buttonToClick = individualPowers[Math.floor(Math.random() * individualPowers.length)];
        await buttonToClick.waitFor({ state: 'visible', timeout: 8000 });
        const box = await buttonToClick.boundingBox();
        if (box) await glideTo(box.x + box.width / 2, box.y + box.height / 2, 28);

        await page.waitForTimeout(250);
        await buttonToClick.click({ delay: 50 });

        //Open the Statblock
        console.log(`[record-monster] Opening statblock...`);
        await page.waitForTimeout(1250);

        const monsterBuilder = await page.locator('monster-builder').first();
        const mobileTabs = monsterBuilder.locator('.pamphlet-main >>> .mobile-tabs').first();
        await mobileTabs.scrollIntoViewIfNeeded()
        await monsterBuilder.evaluate((el: any) => el.setMobileTab('statblock'));

        console.log(`[record-monster] Holding for viewer...`);
        await page.waitForTimeout(Math.max(3000, duration * 1000 - 6000));

    } catch (err) {
        console.error(`[record-monster] ERROR:`, err);
    } finally {
        if (context) {
            await context.close();
        }
        if (browser) {
            await browser.close();
        }
    }

    // Check for video output
    const vids = fs.readdirSync(outDir).filter(f => f.endsWith('.webm')).map(f => path.join(outDir, f));
    vids.sort((a, b) => fs.statSync(b).mtimeMs - fs.statSync(a).mtimeMs);
    if (vids.length === 0) {
        console.error(`[record-monster] No video file generated in ${outDir}`);
    } else {
        const raw = path.join(outDir, 'raw.webm');
        fs.renameSync(vids[0], raw);
        console.log(`[record-monster] Video file saved as ${raw}`);
    }
    console.log('[record-monster] Script finished');
})();
