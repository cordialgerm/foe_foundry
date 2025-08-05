// Add a dismissible Beta banner to the top of the page
document.addEventListener("DOMContentLoaded", function () {
  const banner = document.getElementById("beta-banner");
  const dismissBtn = document.getElementById("dismiss-banner");
  const params = new URLSearchParams(window.location.search);

  if (!banner || !dismissBtn) return;

  // Hide if user already dismissed it or in print mode
  if (localStorage.getItem("hideBetaBanner") === "true" || params.get('render') === 'print') {
    console.log("Beta banner previously dismissed by user.");
    banner.style.display = "none !important";
  }
  else {
    console.log("Displaying Beta banner.");
    banner.style.display = ""; // remove the previous style that was hiding the banner
  }

  dismissBtn.addEventListener("click", () => {
    console.log("Beta banner dismissed by user.");
    banner.style.display = "none !important";
    localStorage.setItem("hideBetaBanner", "true");
  });
});

let statblockId = 0;

// Wrap stat-blocks with monster-statblock component
document.addEventListener("DOMContentLoaded", () => {
  const statblocks = document.querySelectorAll('.stat-block');

  statblocks.forEach(statblock => {

    // Give the statblock a unique HTML ID if it doesn't have one
    if (!statblock.id) {
      statblock.id = `statblock-${++statblockId}`;
    }

    // Create the monster-statblock wrapper
    const wrapper = document.createElement('monster-statblock');
    wrapper.setAttribute('use-slot', '');

    // Insert the wrapper before the statblock
    statblock.parentNode.insertBefore(wrapper, statblock);

    // Move the statblock inside the wrapper as a slot
    wrapper.appendChild(statblock);
  });
});

// Randomize masks on page load
document.addEventListener("DOMContentLoaded", () => {
  randomizeMasks();
});

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