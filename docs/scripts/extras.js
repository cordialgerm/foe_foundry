
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
          <p>Until then, check out the core <a style="font-size: 1.25rem;" href="/monsters/${template}#${variant}"><b>${monsterName}</b> statblock</a> to see what you're working with.</p>
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