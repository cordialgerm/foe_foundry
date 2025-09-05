---
title: Monster Codex | Foe Foundry
description: Browse and discover all Foe Foundry monsters with rich filtering and search capabilities. Find the perfect monster for your next D&D 5E session.
image: img/icons/favicon.webp
hidden:
- backlinks
date: '2025-01-20T00:00:00-07:00'
---

# Monster Codex

<monster-codex></monster-codex>

<script type="module">
import { initializeMonsterStore } from '../src/data/api.js';

// Initialize the monster store and pass it to the component
const monsterStore = initializeMonsterStore();
const codexElement = document.querySelector('monster-codex');
if (codexElement) {
    codexElement.monsterStore = monsterStore;
}
</script>