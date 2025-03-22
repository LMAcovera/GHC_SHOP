function changeMainImage(src) {
    document.getElementById('mainImage').src = src;
    
    // Update active thumbnail
    document.querySelectorAll('.thumbnail').forEach(thumb => {
        thumb.classList.remove('active');
        if (thumb.src === src) {
            thumb.classList.add('active');
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // Size selection
    const sizeBoxes = document.querySelectorAll('.size-box');
    const selectedSizeInput = document.getElementById('selectedSize');

    sizeBoxes.forEach(box => {
        box.addEventListener('click', function() {
            // Remove selected class from all boxes
            sizeBoxes.forEach(b => b.classList.remove('selected'));
            // Add selected class to clicked box
            this.classList.add('selected');
            // Update hidden input value
            selectedSizeInput.value = this.dataset.size;
        });
    });

    // Update rent button handler
    document.getElementById('rentNow').addEventListener('click', function() {
        const selectedSize = selectedSizeInput.value;
        if (!selectedSize) {
            alert('Please select a size first');
            return;
        }

        // Check if user is logged in
        if (document.body.dataset.userLoggedIn !== 'true') {
            alert('Please login to continue');
            window.location.href = '/login';
            return;
        }

        // Redirect to rental request form with product ID and size
        window.location.href = `/rental-request/${productId}?size=${selectedSize}`;
    });

    document.getElementById('buyNow').addEventListener('click', function() {
        const selectedSize = document.getElementById('selectedSize').value;
        if (!selectedSize) {
            alert('Please select a size first');
            return;
        }
        
        // Check if user is logged in (you can pass this from template too)
        if (!document.body.dataset.userLoggedIn) {
            alert('Please login to continue');
            window.location.href = '/login';
            return;
        }
        
        try {
            window.location.href = `/checkout?product_id=${productId}&size=${selectedSize}&type=purchase`;
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        }
    });

    const wishlistBtn = document.getElementById('addToWishlist');
    
    // Check if product is in wishlist on page load
    if (document.body.dataset.userLoggedIn === 'true') {
        fetch(`/check-wishlist/${productId}`)
            .then(response => response.json())
            .then(data => {
                if (data.inWishlist) {
                    wishlistBtn.classList.add('active');
                    wishlistBtn.innerHTML = '<i class="fas fa-heart me-2"></i>Remove from Wishlist';
                }
            });
    }

    wishlistBtn.addEventListener('click', function() {
        // Check if user is logged in
        if (document.body.dataset.userLoggedIn !== 'true') {
            alert('Please login to add items to your wishlist');
            window.location.href = '/login';
            return;
        }

        fetch(`/toggle-wishlist/${productId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                if (data.status === 'added') {
                    wishlistBtn.classList.add('active');
                    wishlistBtn.innerHTML = '<i class="fas fa-heart me-2"></i>Remove from Wishlist';
                    showToast('Product added to wishlist!', 'success');
                } else {
                    wishlistBtn.classList.remove('active');
                    wishlistBtn.innerHTML = '<i class="fas fa-heart me-2"></i>Add to Wishlist';
                    showToast('Product removed from wishlist!', 'info');
                }
            } else {
                showToast('Error updating wishlist', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('An error occurred', 'error');
        });
    });

    // Reserve Now button handler
    document.getElementById('reserveNow').addEventListener('click', function() {
        const selectedSize = selectedSizeInput.value;
        if (!selectedSize) {
            alert('Please select a size first');
            return;
        }

        // Check if user is logged in
        if (document.body.dataset.userLoggedIn !== 'true') {
            alert('Please login to continue');
            window.location.href = '/login';
            return;
        }

        // Show reservation modal
        const reserveModal = new bootstrap.Modal(document.getElementById('reserveRequestModal'));
        reserveModal.show();
    });

    // Submit reservation handler
    document.getElementById('submitReservation').addEventListener('click', function() {
        const form = document.getElementById('reserveRequestForm');
        const formData = new FormData(form);
        formData.append('size', selectedSizeInput.value);

        fetch('/submit-reservation', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Reservation submitted successfully!');
                window.location.href = '/orders';
            } else {
                alert(data.message || 'Error submitting reservation');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        });
    });
});

function showToast(message, type) {
    // You can implement a toast notification here
    alert(message);
} 