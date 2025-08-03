# Foe Foundry Analytics Strategy — GA4 Integration

## Overview

This document defines the analytics strategy for Foe Foundry using **Google Analytics 4 (GA4)** with **BigQuery export** enabled. It outlines the events to be tracked, describes the implementation approach, and details how to wrap and centralize analytics tracking across the site.

## Goals

- Track meaningful user interactions (reroll, forge, edit)
- Attribute conversions to traffic source and landing page type
- Enable funnel analysis: who engages, who explores, who converts
- Provide a scalable path for future event logging or multi-platform analytics

---

## Analytics Stack

| Layer         | Tool                         |
|---------------|------------------------------|
| Event Tracking | `gtag.js` (Google Analytics 4) |
| Data Export   | GA4 → BigQuery (daily export) |
| Query Engine  | BigQuery SQL                 |
| Optional BI   | Looker Studio or Observable  |

---

## Events to Track

- `reroll_button_click`
  - trigger: user clicked the `RerollButton` component
  - parameters: `page_type`, `monster_template`, `monster_key`
  - note: mark as a conversion event
- `forge_button_click`
  - trigger: user clicked the `ForgeButton` component
  - parameters: `page_type`, `monster_template`, `monster_key`
  - note: mark as a conversion event
- `statblock_edited`
  - trigger:
    - **user** took an action such that the `onStatblockChanged` event fired in `MonsterBuilder`
    - OR **user** changed the `monster_key` of the `MonsterBuilder`
    - NOTE - only trigger this based on a user action, not based on the initial load/render of the component
    - parameters: `page_type`, `monster_template`, `monster_key`, `power_key`, `change_type` ("rerolled", "power-changed", "damage-changed", "hp-changed", "monster-changed")
- `email_subscribe_click`
  - trigger: user clicked on the "Subscribe" button via the [[@Subscribe]] markdown helper
    - note: this may require first creating a dedicated `EmailSubscribeCallout` component and refactoring the jinja code to just use this custom component

**Notes:**
- `page_type` can be: `homepage`, `generator`, `monster_page`, `blog_post` based on the current category of page
- Use `monster_template` to be the key of the monster template
- Use `monster_key` to distinguish the specific monster used within the template

---

## EmailSubscribeCallout

Right now, there is a markdown utility that translates things like [[@Subscribe to the Newsletter]] into custom HTML via a jinja extension.

This logic needs to be encapsulated into a lit.js component in src/components/EmailSubscribeCallout.

This component should encapsulate the current logic and styles. Rather than copy the styles directly into the host, use the `adoptCssStyles` to adopt site.css for simplicity (see other similar components).

We need to make this refactor so that we can later hook into the subscribe click and add logging (and so it's easier to change in the future)

---

## Event Wrapping Strategy

All analytics events will be funneled through a **central JS logging utility** to ensure consistency and flexibility.

### Logging Wrapper (`analytics.js`)

```js
export function trackEvent(name, params = {}) {
  if (typeof gtag !== 'undefined' && process.env.NODE_ENV === 'production') {
    gtag('event', name, params);
  }

  // Optional: Add internal logging or backup API
  // fetch('/log', { method: 'POST', body: JSON.stringify({ name, params }) });
}
```

### Usage Example in Component

```js
import { trackEvent } from './analytics';

trackEvent('reroll_click', {
  page_type: 'generator',
  monster_template: 'Fire Elemental',
  variant_id: 'abc123',
});
```

---

## GA4 to BigQuery Setup

- Enable GA4 → BigQuery export (daily)
- Dataset: `analytics_foefoundry`
- Use `_TABLE_SUFFIX` to query across days
- Flatten `event_params` in SQL for custom fields

---

## Query Examples

### Reroll Rate by Source and Page Type

```sql
SELECT
  traffic_source.source,
  event_params.page_type.value.string_value AS page_type,
  COUNT(*) AS reroll_count
FROM
  `foefoundry.analytics_XXXX.events_*`,
  UNNEST(event_params) AS event_params
WHERE
  _TABLE_SUFFIX BETWEEN '20250801' AND '20250807'
  AND event_name = 'reroll_click'
  AND event_params.key = 'page_type'
GROUP BY
  traffic_source.source, event_params.page_type.value.string_value
```

---

## Deliverables

- [ ] Refactor the [[@Subscribe]] style custom markdown that translates to the subscribe jinja template into a lit.js `EmailSubscribeCallout` custom component (similar to other components in docs/src/components/) 
- [ ] Create `analytics.js` wrapper around ga4 and import in all components
- [ ] Hook into all relevant UI interactions with `trackEvent(...)`

---

## Owner

- **Analytics Lead**: Evan Rash  
- **Implementation**: Web Dev team (Foe Foundry)