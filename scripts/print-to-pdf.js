const puppeteer = require('puppeteer');

(async () => {
    const url = process.argv[2];
    const output = process.argv[3] || 'output.pdf';

    if (!url) {
        console.error('Usage: node print-to-pdf.js <url> [output.pdf]');
        process.exit(1);
    }

    // Append ?render=print or &render=print
    const fullUrl = url.includes('?') ? `${url}&render=print` : `${url}?render=print`;

    const browser = await puppeteer.launch({ headless: 'new' });
    const page = await browser.newPage();

    await page.goto(fullUrl, { waitUntil: 'networkidle0' });

    await new Promise(resolve => setTimeout(resolve, 250));  // 250ms wait so page can render fully

    await page.pdf({
        path: output,
        format: 'A4',
        printBackground: true,
        preferCSSPageSize: true,  // This respects your @page CSS rules
    });

    await browser.close();
})();