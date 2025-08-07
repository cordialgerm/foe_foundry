# Mobile Toast Notification: Powers Changed, Swap to Statblock?

## Feature Overview
When a user edits a power in the mobile layout of the MonsterBuilder component, a toast notification should appear near the bottom of the screen. The toast will display the message:

> "Powers Changed, Swap to Statblock?"

It will include a progress bar that fills up over a short duration (e.g., 3 seconds). If the user clicks anywhere on the toast or outside it, the notification is dismissed and the timer stops. If the timer completes without user interaction, the app automatically switches to the statblock tab.

## User Experience
- **Trigger:** Editing a power in mobile layout.
- **Toast Location:** Bottom of the screen, above any navigation or fixed elements.
- **Message:** "Powers Changed, Swap to Statblock?"
- **Progress Bar:** Visually fills up over the timer duration.
- **Dismissal:**
  - Clicking anywhere (toast or outside) dismisses the toast and cancels the timer.
  - If timer completes, automatically switch to statblock tab.
- **Accessibility:**
  - Toast should be keyboard accessible and screen-reader friendly.
  - Progress bar should be visually clear and not distracting.

## Technical Implementation
- **Trigger Point:** After a power edit event in mobile layout (`onStatblockChangeRequested` or similar).
- **Toast Component:** Should be a lightweight, reusable web component compatible with LitElement.
- **Progress Bar:** CSS animation or JS-driven width change.
- **Timer:** JS `setTimeout` for auto-switch; cleared on user interaction.
- **Dismissal:** Listen for click/touch events on toast and document.
- **Tab Switch:** Call `setMobileTab('statblock')` if timer completes.

## Libraries Assessment
### Requirements
- Must work seamlessly with LitElement (web components).
- Lightweight, minimal dependencies.
- Customizable appearance and behavior.
- Good accessibility support.

### Recommended Libraries
1. **No External Library (Custom Implementation):**
   - LitElement makes it easy to create a custom toast component with minimal code.
   - Full control over appearance, animation, and behavior.
   - No dependency or bundle size impact.
   - Recommended for this use case.

2. **shoelace.style (Shoelace Web Components):**
   - Shoelace provides a `sl-toast` component compatible with LitElement.
   - Highly customizable, accessible, and well-documented.
   - Slightly increases bundle size but is modular.
   - [Shoelace Toast Docs](https://shoelace.style/components/toast)

3. **Vaadin (vaadin-notification):**
   - Vaadin's notification component works with web components and LitElement.
   - More enterprise-focused, heavier than Shoelace.
   - [Vaadin Notification Docs](https://vaadin.com/components/vaadin-notification)

### Not Recommended
- **React/Vue/Angular Toast Libraries:** Not compatible with LitElement/web components.
- **Toastr.js, Notyf, etc.:** Not designed for web components, may require wrappers.

## Recommendation
For this feature, a custom LitElement-based toast is preferred for full control and minimal overhead. Shoelace is a good alternative if you want a prebuilt, accessible, and themeable solution.

## Next Steps
- Implement a custom `<mobile-toast>` LitElement component for the notification and progress bar.
- Integrate it into `MonsterBuilder.ts` to trigger on power edit events in mobile layout.
- Ensure accessibility and smooth user experience.
