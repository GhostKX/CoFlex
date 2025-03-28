document.addEventListener('DOMContentLoaded', function() {
    const photoEditBtn = document.querySelector('.photo-edit-btn');
    const fileInput = document.querySelector('input[type="file"]');
    const profilePhotoForm = document.querySelector('form[action*="update_profile_photo"]');

    // Hide file input
    fileInput.style.display = 'none';

    photoEditBtn.addEventListener('click', function(e) {
        e.preventDefault();
        fileInput.click();
    });

    fileInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            const file = e.target.files[0];

            const validTypes = ['image/jpeg', 'image/png', 'image/gif'];

            if (!validTypes.includes(file.type)) {
                alert('Please upload a valid image (JPEG, PNG, or GIF)');
                return;
            }

            if (file.size > 5 * 1024 * 1024) {
                alert('File size should be less than 5MB');
                return;
            }

            profilePhotoForm.submit();
        }
    });
});