# Toast Notification Library Assessment for LitElement

## Criteria
- **Compatibility:** Must work with LitElement and web components.
- **Lightweight:** Minimal impact on bundle size.
- **Customizable:** Easy to style and control behavior.
- **Accessible:** Good support for keyboard and screen readers.

## Library Options

### 1. Custom LitElement Component
- **Pros:**
  - Full control over appearance and logic.
  - No external dependencies.
  - Easily integrates with existing LitElement code.
- **Cons:**
  - Requires manual implementation of accessibility and animation.
- **Best For:** Projects already using LitElement and needing a simple, custom toast.

### 2. Shoelace (`sl-toast`)
- **Pros:**
  - Web component-based, works natively with LitElement.
  - Accessible, themeable, and well-documented.
  - Modular: only import what you need.
- **Cons:**
  - Adds some bundle size.
- **Best For:** Projects wanting a prebuilt, accessible, and customizable solution.

### 3. Vaadin Notification
- **Pros:**
  - Web component-based, compatible with LitElement.
  - Good accessibility and features.
- **Cons:**
  - Heavier than Shoelace.
- **Best For:** Enterprise projects or those already using Vaadin.

### Not Recommended
- React/Vue/Angular toast libraries (not compatible with LitElement).
- Toastr.js, Notyf, etc. (not web component-based).

## Recommendation
For foe_foundry, a custom LitElement toast component is recommended for this feature. Shoelace is a good alternative if you prefer a prebuilt solution.
