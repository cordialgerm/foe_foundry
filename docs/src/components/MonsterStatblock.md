# PRD - Refactor Monster Statblocks

## Problem

- MonsterStatblock currently does not encapsulate all of the logic related to the monster statblock, which is spread around in different components for historical reasons:
  - RerollButton currently contains a lot of logic related to forcing a statblock to to re-render
  - MonsterBuilder currently contains a lot of logic related to trying to maintain the current size of a statblock while re-rendering it
- MonsterStatblock currently doesn't use lit best design practices, because it directly modifies the DOM to place the dynamic content loaded from the API. This needs to change to use a `ref` in the render template
- This makes it difficult to reason about and re-use monster statblocks
- MonsterStatblock has no way of being customized in terms of the HP, Damage, or selected powers

## Proposals

- Refactor `MonsterStatblock` so that it uses lit best practices and renders itself with a `ref` in the render template
- Add additional properties to `MonsterStatblock`
  - `hpMultiplier`: number
  - `damageMultiplier`: number
  - `powers`: a csv of power keys that will be used when loading the monster
- Enhance `MonsterStatblock` so that it has a `reroll()` method that performs three tasks
  - allows for bulk updates of `monsterKey`, `hpMultiplier`, `damageMultiplier`, and `powers` with an optional `changeType` to pass through to the `MonsterStore`
  - animates the statblock with the `pop-out` and `pop-in` animations that are currently spread out across various different files
  - preserves the current height of the statblock before rendering by fixing the height of the container that will hold the new statblock during the loading process so that it doesn't flicker, and then animating to the new height smoothly

## Implementation Plan

### Phase 1: Refactor MonsterStatblock Core (Foundational Changes)

1. **Update MonsterStatblock Properties**
   - Add `hpMultiplier?: number` property (default: 1)
   - Add `damageMultiplier?: number` property (default: 1) 
   - Add `powers?: string` property for CSV of power keys (default: '')
   - Add `changeType?: StatblockChangeType` property for animation hints

2. **Refactor Rendering to Use Lit Best Practices**
   - Replace current `renderStatblock()` DOM manipulation with `ref` directive
   - Create a `statblockRef` using `createRef<HTMLDivElement>()`
   - Update render method to use `${ref(this.statblockRef)}` in template
   - Move statblock content insertion to use the ref instead of `getElementById`

3. **Consolidate Animation Styles**
   - Extract animation CSS from `RerollButton.ts` global styles injection
   - Move `pop-out`, `pop-in`, `summon-flash`, `scale-throb`, and `summon-fade` animations into MonsterStatblock's static styles

### Phase 2: Add Height Preservation Logic

4. **Implement Height Preservation System**
   - Add private `lastKnownHeight: number` property
   - Add `captureCurrentHeight()` method similar to MonsterBuilder
   - Add `preserveHeightDuringTransition()` method that:
     - Captures current height before changes
     - Sets explicit height on container
     - Returns cleanup function for smooth height transition
     - Uses `requestAnimationFrame` for smooth animation to natural height

### Phase 3: Create Unified Reroll Method

5. **Implement `reroll()` Method**
   ```typescript
   async reroll(updates: {
     monsterKey?: string;
     hpMultiplier?: number;
     damageMultiplier?: number;
     powers?: string;
     changeType?: StatblockChangeType;
   }): Promise<void>
   ```
   - Accept partial updates object for bulk property changes
   - Trigger height preservation before making changes
   - Update internal properties
   - Trigger `pop-out` animation
   - Reload statblock with new parameters
   - Trigger `pop-in` and `summon-effect` animations
   - Clean up height transition

6. **Update Task Logic**
   - Modify `_statblockTask` to use all properties (`hpMultiplier`, `damageMultiplier`, `powers`)
   - Parse `powers` CSV string into Power array for StatblockRequest
   - Pass `changeType` to `getStatblock` as StatblockChange

### Phase 4: Integration Changes

7. **Update MonsterBuilder Integration**
   - Replace direct `loadStatblock()` calls with `MonsterStatblock.reroll()`
   - Remove height preservation logic from MonsterBuilder (move to MonsterStatblock)
   - Update event handlers to call `reroll()` with appropriate parameters
   - Remove `#statblock-holder` direct DOM manipulation

8. **Update RerollButton Integration**
   - Remove direct statblock manipulation from `_rerollStatblock()`
   - Find parent MonsterStatblock component instead of raw statblock element
   - Call `monsterStatblock.reroll({ changeType: StatblockChangeType.Rerolled })`
   - Simplify RerollButton to just trigger the reroll, not manage animations

9. **Create Migration Path**
   - Ensure backwards compatibility during transition
   - Add fallback behavior for existing statblock elements

### Phase 4: Supporting Wrapping Light DOM Statblock

There are currently a variety of markdown helpers, like [[!ogre]] that render the inner HTML of a statblock directly into the page. Eventually, we need to come up with a plan for how we can wrap or manage this content with the MonsterStatblock, but DO NOT WORRY ABOUT THAT FOR NOW.


### Success Criteria

- [ ] MonsterStatblock encapsulates all statblock-related logic
- [ ] Uses Lit `ref` instead of direct DOM manipulation  
- [ ] Smooth height transitions with no flickering
- [ ] Unified animation system (pop-out/pop-in/summon effects)
- [ ] Bulk property updates via single `reroll()` method
- [ ] Clean separation of concerns between components