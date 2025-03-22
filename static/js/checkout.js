document.addEventListener('DOMContentLoaded', function() {
    const checkoutForm = document.getElementById('checkoutForm');
    const newAddressForm = document.getElementById('newAddressForm');
    const addNewAddressBtn = document.getElementById('addNewAddress');
    const savedAddressInputs = document.querySelectorAll('input[name="savedAddress"]');
    const newAddressInputs = newAddressForm.querySelectorAll('input, textarea');

    // Toggle form fields required attribute based on address selection
    function toggleNewAddressRequired(isNewAddress) {
        newAddressInputs.forEach(input => {
            input.required = isNewAddress;
        });
    }

    if (addNewAddressBtn) {
        addNewAddressBtn.addEventListener('click', function() {
            newAddressForm.classList.remove('d-none');
            // Clear any selected saved address
            savedAddressInputs.forEach(input => input.checked = false);
            toggleNewAddressRequired(true);
        });
    }

    // Handle saved address selection
    savedAddressInputs.forEach(input => {
        input.addEventListener('change', function() {
            if (this.checked) {
                newAddressForm.classList.add('d-none');
                toggleNewAddressRequired(false);
            }
        });
    });

    checkoutForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const paymentMethod = document.querySelector('input[name="paymentMethod"]:checked').value;
        
        if (paymentMethod === 'GCASH') {
            // Show GCash payment modal
            new bootstrap.Modal(document.getElementById('gcashPaymentModal')).show();
        } else {
            // Handle cash payment directly
            submitOrder();
        }
    });

    // Payment method change handler
    document.querySelectorAll('input[name="paymentMethod"]').forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'GCASH') {
                // Update amount in GCash modal
                document.getElementById('gcashAmount').textContent = 
                    document.querySelector('.total h4').textContent.replace('₱', '');
            }
        });
    });

    // Handle GCash payment confirmation
    document.getElementById('confirmGcashPayment').addEventListener('click', function() {
        const gcashForm = document.getElementById('gcashPaymentForm');
        if (gcashForm.checkValidity()) {
            // Close GCash modal
            bootstrap.Modal.getInstance(document.getElementById('gcashPaymentModal')).hide();
            
            // Submit order
            submitOrder();
        } else {
            gcashForm.reportValidity();
        }
    });

    function submitOrder() {
        // Create FormData object
        const formData = new FormData(checkoutForm);
        
        // If using saved address, add it to formData
        const savedAddressRadio = document.querySelector('input[name="savedAddress"]:checked');
        if (savedAddressRadio) {
            formData.set('savedAddress', savedAddressRadio.value);
        }
        
        // Add GCash payment details if applicable
        const paymentMethod = document.querySelector('input[name="paymentMethod"]:checked').value;
        if (paymentMethod === 'GCASH') {
            const gcashForm = document.getElementById('gcashPaymentForm');
            formData.append('gcash_reference', gcashForm.querySelector('input[type="text"]').value);
            formData.append('payment_proof', gcashForm.querySelector('input[type="file"]').files[0]);
        }
        
        // Send the request
        fetch('/place-order', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const successModal = new bootstrap.Modal(document.getElementById('orderSuccessModal'));
                document.getElementById('successOrderId').textContent = 'ORD-' + data.orderId;
                successModal.show();
            } else {
                alert(data.message || 'An error occurred while placing your order');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while placing your order');
        });
    }
}); 