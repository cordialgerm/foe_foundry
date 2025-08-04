
/// <reference types="vite/client" />
/**
 * Analytics tracking utility for Foe Foundry
 * Provides a centralized wrapper around Google Analytics 4 (GA4)
 */

import { StatblockChangeType } from '../data/monster.js';

// Global gtag type declaration
declare global {
  interface Window {
    gtag?: (...args: any[]) => void;
  }
}

export type PageType = 'homepage' | 'generator' | 'monster-page' | 'power' | 'blog-post' | 'other';

export interface AnalyticsParams {
  monster_key?: string;
  monster_change_type?: StatblockChangeType;
  power_key?: string;
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

  // Only track in production and if gtag is available
  if (typeof window.gtag !== 'undefined' && import.meta.env.PROD) {
    window.gtag('event', name, args);
  }

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
 * Track email subscribe click
 */
export function trackEmailSubscribeClick(): void {
  trackEvent('email_subscribe_click');
}
