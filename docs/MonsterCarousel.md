# Monster Carousel Component Usage

The `<monster-carousel>` component provides a reusable, swipeable carousel for displaying monsters with different filtering options.

## Basic Usage

```html
<!-- Show newest monsters -->
<monster-carousel filter="new"></monster-carousel>

<!-- Show monsters from a specific family -->
<monster-carousel filter="family:criminals"></monster-carousel>

<!-- Show search results -->
<monster-carousel filter="query:dragon"></monster-carousel>
```

## Available Filter Types

### New Monsters
```html
<monster-carousel filter="new"></monster-carousel>
```
Displays the most recently added monsters.

### Family Filters
```html
<monster-carousel filter="family:criminals"></monster-carousel>
<monster-carousel filter="family:undead"></monster-carousel>
<monster-carousel filter="family:monstrosities"></monster-carousel>
<monster-carousel filter="family:giants"></monster-carousel>
<monster-carousel filter="family:orcs_and_goblinoids"></monster-carousel>
```
Displays monsters from specific families defined in `/docs/families/`.

### Search Filters  
```html
<monster-carousel filter="query:dragon"></monster-carousel>
<monster-carousel filter="query:undead"></monster-carousel>
<monster-carousel filter="query:CR 5"></monster-carousel>
```
Uses the search API to find monsters matching the query.

## Features

- Swipeable with touch/mouse support
- Responsive design for all screen sizes  
- Auto-play functionality
- Keyboard navigation (arrow keys)
- Click to navigate to monster pages
- Loading and error states
- Matches homepage carousel styling

## Example Integration

```html
<section>
  <h2>Latest Monsters</h2>
  <monster-carousel filter="new"></monster-carousel>
</section>

<section>  
  <h2>Criminal Underworld</h2>
  <monster-carousel filter="family:criminals"></monster-carousel>
</section>
```

The component automatically handles data fetching, rendering, and user interactions.