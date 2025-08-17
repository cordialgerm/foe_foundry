import type { Locator, Page } from 'playwright';
import { chromium, devices } from 'playwright';
import fs from 'fs';
import path from 'path';

// Custom window type for ripple animation injection
type RippleWindow = typeof window & {
    showRipple: (x: number, y: number) => void;
    movePlaywrightCursor: (x: number, y: number) => void;
};


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
    let p: import('playwright').Page | undefined;
    try {
        browser = await chromium.launch({ headless: false, slowMo: 100 });
        context = await browser.newContext({
            ...device,
            viewport: { width: 393, height: 852 },
            isMobile: true,
            recordVideo: { dir: outDir, size: { width: 393, height: 852 } }, // iPhone 15 Pro physical pixels
        });
        p = await context.newPage();
        if (!p) {
            throw Error("Page doesn't exist")
        }
        const page = p;

        // Forward browser console logs to Node.js terminal
        page.on('console', msg => {
            // Print browser logs with their type
            console.log(`[browser][${msg.type()}]`, ...msg.args().map(arg => arg.toString()), msg.text());
        });

        // hide the beta banner
        // Inject ripple helper and cursor at page startup
        await page.addInitScript(() => {
            localStorage.setItem("hideBetaBanner", "true");
            localStorage.setItem("foe-foundry-power-tutorial-seen", "true");
        });

        console.log(`[record-monster] Navigating to page...`);
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });

        console.log(`[record-monster] Waiting for network idle...`);
        await page.waitForLoadState('networkidle', { timeout: 20000 });

        // Inject ripple helper and cursor helper
        await page.evaluate(() => {
            const w = window as RippleWindow;
            const style = document.createElement('style');
            style.textContent = `
        .playwright-ripple {
            position: fixed;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.7);
            box-shadow: 0 0 8px 2px rgba(255,255,255,0.8);
            pointer-events: none;
            width: 40px;
            height: 40px;
            transform: translate(-50%, -50%) scale(0.5);
            animation: ripple-anim 0.5s ease-out forwards;
            z-index: 9999;
        }
        @keyframes ripple-anim {
            to {
                opacity: 0;
                transform: translate(-50%, -50%) scale(2.5);
            }
        }
        .playwright-cursor {
            position: fixed;
            width: 32px;
            height: 32px;
            pointer-events: none;
            z-index: 10000;
            background: url('data:image/svg+xml;utf8,<svg width="32" height="32" xmlns="http://www.w3.org/2000/svg"><polygon points="0,0 32,16 16,32" fill="black" stroke="white" stroke-width="2"/></svg>') no-repeat center center;
        }
    `;
            document.head.appendChild(style);
            w.showRipple = (x: number, y: number) => {
                console.log('[playwright ripple] showRipple called at', x, y);
                const ripple = document.createElement('div');
                ripple.className = 'playwright-ripple';
                ripple.style.left = `${x}px`;
                ripple.style.top = `${y}px`;
                document.body.appendChild(ripple);
                setTimeout(() => ripple.remove(), 500);
            };
            // Inject cursor element and movement function
            const cursor = document.createElement('div');
            cursor.className = 'playwright-cursor';
            cursor.style.left = '0px';
            cursor.style.top = '0px';
            document.body.appendChild(cursor);
            w.movePlaywrightCursor = (x: number, y: number) => {
                console.log('[playwright cursor] moved to', x, y);
                cursor.style.left = `${x - 4}px`;
                cursor.style.top = `${y - 4}px`;
            };
        });

        console.log(`[record-monster] Waiting for root selector: ${selDefaults.root}`);
        await page.locator(selDefaults.root).waitFor({ state: 'visible', timeout: 20000 });

        // Set the cursor in a good initial position
        await moveCursor(page, 150, 300);

        // Check that all the items we expect exist
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
            } else {
                throw new Error(`[record-monster] ERROR: Could not find element for selector: ${sel}`);
            }
        }
        // Now wait for each to be visible
        for (const sel of selectors) {
            await page.locator(sel).first().waitFor({ state: 'visible', timeout: 20000 });
        }

        // Start Sequence
        await page.waitForTimeout(800);
        await smoothScroll(page, 600, 800);


        //Select a random power-loadout that has 2 or more dropdown items
        console.log(`[record-monster] Opening first power dropdown...`);
        const allPowerLoadouts = await page.locator(selectors[2]).all();
        const powerLoadouts = [];
        for (const loadout of allPowerLoadouts) {
            const items = await loadout.locator('.power-slot-block >>> .dropdown-container >>> .dropdown-menu >>> .dropdown-item').all();
            if (items.length >= 2) {
                powerLoadouts.push(loadout);
            }
        }
        if (powerLoadouts.length === 0) {
            throw new Error('[record-monster] No power-loadouts with 2 or more dropdown items found.');
        }
        const randomPowerLoadout = powerLoadouts[Math.floor(Math.random() * powerLoadouts.length)];

        // Open the dropdown for a random power-loadout
        const powerButton = randomPowerLoadout.locator('.power-slot-block >>> .dropdown-container >>> .power-button');
        await powerButton.waitFor({ state: 'visible', timeout: 20000 });
        await smoothClick(page, powerButton);

        // Select the random dice option
        console.log(`[record-monster] Selecting random dice option...`);
        const individualPowers = await randomPowerLoadout.locator('.power-slot-block >>> .dropdown-container >>> .dropdown-menu >>> .dropdown-item').all();
        const buttonToClick = individualPowers[Math.floor(Math.random() * individualPowers.length)];
        await buttonToClick.waitFor({ state: 'visible', timeout: 8000 });
        await smoothClick(page, buttonToClick);

        //Open the Statblock
        console.log(`[record-monster] Opening statblock...`);
        await page.waitForTimeout(1250);

        const monsterBuilder = await page.locator('monster-builder').first();
        const mobileTabs = monsterBuilder.locator('.pamphlet-main >>> .mobile-tabs').first();
        await smoothGlideTo(page, mobileTabs);
        await playRippleAt(page, mobileTabs);
        await monsterBuilder.evaluate((el: any) => el.setMobileTab('statblock'));

        console.log(`[record-monster] Holding for viewer...`);
        await page.waitForTimeout(1000);

        console.log('[record-monster] Slowly scroll down to the user can see the new statblock');
        await smoothScroll(page, 900, 6000);
        await page.waitForTimeout(1000);
        await smoothScroll(page, -900, 6000);
        await page.waitForTimeout(1000);

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

async function moveCursor(page: Page, x: number, y: number) {
    await page.evaluate(([x, y]) => {
        const w = window as any;
        w.movePlaywrightCursor(x, y);
    }, [x, y]);
}

async function moveCursorTo(page: Page, locator: Locator) {
    const box = await locator.boundingBox();
    if (!box) return;
    const x = box.x + box.width / 2;
    const y = box.y + box.height / 2;
    await moveCursor(page, x, y);
}



async function smoothGlideTo(page: Page, locator: Locator) {

    // Smoothly scroll the element into view and center it
    await locator.evaluate((el: any) => {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });

    // Show and move the cursor
    await moveCursorTo(page, locator);

    // Wait for the animation to finish
    await page.waitForTimeout(1800);
}

async function smoothClick(page: Page, locator: Locator) {

    // glide to the location
    await smoothGlideTo(page, locator);
    await page.waitForTimeout(300);

    // Get click coordinates and show ripple
    const box = await locator.boundingBox();
    if (box) {
        const x = box.x + box.width / 2;
        const y = box.y + box.height / 2;
        await page.evaluate(([x, y]) => {
            const w = window as RippleWindow;
            w.showRipple(x, y);
            w.movePlaywrightCursor(x, y);
        }, [x, y]);
    }

    // click on the locator
    await locator.click({ delay: 100 });
    await page.waitForTimeout(200);
}

async function playRippleAt(page: Page, locator: Locator) {
    const box = await locator.boundingBox();
    if (!box) return;
    const x = box.x + box.width / 2;
    const y = box.y + box.height / 2;
    await page.evaluate(([x, y]) => {
        const w = window as RippleWindow;
        w.movePlaywrightCursor(x, y);
        w.showRipple(x, y);
    }, [x, y]);
}

async function smoothScroll(page: Page, by: number, duration: number) {

    const stepSize = by > 0 ? 5 : -5;
    const steps = Math.floor(Math.abs(by / stepSize));

    // each scroll is modelled to take K milliseconds, so we have to reduce the sleep interval
    const scrollDuration = 0;
    const waitInterval = Math.max(duration / steps - scrollDuration, 0);


    for (let i = 0; i < steps; i++) {
        const m = 1.1 - 0.2 * Math.random();
        await page.evaluate(({ stepSize, m }) => {
            window.scrollBy({ top: m * stepSize, behavior: 'smooth' });
        }, { stepSize, m });

        if (waitInterval > 0) {
            await page.waitForTimeout(waitInterval);
        }
    }
}