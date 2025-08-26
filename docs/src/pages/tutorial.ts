import { GrowthBook } from "@growthbook/growthbook";
import { autoAttributesPlugin } from "@growthbook/growthbook/plugins";

const growthbook = new GrowthBook({
    apiHost: "https://cdn.growthbook.io",
    clientKey: "sdk-aKoPKzaJK9otD0Cn",
    enableDevMode: true,
    trackingCallback: (experiment, result) => {
        // This is where you would send an event to your analytics provider
        console.log("Viewed Experiment", {
            experimentId: experiment.key,
            variationId: result.key
        });
    },
    plugins: [autoAttributesPlugin()],
});

// Wait for features to be available
(async () => {
    await setupTutorial();
})();

async function setupTutorial() {
    await growthbook.init({ streaming: true });

    if (growthbook.isOn("show-tutorial")) {
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
