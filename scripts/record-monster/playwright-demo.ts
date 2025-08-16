import type { Locator, Page } from 'playwright';
import { chromium, devices } from 'playwright';
import fs from 'fs';
import path from 'path';

// Custom window type for ripple animation injection
type RippleWindow = typeof window & {
    __rippleHelperInjected?: boolean;
    showRipple?: (x: number, y: number) => void;
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
        browser = await chromium.launch({ headless: true, slowMo: 100 });
        context = await browser.newContext({
            ...device,
            deviceScaleFactor: 3,  // iPhone 15 pro
            recordVideo: { dir: outDir, size: { width: 3 * 393, height: 3 * 852 } }, // iPhone 15 Pro physical pixels (3x CSS)
            viewport: { width: 393, height: 852 }, // iPhone 15 Pro CSS pixels
            userAgent: device.userAgent,
            isMobile: true
        });
        p = await context.newPage();
        // Forward browser console logs to Node.js terminal
        p.on('console', msg => {
            // Print browser logs with their type
            console.log(`[browser][${msg.type()}]`, ...msg.args().map(arg => arg.toString()), msg.text());
        });
        if (!p) {
            throw Error("Page doesn't exist")
        }

        // Inject ripple helper at page startup
        await p.addInitScript(() => {
            const w = window as typeof window & {
                __rippleHelperInjected?: boolean;
                showRipple?: (x: number, y: number) => void;
            };
            if (!w.__rippleHelperInjected) {
                w.__rippleHelperInjected = true;
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
            }
        });

        const page = p;

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

        //Select a random power-loadout that has 2 or more dropdown items
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
        await monsterBuilder.evaluate((el: any) => el.setMobileTab('statblock'));

        console.log(`[record-monster] Holding for viewer...`);
        await page.waitForTimeout(1000);

        console.log('[record-monster] Slowly scroll down to the user can see the new statblock');
        for (let i = 0; i < 8; i++) {
            await smoothScroll(page, 120); // scroll down 120px
        }
        await page.waitForTimeout(2000);

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

async function smoothGlideTo(page: Page, locator: Locator, steps = 60) {

    // Smoothly scroll the element into view and center it
    await locator.evaluate((el: any) => {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    // Wait for the animation to finish
    await page.waitForTimeout(1800);

    // Get the bounding box after scrolling
    const box = await locator.boundingBox();
    if (!box) return;

    // Move mouse smoothly to the center of the element, with more steps for slower movement
    await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2, { steps: steps });
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
            if (w.showRipple) w.showRipple(x, y);
        }, [x, y]);
    }

    // click on the locator
    await locator.click({ delay: 100 });
    await page.waitForTimeout(200);
}

async function smoothScroll(page: Page, by: number) {
    const m = 1.2 - 0.4 * Math.random();
    await page.evaluate(({ by, m }) => {
        window.scrollTo({ top: window.scrollY + m * by, behavior: 'smooth' });
    }, { by, m });
    await page.waitForTimeout(m * 800);
}