document.addEventListener('DOMContentLoaded', function() {
    const rentalForm = document.getElementById('rentalRequestForm');
    const startDate = document.querySelector('input[name="startDate"]');
    const endDate = document.querySelector('input[name="endDate"]');
    const rentalFeePerDay = parseFloat(document.querySelector('.rental-fee').textContent.match(/₱([\d.]+)/)[1]);

    // Set minimum date to today
    const today = new Date().toISOString().split('T')[0];
    startDate.min = today;
    endDate.min = today;

    // Calculate total amount and days
    function calculateTotal() {
        const start = new Date(startDate.value);
        const end = new Date(endDate.value);
        if (start && end && end >= start) {
            const days = Math.ceil((end - start) / (1000 * 60 * 60 * 24));
            const total = days * rentalFeePerDay;
            document.getElementById('gcashAmount').textContent = total.toFixed(2);
            document.getElementById('rentalDays').textContent = days;
            return { days, total };
        }
        return null;
    }

    // Update end date minimum when start date changes
    startDate.addEventListener('change', function() {
        endDate.min = this.value;
        if (endDate.value && endDate.value < this.value) {
            endDate.value = this.value;
        }
        calculateTotal();
    });

    endDate.addEventListener('change', calculateTotal);

    function submitRentalRequest() {
        const formData = new FormData(rentalForm);
        const calculation = calculateTotal();
        
        // Add rental days and total amount
        formData.append('rental_days', calculation.days);
        formData.append('total_amount', calculation.total);

        // Add GCash payment details if applicable
        if (formData.get('paymentMethod') === 'GCASH') {
            const gcashForm = document.getElementById('gcashPaymentForm');
            const reference = gcashForm.querySelector('input[name="gcash_reference"]').value;
            const proofFile = gcashForm.querySelector('input[name="payment_proof"]').files[0];
            
            if (reference) formData.append('gcash_reference', reference);
            if (proofFile) formData.append('payment_proof', proofFile);
        }

        // Send the request
        fetch('/submit-rental-request', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                window.location.href = '/orders';
            } else {
                alert(data.message || 'An error occurred while submitting your request.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while submitting your request.');
        });
    }

    // Handle form submission
    rentalForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const calculation = calculateTotal();
        if (!calculation) {
            alert('Please select valid dates');
            return;
        }

        const paymentMethod = document.querySelector('input[name="paymentMethod"]:checked').value;
        
        if (paymentMethod === 'GCASH') {
            // Show GCash payment modal
            new bootstrap.Modal(document.getElementById('gcashPaymentModal')).show();
        } else {
            // Submit form directly for cash payment
            submitRentalRequest();
        }
    });

    // Handle GCash payment confirmation
    document.getElementById('confirmGcashPayment').addEventListener('click', function() {
        const gcashForm = document.getElementById('gcashPaymentForm');
        if (gcashForm.checkValidity()) {
            // Close GCash modal
            bootstrap.Modal.getInstance(document.getElementById('gcashPaymentModal')).hide();
            
            // Submit rental request with GCash details
            submitRentalRequest();
        } else {
            gcashForm.reportValidity();
        }
    });
}); 