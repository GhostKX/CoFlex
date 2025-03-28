document.addEventListener('DOMContentLoaded', function() {
            const messages = document.querySelector('.messages');
            if (messages) {
                setTimeout(() => {
                    messages.style.transition = 'opacity 1s ease';
                    messages.style.opacity = '0';
                    setTimeout(() => messages.remove(), 500);
                }, 3000);
            }
});