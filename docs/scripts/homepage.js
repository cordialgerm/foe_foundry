document.addEventListener('DOMContentLoaded', function () {
    initSwipers();
    initBackgroundLogo();
    initLazyIcons();
    randomizeMasks();
});


function initSwipers() {
    const breakpoints = {
        320: {
            slidesPerView: 1,
            spaceBetween: 16
        },
        576: {
            slidesPerView: 2,
            spaceBetween: 16
        },
        768: {
            slidesPerView: 3,
            spaceBetween: 16
        },
        1200: {
            slidesPerView: 3,
            spaceBetween: 32
        },
        1400: {
            slidesPerView: 3,
            spaceBetween: 48
        },
    };
    const breakpointsFew = {
        320: {
            slidesPerView: 1,
            spaceBetween: 16
        },
        480: {
            slidesPerView: 1,
            spaceBetween: 32,
        },
        576: {
            slidesPerView: 2,
            spaceBetween: 16
        },
        768: {
            slidesPerView: 2,
            spaceBetween: 32
        },
        1200: {
            slidesPerView: 3,
            spaceBetween: 32
        },
        1400: {
            slidesPerView: 3,
            spaceBetween: 48
        },
    };
    const breakpointsFitMany = {
        200: {
            slidesPerView: 1,
            spaceBetween: 8
        },
        320: {
            slidesPerView: 2,
            spaceBetween: 8
        },
        576: {
            slidesPerView: 2,
            spaceBetween: 16
        },
        768: {
            slidesPerView: 3,
            spaceBetween: 16
        },
        1200: {
            slidesPerView: 4,
            spaceBetween: 16
        },
        1400: {
            slidesPerView: 4,
            spaceBetween: 32
        },
    };

    [
        { id: 'monsters', breakpoints: breakpoints },
        { id: 'powers', breakpoints: breakpointsFew },
        { id: 'value-props', breakpoints: breakpointsFitMany },
        { id: 'blog', breakpoints: breakpointsFitMany }
    ].forEach(({ id, breakpoints }) => {

        const swiperContainer = document.querySelector(`.swiper-${id}`);

        // Add some random noise to the delay (e.g., ±2000ms)
        const baseDelay = 6000;
        const delayNoise = Math.floor(Math.random() * 2000); // 0–1999ms
        const randomizedDelay = baseDelay + delayNoise;

        const swiper = new Swiper(swiperContainer, {
            autoplay: {
                delay: randomizedDelay,
                disableOnInteraction: true
            },
            breakpoints: breakpoints,
            initialSlide: 1,
            centeredSlides: true,
            createElements: true,
            grabCursor: true,
            keyboard: true,
            navigation: true,
            parallax: true,
            simulateTouch: true,
            on: {
                init: function () {
                    //remove preload class which is designed to help deal with layout shift
                    this.el.classList.remove('preload');
                }
            }
        });

        swiper.autoplay.stop();
        setTimeout(() => swiper.autoplay.start(), 8000 + Math.random() * 3000); // Start autoplay after 6–9s

        swiper.on('click', onSwiperClick);
        swiper.on('tap', onSwiperClick);
    });
}

function initBackgroundLogo() {

    const setClass = () => {
        document.getElementById("parallax-logo-bg")?.classList.add("parallax-logo-bg");
    };

    requestIdleCallback?.(setClass) || setTimeout(setClass, 200);
}

window.addEventListener("load", () => {

});

function onSwiperClick(swiper, event) {
    const clickedSlide = swiper.clickedSlide;
    if (clickedSlide && clickedSlide.dataset.url) {
        window.location.href = clickedSlide.dataset.url;
    }
}


function cleanAndInjectSVGFromURL(url, targetElement, fillValue = 'currentColor') {
    fetch(url)
        .then(res => res.text()) // get the raw SVG text
        .then(svgText => {
            // Strip out any fill="..." attributes
            const cleaned = svgText.replace(/\s*fill=(['"])[^'"]*\1/g, '');

            // Convert SVG string into a DOM element
            const parser = new DOMParser();
            const doc = parser.parseFromString(cleaned, 'image/svg+xml');
            const svgEl = doc.documentElement;

            // Optionally apply a uniform fill
            if (fillValue !== null) {
                svgEl.setAttribute('fill', fillValue);
            }

            // Replace the contents of the target <div>
            targetElement.innerHTML = '';
            targetElement.appendChild(svgEl);
            targetElement.classList.remove('lazy-icon-placeholder');
        })
        .catch(err => {
            console.warn('Error loading SVG icon:', url, err);
        });
}

function initLazyIcons() {
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const el = entry.target;
                const url = el.dataset.iconUrl;

                if (url) {
                    cleanAndInjectSVGFromURL(url, el);
                    observer.unobserve(el); // Stop watching once loaded
                }
            }
        });
    }, {
        rootMargin: '1000px',   // Start loading 200px before it enters the view
        threshold: 0.01         // Trigger when 10% of the element is visible
    });

    document.querySelectorAll('.lazy-icon-placeholder').forEach(el => observer.observe(el));
}

// Add an event listener for any reroll button clicks
document.addEventListener("click", async (event) => {
    const button = event.target.closest("#summon-your-first-monster .reroll-button");
    if (!button) return;

    // Trigger the animation
    button.classList.add("rolling");
    button.disabled = true;
    // Remove class after animation ends
    setTimeout(() => {
        button.classList.remove("rolling");
        button.disabled = false;
    }, 600); // match the animation duration

    const url = `/api/v1/monsters/random?output=monster_only`;
    const res = await fetch(url);
    const html = await res.text();

    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    const newStatblockElement = doc.querySelector('.stat-block');

    // find #statblock-placeholder and replace its content with the new statblock
    const statblockPlaceholder = document.querySelector('#statblock-placeholder');
    if (statblockPlaceholder) {
        statblockPlaceholder.innerHTML = '';
        statblockPlaceholder.appendChild(newStatblockElement);
    }
});