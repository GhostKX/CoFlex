document.addEventListener('DOMContentLoaded', function() {
    // Getting DOM elements
    const startDateInput = document.getElementById('id_start_date');
    const startTimeInput = document.getElementById('id_start_time');
    const endTimeInput = document.getElementById('id_end_time');
    const bookingForm = document.querySelector('.booking-form');
    const endDateInput = document.getElementById('id_end_date');

    // Setting minimum date to today for the date picker
    const today = new Date();
    const todayFormatted = new Intl.DateTimeFormat('en-CA', {
        timeZone: 'Asia/Tashkent',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    }).format(today).replace(/\//g, '-');

    if (startDateInput) {
        startDateInput.min = todayFormatted;
        startDateInput.value = startDateInput.value || todayFormatted;
    }

    if (startTimeInput && !startTimeInput.value) {
        startTimeInput.value = '09:00';
    }

    if (endTimeInput && !endTimeInput.value) {
        endTimeInput.value = '12:00';
    }

    if (bookingForm && endDateInput) {
        bookingForm.addEventListener('submit', function() {
            if (startDateInput && startDateInput.value) {
                endDateInput.value = startDateInput.value;
            }
        });
    }

    const messages = document.querySelectorAll('.message');
    if (messages.length > 0) {
        setTimeout(function() {
            messages.forEach(function(message) {
                message.style.opacity = '0';
                message.style.transition = 'opacity 0.5s ease';
                setTimeout(function() {
                    message.style.display = 'none';
                }, 500);
            });
        }, 5000);
    }
});