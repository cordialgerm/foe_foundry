/// <reference types="vite/client" />
/**
 * GrowthBook utility for Foe Foundry
 * Provides a centralized GrowthBook instance for feature flags and experiments
 */

import { GrowthBook, TrackingCallback } from "@growthbook/growthbook";
import { autoAttributesPlugin } from "@growthbook/growthbook/plugins";
import { thirdPartyTrackingPlugin } from "@growthbook/growthbook/plugins";

// Singleton GrowthBook instance
let growthbookInstance: GrowthBook | null = null;

// Singleton FeatureFlags instance
let featureFlagsInstance: FeatureFlags | null = null;

/**
 * Get or create the GrowthBook instance
 */
export function getGrowthBook(): GrowthBook {
    if (!growthbookInstance) {
        const clientKey = import.meta.env.VITE_GROWTHBOOK_CLIENT_KEY;
        const isDev = import.meta.env.DEV;

        // Optional settings for the plugin
        const trackingCallback: TrackingCallback = (experiment, result) => {
            console.log("Experiment Viewed", {
                experimentId: experiment.key,
                variationId: result.key,
            });
        };
        const trackingPlugin = thirdPartyTrackingPlugin({
            additionalCallback: trackingCallback
        });
        growthbookInstance = new GrowthBook({
            apiHost: "https://cdn.growthbook.io",
            clientKey: clientKey,
            enableDevMode: isDev,
            plugins: [autoAttributesPlugin(), trackingPlugin],
        });
    }

    return growthbookInstance;
}

/**
 * Initialize GrowthBook with streaming enabled
 * Call this once when your app starts
 */
export async function initGrowthBook(): Promise<GrowthBook> {
    const gb = getGrowthBook();
    await gb.init({ streaming: true });
    return gb;
}

/**
 * Track a custom event to GrowthBook
 */
export function trackGrowthBookEvent(event: string, properties?: Record<string, any>): void {
    const gb = getGrowthBook();

    // If GrowthBook has a track method, use it
    if (typeof (gb as any).track === 'function') {
        (gb as any).track(event, properties);
    }

    // Also log for debugging
    if (!import.meta.env.PROD) {
        console.log('GrowthBook Event:', event, properties);
    }
}

/**
 * Easy access to feature flags
 */
export interface FeatureFlags {
    readonly showTutorial: boolean;
    readonly showStatblockDownloadOptions: boolean;
    readonly showSkullUpsell: boolean;
}

/**
 * Get a FeatureFlags object with property-based access to feature flags
 */
export async function getFeatureFlags(): Promise<FeatureFlags> {

    const gb = await initGrowthBook();

    if (!featureFlagsInstance) {
        featureFlagsInstance = {
            get showTutorial(): boolean {
                return gb.isOn("show-tutorial");
            },
            get showStatblockDownloadOptions(): boolean {
                return gb.isOn("show-statblock-download-options");
            },
            get showSkullUpsell(): boolean {
                return gb.isOn("show-skull-upsell");
            }
        };
    }
    return featureFlagsInstance;
}
