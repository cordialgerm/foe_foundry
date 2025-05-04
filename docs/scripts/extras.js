
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
          <p>The Monster Generator isn't live yet—but it's coming soon. When it launches, you'll be able to customize your own version of the <strong>${template}</strong>, complete with flavorful powers, thematic variants, and level scaling.</p>
          <p>Until then, check out the core <a style="font-size: 1.5rem;" href="/monsters/${template}#${variant}"><b>${monsterName}</b> statblock</a> to see what you're working with.</p>
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

  statblocks.forEach(statblock => {

    // tag the statblock with an id for tracking
    statblock.setAttribute('data-statblock-id', ++statblockId);

    // wrap the statblock in a parent div so we can position the button relative to it
    const wrapper = wrapStatblock(statblock);
    statblock.parentNode.insertBefore(wrapper, statblock);
    wrapper.appendChild(statblock);

    // create the reroll button
    const button = createRerollButton(statblock, wrapper);
    wrapper.appendChild(button);
  });
});

// Add an event listener for any reroll button clicks
document.addEventListener("click", (event) => {
  const button = event.target.closest(".reroll-button");
  if (!button) return;

  const wrapper = button.parentElement;
  if (!wrapper) return;

  const variantKey = button.dataset.monster;
  const statblock = wrapper.querySelector(".stat-block");
  console.log("Reroll button clicked:", variantKey, statblock);

  if (!variantKey || !statblock) return;

  rerollMonster(variantKey, statblock);
});


function wrapStatblock(statblock) {
  // Wrap statblock in a container to position the button relative to it
  const wrapper = document.createElement('div');
  wrapper.className = 'statblock-wrapper';
  wrapper.setAttribute('data-monster', statblock.dataset.monster);
  return wrapper;
}

function createRerollButton(statblock) {
  const button = document.createElement('button');
  button.className = 'reroll-button';
  button.setAttribute('aria-label', 'Reroll this monster');
  button.setAttribute('title', 'Reroll this monster');
  button.setAttribute('data-monster', statblock.dataset.monster);
  button.innerText = '🎲';
  return button;
}

function rerollMonster(variantKey) {

  const url = `/api/v1/monsters/${variantKey}?output=monster_only`;

  fetch(url)
    .then(res => res.text())
    .then(html => {
      // Parse the new statblock HTML into a DOM element
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, 'text/html');

      const newStatblockElement = doc.querySelector('.stat-block');
      newStatblockElement.setAttribute('data-statblock-id', ++statblockId);
      const oldStatblockElement = document.querySelector(`.stat-block[data-monster="${variantKey}"]`);
      console.log("Replacing old statblock:", oldStatblockElement, "with new statblock:", newStatblockElement);

      // Replace the old statblock in the wrapper
      oldStatblockElement.replaceWith(newStatblockElement);
    })
    .catch(err => console.error("Failed to reroll monster:", err));
}