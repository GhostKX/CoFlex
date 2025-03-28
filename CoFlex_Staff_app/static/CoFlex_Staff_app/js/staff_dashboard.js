document.addEventListener('DOMContentLoaded', function() {
    // Core DOM Elements
    const photoInput = document.getElementById('profile_photo');
    const photoEditBtn = document.querySelector('.photo-edit-btn');
    const dateInput = document.getElementById('selected_date');
    const bookIdFilter = document.getElementById('book-id-filter');
    const firstNameFilter = document.getElementById('first-name-filter');
    const lastNameFilter = document.getElementById('last-name-filter');
    const checkinFilter = document.getElementById('checkin-filter');
    const checkoutFilter = document.getElementById('checkout-filter');
    const requestsFilter = document.getElementById('requests-filter');
    const statusFilter = document.getElementById('status-filter');

    // Day Navigation Elements
    const dayButtons = document.querySelectorAll('.day-btn');
    const daysContainer = document.querySelector('.days-scroll-container');
    const bookingsTable = document.querySelector('.bookings-table tbody');

    // Get CSRF token
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    initProfilePhoto();
    initFilters();
    initMessages();
    initDayNavigation();

    // Profile Photo Upload
    function initProfilePhoto() {
        if (photoEditBtn && photoInput) {
            photoEditBtn.addEventListener('click', function() {
                photoInput.click();
            });

            photoInput.addEventListener('change', function() {
                if (this.files && this.files[0]) {
                    this.closest('form').submit();
                }
            });
        }
    }

    // Initialize Filters
    function initFilters() {
        const filters = [
            bookIdFilter,
            firstNameFilter,
            lastNameFilter,
            checkinFilter,
            checkoutFilter,
            requestsFilter,
            statusFilter
        ];

        filters.forEach(filter => {
            if (filter) {
                if (filter.tagName === 'SELECT') {
                    filter.addEventListener('change', function() {
                        // Get the current active date
                        const activeDay = document.querySelector('.day-btn.active');
                        const date = activeDay ? activeDay.dataset.date : dateInput.value;
                        loadDayBookings(date);
                    });
                } else {
                    // Use debounce to prevent too many requests
                    let timeout;
                    filter.addEventListener('input', function() {
                        clearTimeout(timeout);
                        timeout = setTimeout(() => {
                            const activeDay = document.querySelector('.day-btn.active');
                            const date = activeDay ? activeDay.dataset.date : dateInput.value;
                            loadDayBookings(date);
                        }, 300);
                    });
                }
            }
        });
    }

    function filterBookings() {
        const bookIdValue = bookIdFilter ? bookIdFilter.value.toLowerCase() : '';
        const firstNameValue = firstNameFilter ? firstNameFilter.value.toLowerCase() : '';
        const lastNameValue = lastNameFilter ? lastNameFilter.value.toLowerCase() : '';
        const checkinValue = checkinFilter ? checkinFilter.value.toLowerCase() : '';
        const checkoutValue = checkoutFilter ? checkoutFilter.value.toLowerCase() : '';
        const requestsValue = requestsFilter ? requestsFilter.value.toLowerCase() : '';
        const statusValue = statusFilter ? statusFilter.value.toLowerCase() : 'all';

        const rows = document.querySelectorAll('.bookings-table tbody tr');

        rows.forEach(row => {
            if (row.classList.contains('no-bookings-row') || row.querySelector('.no-bookings')) return;

        // Making the row clickable
        row.style.cursor = 'pointer';

        // Extracting booking ID from the first cell
        const bookingId = row.cells[0].textContent.trim();

        // Getting staff_id and location_code from the URL
        const urlParts = window.location.pathname.split('/');
        const staffIdIndex = urlParts.indexOf('staff_dashboard') + 1;
        const staffId = urlParts[staffIdIndex];
        const locationCode = urlParts[staffIdIndex + 1];

        // Adding click event to the row
        row.addEventListener('click', function() {
            window.location.href = `${bookingId}/booking_details_view/`;
        });

            const bookId = row.cells[0].textContent.toLowerCase();
            const firstName = row.cells[1].textContent.toLowerCase();
            const lastName = row.cells[2].textContent.toLowerCase();
            const checkin = row.cells[3].textContent.toLowerCase();
            const checkout = row.cells[4].textContent.toLowerCase();
            const requests = row.cells[5].textContent.toLowerCase();

            // Getting the status text from the status badge
            const statusBadge = row.cells[6].querySelector('.status-badge');
            const status = statusBadge ? statusBadge.textContent.trim().toLowerCase() : '';

            const matchesBookId = bookId.includes(bookIdValue);
            const matchesFirstName = firstName.includes(firstNameValue);
            const matchesLastName = lastName.includes(lastNameValue);
            const matchesCheckin = checkin.includes(checkinValue);
            const matchesCheckout = checkout.includes(checkoutValue);
            const matchesRequests = requests.includes(requestsValue);
            const matchesStatus = statusValue === 'all' || status.includes(statusValue);

            if (matchesBookId && matchesFirstName && matchesLastName &&
                matchesCheckin && matchesCheckout && matchesRequests && matchesStatus) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }

    function initDayNavigation() {
        if (dayButtons.length > 0) {
            const activeBtn = document.querySelector('.day-btn.active');
            if (activeBtn) {
                scrollToActiveDay(activeBtn);
            }

            // Day Button Click Event - Now separate from date input
            dayButtons.forEach(btn => {
                btn.addEventListener('click', function() {
                    const date = this.dataset.date;
                    loadDayBookings(date);

                    // Update active state
                    dayButtons.forEach(b => b.classList.remove('active'));
                    this.classList.add('active');
                });
            });
        }
    }

    function scrollToActiveDay(activeBtn) {
        if (daysContainer && activeBtn) {
            const containerWidth = daysContainer.offsetWidth;
            const btnLeft = activeBtn.offsetLeft;
            const btnWidth = activeBtn.offsetWidth;

            // Center the active button
            daysContainer.scrollLeft = btnLeft - (containerWidth / 2) + (btnWidth / 2);
        }
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function loadDayBookings(date) {
        // Getting staff_id and location_code from the URL
        const urlParts = window.location.pathname.split('/');
        const staffIdIndex = urlParts.indexOf('staff_dashboard') + 1;
        const staffId = urlParts[staffIdIndex];
        const locationCode = urlParts[staffIdIndex + 1];

        // Collecting all filter values
        const filterData = {
            selected_date: date,
            book_id: bookIdFilter ? bookIdFilter.value : '',
            first_name: firstNameFilter ? firstNameFilter.value : '',
            last_name: lastNameFilter ? lastNameFilter.value : '',
            checkin: checkinFilter ? checkinFilter.value : '',
            checkout: checkoutFilter ? checkoutFilter.value : '',
            requests: requestsFilter ? requestsFilter.value : '',
            status: statusFilter ? statusFilter.value : 'all'
        };

        // Fading out the current bookings
        if (bookingsTable) {
            bookingsTable.classList.add('bookings-fade');
        }

        // Making the request to the server
        fetch(`staff_specific_date/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "Content-Type": "application/json"
            },
            body: JSON.stringify(filterData)
        })
        .then(response => response.json())
        .then(data => {
            setTimeout(() => {
                if (!bookingsTable) return;

                // Clear existing bookings
                while (bookingsTable.firstChild) {
                    bookingsTable.removeChild(bookingsTable.firstChild);
                }

                // If no bookings, show message
                if (data.bookings.length === 0) {
                    const noBookingsRow = document.createElement('tr');
                    const noBookingsCell = document.createElement('td');
                    noBookingsCell.colSpan = 7;
                    noBookingsCell.className = 'no-bookings';
                    noBookingsCell.textContent = 'No bookings found';
                    noBookingsRow.appendChild(noBookingsCell);
                    bookingsTable.appendChild(noBookingsRow);
                } else {
                    // Adding bookings to the table
                    data.bookings.forEach(booking => {
                        const row = document.createElement('tr');

                        // Constructing the dynamic URL using JavaScript
                        const bookingDetailsUrl = `/staff/${booking.staff_id}/${booking.location_code}/booking/${booking.booking_id}/`;

                        // Adding click event to the row
                        row.addEventListener('click', function() {
                            window.location.href = bookingDetailsUrl;
                        });

                        // Creating cells for each booking property
                        const properties = [
                            'booking_id',
                            'user_first_name',
                            'user_last_name',
                            'start_time',
                            'end_time',
                            'special_requests',
                            'status'
                        ];

                        properties.forEach((prop, index) => {
                            const cell = document.createElement('td');

                            if (prop === 'status') {
                                // Creating status badge with appropriate icon
                                const statusBadge = document.createElement('div');
                                const status = booking[prop] ? booking[prop].toLowerCase() : '';
                                const slugifiedStatus = status.replace(/\s+/g, '-');

                                statusBadge.className = `status-badge status-${slugifiedStatus}`;

                                // Adding appropriate icon based on status
                                const icon = document.createElement('span');
                                icon.className = 'material-icons';

                                switch(status) {
                                    case 'booked':
                                        icon.textContent = 'event_available';
                                        break;
                                    case 'in progress':
                                        icon.textContent = 'hourglass_top';
                                        break;
                                    case 'finished':
                                        icon.textContent = 'task_alt';
                                        break;
                                    case 'due out':
                                        icon.textContent = 'schedule';
                                        break;
                                    case 'cancelled':
                                        icon.textContent = 'cancel';
                                        break;
                                    default:
                                        icon.textContent = 'help_outline';
                                }

                                statusBadge.appendChild(icon);
                                statusBadge.appendChild(document.createTextNode(booking[prop] || ''));
                                cell.appendChild(statusBadge);
                            } else if (prop === 'start_time' || prop === 'end_time') {
                                cell.textContent = booking[prop] || 'N/A';
                            } else {
                                cell.textContent = booking[prop] || '';
                            }

                            row.appendChild(cell);
                        });

                        bookingsTable.appendChild(row);
                    });
                }

                // Fading in the new bookings
                bookingsTable.classList.remove('bookings-fade');

                // Applying client-side filters as well (for consistency)
                filterBookings();
            }, 300); // Slighting delay for fade effect
        })
        .catch(error => {
            console.error('Error loading bookings:', error);

            if (!bookingsTable) return;

            // Showing error message
            while (bookingsTable.firstChild) {
                bookingsTable.removeChild(bookingsTable.firstChild);
            }

            const errorRow = document.createElement('tr');
            const errorCell = document.createElement('td');
            errorCell.colSpan = 7;
            errorCell.className = 'error-message';
            errorCell.textContent = 'Error loading bookings. Please try again.';
            errorRow.appendChild(errorCell);
            bookingsTable.appendChild(errorRow);

            bookingsTable.classList.remove('bookings-fade');
        });
    }

    // Auto-hiding messages after 5 seconds
    function initMessages() {
        setTimeout(function() {
            const messages = document.querySelector('.messages');
            if (messages) {
                messages.style.opacity = '0';
                setTimeout(() => {
                    if (messages) {
                        messages.style.display = 'none';
                    }
                }, 300);
            }
        }, 5000);
    }
});