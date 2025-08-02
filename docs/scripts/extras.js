// Add a dismissible Alpha banner to the top of the page
document.addEventListener("DOMContentLoaded", function () {
  const banner = document.getElementById("alpha-banner");
  const dismissBtn = document.getElementById("dismiss-banner");
  const params = new URLSearchParams(window.location.search);

  if (!banner || !dismissBtn) return;

  // Hide if user already dismissed it or in print mode
  if (localStorage.getItem("hideAlphaBanner") === "true" || params.get('render') === 'print') {
    console.log("Alpha banner previously dismissed by user.");
    banner.style.display = "none";
  }

  dismissBtn.addEventListener("click", () => {
    console.log("Alpha banner dismissed by user.");
    banner.style.display = "none";
    localStorage.setItem("hideAlphaBanner", "true");
  });
});

let statblockId = 0;

// Add a Re-Roll button to statblocks
document.addEventListener("DOMContentLoaded", () => {
  const statblocks = document.querySelectorAll('.stat-block');

  statblocks.forEach(async statblock => {

    // tag the statblock with an id for tracking
    statblock.setAttribute('data-statblock-id', ++statblockId);

    // wrap the statblock in a parent div so we can position the button relative to it
    const wrapper = wrapStatblock(statblock);
    statblock.parentNode.insertBefore(wrapper, statblock);
    wrapper.appendChild(statblock);

    // create the reroll button using the new component
    const button = createRerollButton(statblock);
    wrapper.appendChild(button);
  });
});

// Add an event listener for reroll events from the reroll-button component
document.addEventListener("reroll", (event) => {
  const { monsterKey } = event.detail;

  if (!monsterKey) return;

  console.log("Reroll event received:", monsterKey);

  rerollMonster(monsterKey);
});

// Randomize masks on page load
document.addEventListener("DOMContentLoaded", () => {
  randomizeMasks();
});


function wrapStatblock(statblock) {
  // Wrap statblock in a container to position the button relative to it
  const wrapper = document.createElement('div');
  wrapper.className = 'statblock-wrapper';
  wrapper.setAttribute('data-monster', statblock.dataset.monster);
  return wrapper;
}

function createRerollButton(statblock) {
  const button = document.createElement('reroll-button');
  button.setAttribute('monster-key', statblock.dataset.monster);
  return button;
}

async function rerollMonster(monsterKey) {
  const url = `/api/v1/statblocks/${monsterKey}?output=monster_only`;

  const oldStatblockElement = document.querySelector(`.stat-block[data-monster="${monsterKey}"]`);
  oldStatblockElement.classList.add("pop-out");

  try {
    const res = await fetch(url);
    const html = await res.text();

    // Parse the new statblock HTML into a DOM element
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    const newStatblockElement = doc.querySelector('.stat-block');
    newStatblockElement.setAttribute('data-statblock-id', ++statblockId);

    // Replace old with new
    oldStatblockElement.replaceWith(newStatblockElement);
    newStatblockElement.classList.add("pop-in");

    // Wait for pop-in animation, then trigger summon effect
    await sleep(200);
    newStatblockElement.classList.remove("pop-in");

    // wait a little bit before starting summon effect
    await sleep(200);
    newStatblockElement.classList.add("summon-effect");

    // Remove summon-effect after it's done
    await sleep(400);
    newStatblockElement.classList.remove("summon-effect");

  } catch (err) {
    console.error("Failed to reroll monster:", err);
  }
}

function randomizeMasks() {
  const variants = ['v1', 'v2', 'v3', 'v4', 'v5', 'v6'];

  document.querySelectorAll('.masked').forEach(el => {
    const hasVariant = variants.some(variant => el.classList.contains(variant));

    if (!hasVariant) {
      const random = variants[Math.floor(Math.random() * variants.length)];
      el.classList.add(random);
    }
  });
}


function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}


// AnchorJS setup for linking to headings
document.addEventListener("DOMContentLoaded", () => {
  // Initialize anchor.js for linking to headings
  const anchors = new window.AnchorJS();
  anchors.options = {
    placement: 'right',
    class: 'anchor-link',
  };
  anchors.add('h1, h2, h3');
});