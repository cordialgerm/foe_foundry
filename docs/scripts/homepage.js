document.addEventListener('DOMContentLoaded', function () {
    initSwipers();
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
        });

        swiper.autoplay.stop();
        setTimeout(() => swiper.autoplay.start(), 8000 + Math.random() * 3000); // Start autoplay after 6–9s
    });
}
