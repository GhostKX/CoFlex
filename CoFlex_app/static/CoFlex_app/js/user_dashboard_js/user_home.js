document.addEventListener('DOMContentLoaded', function () {
    const mobileMenuToggle = document.createElement('button');
    mobileMenuToggle.innerHTML = '<span class="material-icons">menu</span>';
    mobileMenuToggle.classList.add('mobile-menu-toggle');

    function checkMobileView() {
        const navbar = document.querySelector('.navbar');
        const navButtons = document.querySelector('.nav-buttons');

        if (window.innerWidth <= 768) {
            if (!document.querySelector('.mobile-menu-toggle')) {
                navbar.prepend(mobileMenuToggle);

                mobileMenuToggle.addEventListener('click', () => {
                    navButtons.classList.toggle('mobile-open');
                    mobileMenuToggle.classList.toggle('active');
                });
            }
        } else {
            const existingToggle = document.querySelector('.mobile-menu-toggle');
            if (existingToggle) {
                existingToggle.remove();
                navButtons.classList.remove('mobile-open');
            }
        }
    }

    const carousel = document.querySelector('.subscription-carousel');
    const prevButton = document.querySelector('.carousel-button.left');
    const nextButton = document.querySelector('.carousel-button.right');
    const cards = Array.from(carousel.querySelectorAll('.subscription-card'));

    let currentIndex = 0;
    let isAnimating = false;
    const cardsToShow = 3;

    // Cloning cards for infinite loop
    const clonedCards = cards.map(card => card.cloneNode(true));
    carousel.append(...clonedCards);

    function updateCarousel() {
        if (isAnimating) return;
        isAnimating = true;

        const cardWidth = cards[0].offsetWidth;
        const gap = parseInt(window.getComputedStyle(carousel).gap);
        const offset = -(currentIndex * (cardWidth + gap));

        carousel.style.transition = 'transform 0.6s ease-in-out';
        carousel.style.transform = `translateX(${offset}px)`;

        if (currentIndex >= cards.length) {
            setTimeout(() => {
                carousel.style.transition = 'none';
                carousel.style.transform = `translateX(0)`;
                currentIndex = 0;
            }, 600);
        } else if (currentIndex < 0) {
            setTimeout(() => {
                carousel.style.transition = 'none';
                currentIndex = cards.length - 1;
                const lastOffset = -(cards.length - 1) * (cardWidth + gap);
                carousel.style.transform = `translateX(${lastOffset}px)`;
            }, 600);
        }

        highlightCenterCard();

        setTimeout(() => {
            isAnimating = false;
        }, 600);
    }

    function highlightCenterCard() {
        cards.forEach(card => card.classList.remove('center-card'));
        const centerCardIndex = (currentIndex + Math.floor(cardsToShow / 2)) % cards.length;
        cards[centerCardIndex].classList.add('center-card');
    }

    nextButton.addEventListener('click', () => {
        if (!isAnimating) {
            currentIndex++;
            updateCarousel();
        }
    });

    prevButton.addEventListener('click', () => {
        if (!isAnimating) {
            currentIndex--;
            updateCarousel();
        }
    });

    function handleResponsiveCarousel() {
        const cardWidth = cards[0].offsetWidth;
        const gap = parseInt(window.getComputedStyle(carousel).gap);
        const offset = -(currentIndex * (cardWidth + gap));
        carousel.style.transform = `translateX(${offset}px)`;
    }

    checkMobileView();
    window.addEventListener('resize', checkMobileView);
    window.addEventListener('resize', handleResponsiveCarousel);

    updateCarousel();
    initializeMessages();
});