document.addEventListener('DOMContentLoaded', function() {
    const timerDisplay = document.querySelector('#resend-timer span');
    const timerElement = document.getElementById('resend-timer');
    const resendForm = document.getElementById('resend-form');
    let timeLeft = 59;

    const countdown = setInterval(() => {
        timeLeft--;
        timerDisplay.textContent = timeLeft;

        if (timeLeft <= 0) {
            clearInterval(countdown);
            timerElement.style.display = 'none';
            resendForm.style.display = 'block';
        }
    }, 1000);

    window.confirmCancel = function(user_id) {
        console.log("confirmCancel triggered with user_id:", user_id);
        const userConfirmed = confirm("Are you sure you want to cancel the registration process? This will delete your account.");
        if (userConfirmed) {
            window.location.href = "/cancel_verification/" + user_id;
        }
    }
});