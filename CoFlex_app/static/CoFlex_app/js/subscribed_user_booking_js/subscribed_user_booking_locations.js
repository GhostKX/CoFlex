document.addEventListener('DOMContentLoaded', () => {
    const slides = document.querySelectorAll('.slide');
    const container = document.querySelector('.background-container');
    const dotsContainer = document.querySelector('.navigation-dots');
    const imageFrames = document.querySelectorAll('.image-frame');
    const logoFrames = document.querySelectorAll('.logo-frame');

    let currentIndex = 0;
    const totalSlides = slides.length;
    let isHovered = false;
    let slideInterval;
    let transitionTimeout;

    // Creating navigation dots
    slides.forEach((_, index) => {
        const dot = document.createElement('div');
        dot.classList.add('dot');
        if (index === 0) dot.classList.add('active');
        dot.addEventListener('click', () => {
            if (!isHovered) {
                goToSlide(index);
            }
        });
        dotsContainer.appendChild(dot);
    });

    const dots = document.querySelectorAll('.dot');

    // Adding hover effect handlers
    logoFrames.forEach(frame => {
        frame.addEventListener('mouseenter', () => {
            clearTimeout(transitionTimeout);
            isHovered = true;
            stopSlideshow();
            const parentSlide = frame.closest('.slide');
            parentSlide.setAttribute('data-logo-hovered', 'true');
        });

        frame.addEventListener('mouseleave', () => {
            const parentSlide = frame.closest('.slide');
            parentSlide.removeAttribute('data-logo-hovered');

            transitionTimeout = setTimeout(() => {
                isHovered = false;
                startSlideshow();
            }, 1000);
        });
    });

    function goToSlide(index) {
        slides.forEach(slide => slide.classList.remove('active'));
        dots.forEach(dot => dot.classList.remove('active'));

        slides[index].classList.add('active');
        dots[index].classList.add('active');

        currentIndex = index;
    }

    function nextSlide() {
        if (!isHovered) {
            const nextIndex = (currentIndex + 1) % totalSlides;
            goToSlide(nextIndex);
        }
    }

    function startSlideshow() {
        if (!isHovered) {
            slideInterval = setInterval(nextSlide, 2500);
        }
    }

    function stopSlideshow() {
        clearInterval(slideInterval);
    }

    imageFrames.forEach(frame => {
        frame.addEventListener('mouseenter', () => {
            clearTimeout(transitionTimeout);
            isHovered = true;
            stopSlideshow();
        });

        frame.addEventListener('mouseleave', () => {
            transitionTimeout = setTimeout(() => {
                isHovered = false;
                startSlideshow();
            }, 1000);
        });
    });

    let touchStartX = 0;
    let touchEndX = 0;
    let touchStartY = 0;
    let touchEndY = 0;

    container.addEventListener('touchstart', (e) => {
        clearTimeout(transitionTimeout);
        touchStartX = e.changedTouches[0].screenX;
        touchStartY = e.changedTouches[0].screenY;
        stopSlideshow();
    });

    container.addEventListener('touchend', (e) => {
        touchEndX = e.changedTouches[0].screenX;
        touchEndY = e.changedTouches[0].screenY;
        handleSwipe();

        transitionTimeout = setTimeout(() => {
            startSlideshow();
        }, 1000);
    });

    function handleSwipe() {
        const swipeThreshold = 50;
        const differenceX = touchStartX - touchEndX;
        const differenceY = Math.abs(touchStartY - touchEndY);

        if (Math.abs(differenceX) > swipeThreshold && differenceY < 100) {
            if (differenceX > 0) {
                goToSlide((currentIndex + 1) % totalSlides);
            } else {
                goToSlide((currentIndex - 1 + totalSlides) % totalSlides);
            }
        }
    }

    startSlideshow();
});