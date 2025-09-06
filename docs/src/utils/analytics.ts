
/// <reference types="vite/client" />
/**
 * Analytics tracking utility for Foe Foundry
 * Provides a centralized wrapper around Google Analytics 4 (GA4) and GrowthBook
 */

import { StatblockChangeType } from '../data/monster.js';
import { trackGrowthBookEvent } from './growthbook.js';

// Global gtag type declaration
declare global {
  interface Window {
    gtag?: (...args: any[]) => void;
  }
}

export type PageType = 'homepage' | 'generator' | 'monster-page' | 'power' | 'blog-post' | 'codex' | 'other';

export interface AnalyticsParams {
  monster_key?: string;
  monster_change_type?: StatblockChangeType;
  power_key?: string;
  export_format?: string;
  search_query?: string;
  search_result_count?: number;
  monster_family?: string;
  codex_tab?: 'browse' | 'search';
  filter_type?: string;
  filter_value?: string;
}

/**
 * Track an analytics event
 */
export function trackEvent(name: string, params: AnalyticsParams = {}): void {
  // Check if we're in a browser environment
  if (typeof window === 'undefined') return;

  const pageType = getCurrentPageType();
  const args = {
    page_type: pageType,
    ...params
  };

  // Track to Google Analytics if available and in production
  if (typeof window.gtag !== 'undefined' && import.meta.env.PROD) {
    window.gtag('event', name, args);
  }

  // Track to GrowthBook
  trackGrowthBookEvent(name, args);

  // Log in development for debugging
  if (!import.meta.env.PROD) {
    console.log('Analytics Event:', name, args);
  }
}

/**
 * Get the current page type based on the URL path
 */
export function getCurrentPageType(): PageType {
  if (typeof window === 'undefined') return 'other';

  const path = window.location.pathname;

  if (path === '/' || path === '/index.html') {
    return 'homepage';
  } else if (path.includes('/generate/')) {
    return 'generator';
  } else if (path.includes('/monsters/')) {
    return 'monster-page';
  } else if (path.includes('/powers/')) {
    return 'power';
  } else if (path.includes('/blog/')) {
    return 'blog-post';
  } else if (path === '/codex/' || path === '/codex') {
    return 'codex';
  } else {
    return 'other';
  }
}

/**
 * Track reroll button click
 */
export function trackRerollClick(monsterKey: string): void {
  trackEvent('reroll_button_click', {
    monster_key: monsterKey,
  });
}

/**
 * Track forge button click
 */
export function trackForgeClick(monsterKey: string): void {
  trackEvent('forge_button_click', {
    monster_key: monsterKey,
  });
}

/**
 * Track statblock edit
 */
export function trackStatblockEdit(monsterKey: string, changeType: StatblockChangeType, powerKey?: string): void {
  trackEvent('statblock_edited', {
    monster_key: monsterKey,
    monster_change_type: changeType,
    power_key: powerKey,
  });
}

/**
 * Track download button click
 */
export function trackDownloadClick(monsterKey: string, format?: string): void {
  const params: AnalyticsParams = {
    monster_key: monsterKey,
  };
  
  // Add format type if provided
  if (format) {
    params.export_format = format;
  }
  
  trackEvent('download_button_click', params);
}

/**
 * Track email subscribe click
 */
export function trackEmailSubscribeClick(): void {
  trackEvent('email_subscribe_click');
}

/**
 * Track codex search performed
 */
export function trackCodexSearch(query: string, resultCount: number): void {
  trackEvent('codex_search_performed', {
    search_query: query,
    search_result_count: resultCount,
    codex_tab: 'search',
  });
}

/**
 * Track monster family click in browse tab
 */
export function trackCodexMonsterFamilyClick(monsterKey: string, familyName: string): void {
  trackEvent('codex_monster_family_click', {
    monster_key: monsterKey,
    monster_family: familyName,
    codex_tab: 'browse',
  });
}

/**
 * Track search result click in search tab
 */
export function trackCodexSearchResultClick(monsterKey: string, query?: string): void {
  trackEvent('codex_search_result_click', {
    monster_key: monsterKey,
    search_query: query,
    codex_tab: 'search',
  });
}

/**
 * Track forge button click from codex
 */
export function trackCodexForgeClick(monsterKey: string, tab: 'browse' | 'search'): void {
  trackEvent('codex_forge_click', {
    monster_key: monsterKey,
    codex_tab: tab,
  });
}

/**
 * Track statblock view button click from codex
 */
export function trackCodexStatblockClick(monsterKey: string, tab: 'browse' | 'search'): void {
  trackEvent('codex_statblock_click', {
    monster_key: monsterKey,
    codex_tab: tab,
  });
}

/**
 * Track codex filter usage
 */
export function trackCodexFilterUsage(filterType: string, filterValue: string): void {
  trackEvent('codex_filter_used', {
    filter_type: filterType,
    filter_value: filterValue,
    codex_tab: 'search',
  });
}
