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

  statblocks.forEach(statblock => {

    // Give the statblock a unique HTML ID if it doesn't have one
    if (!statblock.id) {
      statblock.id = `statblock-${++statblockId}`;
    }

    const rerollButton = createRerollButton(statblock);
    statblock.parentNode.insertBefore(rerollButton, statblock.nextSibling);

    const editButton = createEditButton(statblock);
    statblock.parentNode.insertBefore(editButton, statblock.nextSibling);
  });
});

// Randomize masks on page load
document.addEventListener("DOMContentLoaded", () => {
  randomizeMasks();
});


function createRerollButton(statblock) {
  const button = document.createElement('reroll-button');
  button.setAttribute('target', statblock.id);
  return button;
}

function createEditButton(statblock) {
  const button = document.createElement('edit-button');
  button.setAttribute('target', statblock.id);
  return button;
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