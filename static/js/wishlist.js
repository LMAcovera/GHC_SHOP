document.addEventListener('DOMContentLoaded', function() {
    // Handle remove from wishlist
    document.querySelectorAll('.remove-wishlist').forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.closest('.wishlist-item').dataset.productId;
            
            if (confirm('Are you sure you want to remove this item from your wishlist?')) {
                fetch(`/toggle-wishlist/${productId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Remove the card with animation
                        const card = this.closest('.col');
                        card.style.opacity = '0';
                        setTimeout(() => {
                            card.remove();
                            
                            // Check if wishlist is empty
                            if (document.querySelectorAll('.wishlist-item').length === 0) {
                                location.reload(); // Reload to show empty state
                            }
                        }, 300);
                    } else {
                        alert('Error removing item from wishlist');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred');
                });
            }
        });
    });
}); 