// Replace the template-callout div on the /generate page with a temporary message
document.addEventListener("DOMContentLoaded", async function () {
    await loadStatblock();
});

// Add an event listener for any reroll button clicks
document.addEventListener("click", async (event) => {
    const button = event.target.closest(".reroll-button");
    if (!button) return;

    console.log("Reroll button clicked");

    // Trigger the animation
    button.classList.add("rolling");
    button.disabled = true;
    // Remove class after animation ends
    setTimeout(() => {
        button.classList.remove("rolling");
        button.disabled = false;
    }, 600); // match the animation duration

    await loadStatblock();
});

async function loadStatblock() {
    const params = new URLSearchParams(window.location.search);
    const template = params.get("template");
    const variant = params.get("variant");
    const container = document.getElementById("template-callout");

    if (!container) return;

    let url = '';
    if (template && variant) {
        url = `/api/v1/monsters/${variant}?output=monster_only`;
    }
    else {
        url = `/api/v1/monsters/random?output=monster_only`;
    }

    const res = await fetch(url);
    const html = await res.text();

    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    const newStatblockElement = doc.querySelector('.stat-block');

    container.innerHTML = '';
    container.appendChild(newStatblockElement);
}