
// Replace the template-callout div on the /generate page with a temporary message
document.addEventListener("DOMContentLoaded", function () {
  const params = new URLSearchParams(window.location.search);
  const template = params.get("template");
  const variant = params.get("variant");
  const container = document.getElementById("template-callout");

  if (template && variant && container) {

    const monsterName = template.charAt(0).toUpperCase() + template.slice(1);

    container.innerHTML = `
        <div class="template-callout burnt-parchment p-5">
          <h2>Want to Summon a ${monsterName}?</h2>
          <p>The Monster Generator isn't live yet - but it's coming soon. When it launches, you'll be able to customize your own version of the <strong>${template}</strong>, complete with flavorful powers, thematic variants, and level scaling.</p>
          <p>Until then, check out the core <a style="font-size: 1.25rem;" href="/monsters/${template}/#${variant}"><b>${monsterName}</b> statblock</a> to see what you're working with.</p>
        </div>
      `;
  }
});

// Add a dismissible Alpha banner to the top of the page
document.addEventListener("DOMContentLoaded", function () {
  const banner = document.getElementById("alpha-banner");
  const dismissBtn = document.getElementById("dismiss-banner");

  if (!banner || !dismissBtn) return;

  // Hide if user already dismissed it
  if (localStorage.getItem("hideAlphaBanner") === "true") {
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

    // create the reroll button
    const button = await createRerollButton(statblock, wrapper);
    wrapper.appendChild(button);
  });
});

// Add an event listener for any reroll button clicks
document.addEventListener("click", (event) => {
  const button = event.target.closest(".reroll-button");
  if (!button) return;

  const wrapper = button.parentElement;
  if (!wrapper) return;

  const monsterKey = button.dataset.monster;
  const statblock = wrapper.querySelector(".stat-block");

  if (!monsterKey || !statblock) return;

  console.log("Reroll button clicked:", monsterKey, statblock);

  // Trigger the animation
  button.classList.add("rolling");
  button.disabled = true;
  // Remove class after animation ends
  setTimeout(() => {
    button.classList.remove("rolling");
    button.disabled = false;
  }, 600); // match the animation duration

  rerollMonster(monsterKey, statblock);
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

async function createRerollButton(statblock) {

  const button = document.createElement("button");
  button.classList.add("reroll-button");
  button.setAttribute("aria-label", "Reroll this monster");
  button.setAttribute("title", "Reroll this monster");
  button.setAttribute('data-monster', statblock.dataset.monster);

  const response = await fetch('/img/icons/d20.svg');
  const svgText = await response.text();

  const parser = new DOMParser();
  const svgDoc = parser.parseFromString(svgText, "image/svg+xml");
  const svgElement = svgDoc.documentElement;

  svgElement.classList.add("d20-icon");
  svgElement.removeAttribute("width");
  svgElement.removeAttribute("height");
  svgElement.removeAttribute("style");

  button.appendChild(svgElement);

  return button;
}

async function rerollMonster(monsterKey) {
  const url = `/api/v1/monsters/${monsterKey}?output=monster_only`;

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