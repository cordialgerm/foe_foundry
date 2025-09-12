// Homepage-specific functionality for Foe Foundry
// Includes Swiper carousels, lazy icons, and monster reroll functionality

// Import dependencies properly
import { Swiper } from 'swiper';
import { Navigation, Autoplay, Keyboard, Parallax } from 'swiper/modules';
import type { SwiperOptions } from 'swiper/types';
import 'swiper/css';
import 'swiper/css/navigation';
import 'swiper/css/autoplay';
import AnchorJS from 'anchor-js';

// Configure Swiper to use modules
Swiper.use([Navigation, Autoplay, Keyboard, Parallax]);

// Export to make this file a module
export { };

// Initialize AnchorJS
const anchors = new AnchorJS();

// Initialize homepage functionality when on the homepage
if (window.location.pathname === '/' || window.location.pathname === '/index.html') {
    console.log('Loaded homepage');
    // Use DOMContentLoaded to ensure the page is fully loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeHomepage);
    } else {
        // DOM is already loaded
        initializeHomepage();
    }
}

function initializeHomepage() {
    console.log('Initializing homepage functionality...');
    initSwipers();
    initBackgroundLogo();
    initLazyIcons();
    randomizeMasks();
}

interface SwiperBreakpoints {
    [key: number]: {
        slidesPerView: number;
        spaceBetween: number;
    };
}

interface SwiperConfig {
    id: string;
    breakpoints: SwiperBreakpoints;
}

function initSwipers() {
    const breakpoints: SwiperBreakpoints = {
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
    
    const breakpointsFew: SwiperBreakpoints = {
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
    
    const breakpointsFitMany: SwiperBreakpoints = {
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

    const swiperConfigs: SwiperConfig[] = [
        { id: 'monsters', breakpoints: breakpoints },
        { id: 'powers', breakpoints: breakpointsFew },
        { id: 'value-props', breakpoints: breakpointsFitMany },
        { id: 'blog', breakpoints: breakpointsFitMany }
    ];

    swiperConfigs.forEach(({ id, breakpoints }) => {
        const swiperContainer = document.querySelector(`.swiper-${id}`) as HTMLElement;
        
        if (!swiperContainer) {
            console.log(`Swiper container not found: .swiper-${id}`);
            return;
        }

        // Add some random noise to the delay (e.g., ±2000ms)
        const baseDelay = 6000;
        const delayNoise = Math.floor(Math.random() * 2000); // 0–1999ms
        const randomizedDelay = baseDelay + delayNoise;

        const swiper = new Swiper(swiperContainer, {
            modules: [Navigation, Autoplay, Keyboard, Parallax],
            autoplay: {
                delay: randomizedDelay,
                disableOnInteraction: true
            },
            breakpoints: breakpoints as any,
            initialSlide: 1,
            centeredSlides: true,
            grabCursor: true,
            keyboard: {
                enabled: true
            },
            navigation: {
                enabled: true
            },
            parallax: true,
            simulateTouch: true,
            on: {
                init: function (swiper) {
                    //remove preload class which is designed to help deal with layout shift
                    swiper.el.classList.remove('preload');
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
        const logoElement = document.getElementById("parallax-logo-bg");
        if (logoElement) {
            logoElement.classList.add("parallax-logo-bg");
        }
    };

    if (window.requestIdleCallback) {
        window.requestIdleCallback(setClass);
    } else {
        setTimeout(setClass, 200);
    }
}

function onSwiperClick(swiper: any, event: Event) {
    const clickedSlide = swiper.clickedSlide as HTMLElement;
    if (clickedSlide && clickedSlide.dataset.url) {
        const url = clickedSlide.dataset.url;
        // If this is the monster swiper, call trackMonsterClick
        if (swiper.el && swiper.el.classList.contains('swiper-monsters')) {
            // Try to extract the template key from the URL
            // Example URL: /monsters/{template_key}/
            const match = url.match(/\/monsters\/([^/]+)\//);
            if (match && typeof window.foeFoundryAnalytics?.trackMonsterClick === 'function') {
                const templateKey = match[1];
                window.foeFoundryAnalytics.trackMonsterClick(templateKey, 'template', 'carousel-legacy');
            }
        }
        window.location.href = url;
    }
}

function cleanAndInjectSVGFromURL(url: string, targetElement: HTMLElement, fillValue: string = 'currentColor') {
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
                const el = entry.target as HTMLElement;
                const url = el.dataset.iconUrl;

                if (url) {
                    cleanAndInjectSVGFromURL(url, el);
                    observer.unobserve(el); // Stop watching once loaded
                }
            }
        });
    }, {
        rootMargin: '1000px',   // Start loading 1000px before it enters the view
        threshold: 0.01         // Trigger when 1% of the element is visible
    });

    document.querySelectorAll('.lazy-icon-placeholder').forEach(el => observer.observe(el));
}

function randomizeMasks() {
    const variants = ['v1', 'v2', 'v3', 'v4', 'v5', 'v6'];

    document.querySelectorAll('.masked').forEach(el => {
        const element = el as HTMLElement;
        const hasVariant = variants.some(variant => element.classList.contains(variant));

        if (!hasVariant) {
            const random = variants[Math.floor(Math.random() * variants.length)];
            element.classList.add(random);
        }
    });
}

// Add an event listener for any reroll button clicks
document.addEventListener("click", async (event) => {
    const target = event.target as HTMLElement;
    const button = target.closest("#summon-your-first-monster .reroll-button") as HTMLButtonElement;
    if (!button) return;

    // Trigger the animation
    button.classList.add("rolling");
    button.disabled = true;
    // Remove class after animation ends
    setTimeout(() => {
        button.classList.remove("rolling");
        button.disabled = false;
    }, 600); // match the animation duration

    try {
        const url = `/api/v1/statblocks/random?output=monster_only`;
        const res = await fetch(url);
        const html = await res.text();

        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const newStatblockElement = doc.querySelector('.stat-block');

        // find #statblock-placeholder and replace its content with the new statblock
        const statblockPlaceholder = document.querySelector('#statblock-placeholder');
        if (statblockPlaceholder && newStatblockElement) {
            statblockPlaceholder.innerHTML = '';
            statblockPlaceholder.appendChild(newStatblockElement);
        }
    } catch (error) {
        console.error('Error rerolling monster:', error);
        // Re-enable button in case of error
        button.classList.remove("rolling");
        button.disabled = false;
    }
});