import { getFeatureFlags } from '../utils/growthbook.js';

// Wait for features to be available
(async () => {
    await setupTutorial();
})();

async function setupTutorial() {
    // check feature flags
    const flags = await getFeatureFlags();

    if (flags.showTutorial) {
        console.log("show-tutorial is on");

        // Enable all statblock-tutorial elements on the page
        const tutorialElements = document.querySelectorAll('statblock-tutorial');
        tutorialElements.forEach((element: any) => {
            element.enabled = true;
        });
    } else {
        console.log("show-tutorial is off");
    }
}
