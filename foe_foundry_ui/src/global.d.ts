import type {
    trackMonsterClick,
    trackRerollClick,
    trackForgeClick,
    trackStatblockClick,
    trackStatblockEdit,
    trackDownloadClick,
    trackEmailSubscribeClick,
    trackSearch,
    trackFilterUsage
} from './utils/analytics';

declare global {
    interface Window {
        baseUrl?: string;
        defaultMonsterKey: string;
        foeFoundryAnalytics?: {
            trackMonsterClick: typeof trackMonsterClick;
            trackRerollClick: typeof trackRerollClick;
            trackForgeClick: typeof trackForgeClick;
            trackStatblockClick: typeof trackStatblockClick;
            trackStatblockEdit: typeof trackStatblockEdit;
            trackDownloadClick: typeof trackDownloadClick;
            trackEmailSubscribeClick: typeof trackEmailSubscribeClick;
            trackSearch: typeof trackSearch;
            trackFilterUsage: typeof trackFilterUsage;
        };
    }
}

export { };
