document.addEventListener('DOMContentLoaded', function() {
    const bookingForm = document.getElementById('bookingForm');
    const inspirationPreview = document.getElementById('inspirationPreview');
    
    // Initialize date picker with minimum date as tomorrow
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const dateInput = document.getElementById('preferred_date');
    dateInput.min = tomorrow.toISOString().split('T')[0];
    
    // Handle image preview
    document.getElementById('inspiration_image').addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                inspirationPreview.src = e.target.result;
                inspirationPreview.style.display = 'block';
            };
            reader.readAsDataURL(file);
        }
    });
    
    // Form submission
    bookingForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(bookingForm);
        
        // Validate budget
        const budget = parseFloat(formData.get('budget_range'));
        if (budget < 5000) {
            alert('Minimum budget should be ₱5,000');
            return;
        }
        
        // Show loading state
        const submitBtn = bookingForm.querySelector('button[type="submit"]');
        const originalBtnText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Submitting...';
        
        fetch('/book-appointment', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                Swal.fire({
                    icon: 'success',
                    title: 'Success!',
                    text: data.message,
                    confirmButtonText: 'OK'
                }).then(() => {
                    window.location.href = '/orders';
                });
            } else {
                throw new Error(data.message || 'Something went wrong');
            }
        })
        .catch(error => {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: error.message
            });
        })
        .finally(() => {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnText;
        });
    });
    
    // Budget range input formatting
    const budgetInput = document.getElementById('budget');
    budgetInput.addEventListener('input', function() {
        let value = this.value.replace(/[^0-9]/g, '');
        if (value) {
            value = parseInt(value);
            if (value < 5000) value = 5000;
            this.value = value;
        }
    });
}); 