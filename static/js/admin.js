document.addEventListener('DOMContentLoaded', function() {
    // Handle product submission
    const submitButton = document.getElementById('submitProduct');
    const addProductForm = document.getElementById('addProductForm');

    submitButton.addEventListener('click', function() {
        if (addProductForm.checkValidity()) {
            const formData = new FormData(addProductForm);
            
            fetch('/admin/add-product', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert(data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while adding the product');
            });
        } else {
            addProductForm.reportValidity();
        }
    });

    // Handle product deletion
    document.querySelectorAll('.delete-product').forEach(button => {
        button.addEventListener('click', function() {
            if (confirm('Are you sure you want to delete this product?')) {
                const productId = this.dataset.productId;
                
                fetch(`/admin/delete-product/${productId}`, {
                    method: 'DELETE'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        location.reload();
                    } else {
                        alert(data.message);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred while deleting the product');
                });
            }
        });
    });

    // Handle adding new size fields
    document.querySelector('.add-size').addEventListener('click', function() {
        const sizesContainer = document.getElementById('sizesContainer');
        const newSizeGroup = document.createElement('div');
        newSizeGroup.className = 'input-group mb-2';
        newSizeGroup.innerHTML = `
            <input type="text" class="form-control" name="sizes[]" required>
            <button type="button" class="btn btn-danger remove-size">
                <i class="fas fa-minus"></i>
            </button>
        `;
        sizesContainer.appendChild(newSizeGroup);

        // Add remove handler to new button
        newSizeGroup.querySelector('.remove-size').addEventListener('click', function() {
            this.closest('.input-group').remove();
        });
    });

    // Only initialize if we're on the revenue tab
    if (document.getElementById('revenueChart')) {
        initializeRevenueAnalytics();
    }
});

function filterOrders(status) {
    const rows = document.querySelectorAll('.order-row');
    rows.forEach(row => {
        if (status === 'all' || row.dataset.status === status) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// Handle order info button click
document.querySelectorAll('.view-order').forEach(button => {
    button.addEventListener('click', function() {
        const orderId = this.dataset.orderId;
        
        fetch(`/admin/order-details/${orderId}`)
            .then(response => response.json())
            .then(data => {
                const details = document.getElementById('orderDetails');
                details.innerHTML = `
                    <div class="order-details-container">
                        <div class="order-section customer-info">
                            <div class="section-header">
                                <i class="fas fa-user-circle"></i>
                                <h5>Customer Information</h5>
                            </div>
                            <div class="info-grid">
                                <div class="info-item">
                                    <label>Name</label>
                                    <span>${data.customer_name}</span>
                                </div>
                                <div class="info-item">
                                    <label>Contact</label>
                                    <span>${data.contact_number}</span>
                                </div>
                                <div class="info-item full-width">
                                    <label>Address</label>
                                    <span>${data.complete_address}</span>
                                </div>
                            </div>
                        </div>

                        <div class="order-section order-info">
                            <div class="section-header">
                                <i class="fas fa-shopping-cart"></i>
                                <h5>Order Information</h5>
                            </div>
                            <div class="info-grid">
                                <div class="info-item">
                                    <label>Order ID</label>
                                    <span>#${data.order_id}</span>
                                </div>
                                <div class="info-item">
                                    <label>Product</label>
                                    <span>${data.product_name}</span>
                                </div>
                                <div class="info-item">
                                    <label>Size</label>
                                    <span>${data.size}</span>
                                </div>
                                <div class="info-item">
                                    <label>Total Amount</label>
                                    <span class="amount">₱${parseFloat(data.total_amount).toFixed(2)}</span>
                                </div>
                                <div class="info-item">
                                    <label>Payment Method</label>
                                    <span>${data.payment_method}</span>
                                </div>
                                <div class="info-item">
                                    <label>Delivery Method</label>
                                    <span>${data.delivery_method}</span>
                                </div>
                                <div class="info-item">
                                    <label>Status</label>
                                    <span class="status-badge ${data.order_status.toLowerCase()}">${data.order_status}</span>
                                </div>
                                <div class="info-item">
                                    <label>Order Date</label>
                                    <span>${new Date(data.created_at).toLocaleString()}</span>
                                </div>
                            </div>
                        </div>

                        ${data.payment_method === 'GCASH' ? `
                            <div class="order-section payment-info">
                                <div class="section-header">
                                    <i class="fas fa-money-bill-wave"></i>
                                    <h5>GCash Payment Details</h5>
                                </div>
                                <div class="info-grid">
                                    <div class="info-item">
                                        <label>Reference Number</label>
                                        <span class="reference-number">${data.gcash_reference || 'N/A'}</span>
                                    </div>
                                    ${data.payment_proof ? `
                                        <div class="info-item full-width">
                                            <label>Payment Proof</label>
                                            <div class="payment-proof-container">
                                                <img src="/static/${data.payment_proof}" 
                                                     alt="Payment Proof" 
                                                     class="payment-proof-image">
                                            </div>
                                        </div>
                                    ` : ''}
                                </div>
                            </div>
                        ` : ''}
                    </div>
                `;
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error loading order details');
            });
    });
});

// Handle order status update
document.querySelectorAll('.update-order').forEach(button => {
    button.addEventListener('click', function() {
        const orderId = this.dataset.orderId;
        const currentStatus = this.closest('tr').querySelector('.badge').textContent.toLowerCase();
        
        // Set the current status in the dropdown
        document.getElementById('orderStatus').value = currentStatus;
        document.getElementById('updateOrderId').value = orderId;
        
        // Show the modal
        new bootstrap.Modal(document.getElementById('updateOrderModal')).show();
    });
});

// Add handler for update confirmation
document.getElementById('confirmUpdateOrder').addEventListener('click', function() {
    const orderId = document.getElementById('updateOrderId').value;
    const newStatus = document.getElementById('orderStatus').value;
    
    fetch(`/admin/update-order-status/${orderId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: newStatus })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert(data.message);
        }
    });
});

// Handle order deletion
document.querySelectorAll('.delete-order').forEach(button => {
    button.addEventListener('click', function() {
        if (confirm('Are you sure you want to delete this order?')) {
            const orderId = this.dataset.orderId;
            fetch(`/admin/delete-order/${orderId}`, {
                method: 'DELETE'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert(data.message);
                }
            });
        }
    });
});

function filterRequests(type) {
    const rows = document.querySelectorAll('.request-row');
    rows.forEach(row => {
        if (type === 'all' || row.dataset.type === type) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// Handle request info button click
document.querySelectorAll('.view-request').forEach(button => {
    button.addEventListener('click', function() {
        const requestId = this.dataset.requestId;
        const requestType = this.dataset.requestType;
        
        console.log('Request ID:', requestId); // Debug log
        console.log('Request Type:', requestType); // Debug log
        
        if (requestType === 'appointment') {
            fetch(`/admin/request-details/appointment/${requestId}`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                const details = document.getElementById('requestDetails');
                details.innerHTML = `
                    <div class="order-details-container">
                        <div class="order-section customer-info">
                            <div class="section-header">
                                <i class="fas fa-user-circle"></i>
                                <h5>Customer Information</h5>
                            </div>
                            <div class="info-grid">
                                <div class="info-item">
                                    <label>Name</label>
                                    <span>${data.full_name}</span>
                                </div>
                                <div class="info-item">
                                    <label>Contact</label>
                                    <span>${data.contact_number}</span>
                                </div>
                            </div>
                        </div>

                        <div class="order-section appointment-info">
                            <div class="section-header">
                                <i class="fas fa-calendar-check"></i>
                                <h5>Appointment Details</h5>
                            </div>
                            <div class="info-grid">
                                <div class="info-item">
                                    <label>Category</label>
                                    <span>${data.category_name}</span>
                                </div>
                                <div class="info-item">
                                    <label>Preferred Date</label>
                                    <span>${data.preferred_date}</span>
                                </div>
                                <div class="info-item">
                                    <label>Preferred Time</label>
                                    <span>${data.preferred_time}</span>
                                </div>
                                <div class="info-item">
                                    <label>Budget Range</label>
                                    <span>₱${parseFloat(data.budget_range).toFixed(2)}</span>
                                </div>
                                <div class="info-item full-width">
                                    <label>Design Description</label>
                                    <span>${data.description}</span>
                                </div>
                                ${data.special_requirements ? `
                                    <div class="info-item full-width">
                                        <label>Special Requirements</label>
                                        <span>${data.special_requirements}</span>
                                    </div>
                                ` : ''}
                            </div>
                        </div>

                        ${data.inspiration_image ? `
                            <div class="order-section inspiration-info">
                                <div class="section-header">
                                    <i class="fas fa-image"></i>
                                    <h5>Inspiration Image</h5>
                                </div>
                                <div class="inspiration-image-container">
                                    <img src="/static/${data.inspiration_image}" 
                                         alt="Inspiration Image" 
                                         class="inspiration-image">
                                </div>
                            </div>
                        ` : ''}
                    </div>
                `;
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error loading appointment details');
            });
        } else {
            fetch(`/admin/request-details/${requestType}/${requestId}`)
                .then(response => response.json())
                .then(data => {
                    const details = document.getElementById('requestDetails');
                    
                    if (requestType === 'appointment') {
                        details.innerHTML = `
                            <div class="order-details-container">
                                <div class="order-section customer-info">
                                    <div class="section-header">
                                        <i class="fas fa-user-circle"></i>
                                        <h5>Customer Information</h5>
                                    </div>
                                    <div class="info-grid">
                                        <div class="info-item">
                                            <label>Name</label>
                                            <span>${data.full_name}</span>
                                        </div>
                                        <div class="info-item">
                                            <label>Contact</label>
                                            <span>${data.contact_number}</span>
                                        </div>
                                    </div>
                                </div>

                                <div class="order-section appointment-info">
                                    <div class="section-header">
                                        <i class="fas fa-calendar-check"></i>
                                        <h5>Appointment Details</h5>
                                    </div>
                                    <div class="info-grid">
                                        <div class="info-item">
                                            <label>Category</label>
                                            <span>${data.category_name}</span>
                                        </div>
                                        <div class="info-item">
                                            <label>Preferred Date</label>
                                            <span>${data.preferred_date}</span>
                                        </div>
                                        <div class="info-item">
                                            <label>Preferred Time</label>
                                            <span>${data.preferred_time}</span>
                                        </div>
                                        <div class="info-item">
                                            <label>Budget Range</label>
                                            <span>₱${parseFloat(data.budget_range).toFixed(2)}</span>
                                        </div>
                                        <div class="info-item full-width">
                                            <label>Design Description</label>
                                            <span>${data.description}</span>
                                        </div>
                                        <div class="info-item full-width">
                                            <label>Special Requirements</label>
                                            <span>${data.special_requirements || 'None'}</span>
                                        </div>
                                    </div>
                                </div>

                                ${data.inspiration_image ? `
                                    <div class="order-section inspiration-info">
                                        <div class="section-header">
                                            <i class="fas fa-image"></i>
                                            <h5>Inspiration Image</h5>
                                        </div>
                                        <div class="inspiration-image-container">
                                            <img src="/static/${data.inspiration_image}" 
                                                 alt="Inspiration Image" 
                                                 class="inspiration-image">
                                        </div>
                                    </div>
                                ` : ''}
                            </div>
                        `;
                    } else {
                        details.innerHTML = `
                            <div class="order-details-container">
                                <div class="order-section customer-info">
                                    <div class="section-header">
                                        <i class="fas fa-user-circle"></i>
                                        <h5>Customer Information</h5>
                                    </div>
                                    <div class="info-grid">
                                        <div class="info-item">
                                            <label>Name</label>
                                            <span>${data.full_name}</span>
                                        </div>
                                        <div class="info-item">
                                            <label>Contact</label>
                                            <span>${data.contact_number}</span>
                                        </div>
                                        <div class="info-item full-width">
                                            <label>Address</label>
                                            <span>${data.address}</span>
                                        </div>
                                    </div>
                                </div>

                                <div class="order-section product-info">
                                    <div class="section-header">
                                        <i class="fas fa-tshirt"></i>
                                        <h5>Product Information</h5>
                                    </div>
                                    <div class="info-grid">
                                        <div class="info-item">
                                            <label>Product</label>
                                            <span>${data.product_name}</span>
                                        </div>
                                        <div class="info-item">
                                            <label>Size</label>
                                            <span>${data.size}</span>
                                        </div>
                                        <div class="info-item">
                                            <label>Rental Fee/Day</label>
                                            <span class="amount">₱${data.rental_fee_per_day}</span>
                                        </div>
                                    </div>
                                </div>

                                <div class="order-section rental-info">
                                    <div class="section-header">
                                        <i class="fas fa-calendar-alt"></i>
                                        <h5>Rental Details</h5>
                                    </div>
                                    <div class="info-grid">
                                        <div class="info-item">
                                            <label>Start Date</label>
                                            <span>${data.start_date}</span>
                                        </div>
                                        <div class="info-item">
                                            <label>End Date</label>
                                            <span>${data.end_date}</span>
                                        </div>
                                        <div class="info-item">
                                            <label>Number of Days</label>
                                            <span>${data.rental_days}</span>
                                        </div>
                                        <div class="info-item">
                                            <label>Total Rental Fee</label>
                                            <span class="amount">₱${data.total_rental_fee}</span>
                                        </div>
                                        <div class="info-item">
                                            <label>Payment Method</label>
                                            <span>${data.payment_method}</span>
                                        </div>
                                        <div class="info-item">
                                            <label>Status</label>
                                            <span class="status-badge ${data.status.toLowerCase()}">${data.status}</span>
                                        </div>
                                    </div>
                                    ${data.payment_method === 'GCASH' ? `
                                        <div class="info-grid mt-3">
                                            <div class="info-item">
                                                <label>GCash Reference</label>
                                                <span class="reference-number">${data.gcash_reference || 'N/A'}</span>
                                            </div>
                                            ${data.payment_proof ? `
                                                <div class="info-item full-width">
                                                    <label>Payment Proof</label>
                                                    <div class="payment-proof-container">
                                                        <img src="/static/${data.payment_proof}" 
                                                             alt="Payment Proof" 
                                                             class="payment-proof-image">
                                                    </div>
                                                </div>
                                            ` : ''}
                                        </div>
                                    ` : ''}
                                </div>

                                <div class="order-section id-info">
                                    <div class="section-header">
                                        <i class="fas fa-id-card"></i>
                                        <h5>Valid ID</h5>
                                    </div>
                                    ${data.valid_id_path ? `
                                        <div class="valid-id-container">
                                            <img src="/static/${data.valid_id_path}" 
                                                 alt="Valid ID" 
                                                 class="valid-id-image">
                                        </div>
                                    ` : '<p class="text-muted">No valid ID uploaded</p>'}
                                </div>
                            </div>
                        `;
                    }
                });
        }
    });
});

// Handle request status update
document.querySelectorAll('.update-request').forEach(button => {
    button.addEventListener('click', function() {
        const requestId = this.dataset.requestId;
        const requestType = this.dataset.requestType;
        document.getElementById('updateRequestId').value = requestId;
        document.getElementById('updateRequestType').value = requestType;
    });
});

document.getElementById('confirmUpdateRequest').addEventListener('click', function() {
    const appointmentId = document.getElementById('updateRequestId').value;
    const requestType = document.getElementById('updateRequestType').value;
    const status = document.getElementById('requestStatus').value;
    const note = document.getElementById('statusNote').value;

    // Make sure we have an ID
    if (!appointmentId) {
        console.error('No appointment ID found');
        alert('Error: Missing appointment ID');
        return;
    }

    // Build the correct URL with the ID
    const url = `/admin/update-request-status/${requestType}/${appointmentId}`;
    console.log('Sending request to:', url); // Debug log

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            status: status,
            note: note 
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Close modal and refresh page
            const modal = bootstrap.Modal.getInstance(document.getElementById('updateRequestModal'));
            modal.hide();
            location.reload();
        } else {
            alert('Error: ' + (data.message || 'Failed to update status'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error updating request status: ' + error.message);
    });
});

// Handle request deletion
document.querySelectorAll('.delete-request').forEach(button => {
    button.addEventListener('click', function() {
        if (confirm('Are you sure you want to delete this request?')) {
            const requestId = this.dataset.requestId;
            const requestType = this.dataset.requestType;
            
            fetch(`/admin/delete-request/${requestType}/${requestId}`, {
                method: 'DELETE'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert(data.message);
                }
            });
        }
    });
});

function filterRentals(status) {
    const rows = document.querySelectorAll('.rental-row');
    rows.forEach(row => {
        if (status === 'all' || row.dataset.status === status) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// Handle rental info button click
document.querySelectorAll('.view-rental').forEach(button => {
    button.addEventListener('click', function() {
        const rentalId = this.dataset.rentalId;
        
        fetch(`/admin/rental-details/${rentalId}`)
            .then(response => response.json())
            .then(rental => {
                const details = document.getElementById('rentalDetails');
                details.innerHTML = `
                    <div class="order-details-container">
                        <div class="order-section customer-info">
                            <div class="section-header">
                                <i class="fas fa-user-circle"></i>
                                <h5>Customer Information</h5>
                            </div>
                            <div class="info-grid">
                                <div class="info-item">
                                    <label>Name</label>
                                    <span>${rental.customer_name}</span>
                                </div>
                                <div class="info-item">
                                    <label>Contact</label>
                                    <span>${rental.contact_number}</span>
                                </div>
                                <div class="info-item full-width">
                                    <label>Address</label>
                                    <span>${rental.address}</span>
                                </div>
                            </div>
                        </div>

                        <div class="order-section rental-info">
                            <div class="section-header">
                                <i class="fas fa-calendar-alt"></i>
                                <h5>Rental Details</h5>
                            </div>
                            <div class="info-grid">
                                <div class="info-item">
                                    <label>Product</label>
                                    <span>${rental.product_name}</span>
                                </div>
                                <div class="info-item">
                                    <label>Size</label>
                                    <span>${rental.size}</span>
                                </div>
                                <div class="info-item">
                                    <label>Start Date</label>
                                    <span>${new Date(rental.start_date).toLocaleDateString()}</span>
                                </div>
                                <div class="info-item">
                                    <label>End Date</label>
                                    <span>${new Date(rental.end_date).toLocaleDateString()}</span>
                                </div>
                                <div class="info-item">
                                    <label>Total Amount</label>
                                    <span class="amount">₱${parseFloat(rental.total_amount).toFixed(2)}</span>
                                </div>
                                <div class="info-item">
                                    <label>Payment Method</label>
                                    <span>${rental.payment_method || 'N/A'}</span>
                                </div>
                            </div>
                        </div>

                        ${rental.payment_method === 'GCASH' ? `
                            <div class="order-section payment-info">
                                <div class="section-header">
                                    <i class="fas fa-money-bill-wave"></i>
                                    <h5>GCash Payment Details</h5>
                                </div>
                                <div class="info-grid">
                                    <div class="info-item">
                                        <label>Reference Number</label>
                                        <span class="reference-number">${rental.gcash_reference || 'N/A'}</span>
                                    </div>
                                    ${rental.payment_proof ? `
                                        <div class="info-item full-width">
                                            <label>Payment Proof</label>
                                            <div class="payment-proof-container">
                                                <img src="/static/${rental.payment_proof}" 
                                                     alt="Payment Proof" 
                                                     class="payment-proof-image">
                                            </div>
                                        </div>
                                    ` : ''}
                                </div>
                            </div>
                        ` : ''}

                        <div class="order-section id-info">
                            <div class="section-header">
                                <i class="fas fa-id-card"></i>
                                <h5>Valid ID</h5>
                            </div>
                            ${rental.valid_id_path ? `
                                <div class="valid-id-container">
                                    <img src="/static/${rental.valid_id_path}" 
                                         alt="Valid ID" 
                                         class="valid-id-image">
                                </div>
                            ` : '<p class="text-muted">No valid ID uploaded</p>'}
                        </div>
                    </div>
                `;
            });
    });
});

// Handle rental status update
document.querySelectorAll('.update-rental').forEach(button => {
    button.addEventListener('click', function() {
        const rentalId = this.dataset.rentalId;
        const currentStatus = this.closest('tr').querySelector('.badge').textContent.toLowerCase();
        
        document.getElementById('rentalStatus').value = currentStatus;
        document.getElementById('updateRentalId').value = rentalId;
    });
});

document.getElementById('confirmUpdateRental').addEventListener('click', function() {
    const rentalId = document.getElementById('updateRentalId').value;
    const newStatus = document.getElementById('rentalStatus').value;
    
    fetch(`/admin/update-rental-status/${rentalId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: newStatus })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert(data.message);
        }
    });
});

// Handle rental deletion
document.querySelectorAll('.delete-rental').forEach(button => {
    button.addEventListener('click', function() {
        if (confirm('Are you sure you want to delete this rental?')) {
            const rentalId = this.dataset.rentalId;
            fetch(`/admin/delete-rental/${rentalId}`, {
                method: 'DELETE'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert(data.message);
                }
            });
        }
    });
});

function showRentalDetails(rental) {
    const details = document.getElementById('rentalDetails');
    const returnSection = document.getElementById('returnSection');
    const confirmReturnBtn = document.getElementById('confirmReturnBtn');
    const returnInfo = document.getElementById('returnInfo');
    
    // Populate rental details
    details.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <h6>Customer Information</h6>
                <p><strong>Name:</strong> ${rental.customer_name}</p>
                <p><strong>Contact:</strong> ${rental.contact_number}</p>
                <p><strong>Address:</strong> ${rental.address}</p>
            </div>
            <div class="col-md-6">
                <h6>Product Information</h6>
                <p><strong>Product:</strong> ${rental.product_name}</p>
                <p><strong>Size:</strong> ${rental.size}</p>
                <p><strong>Total Amount:</strong> ₱${rental.total_amount}</p>
            </div>
        </div>
        <div class="row mt-3">
            <div class="col-md-6">
                <h6>Rental Details</h6>
                <p><strong>Start Date:</strong> ${formatDate(rental.start_date)}</p>
                <p><strong>End Date:</strong> ${formatDate(rental.end_date)}</p>
                <p><strong>Number of Days:</strong> ${rental.rental_days}</p>
                <p><strong>Status:</strong> ${rental.status}</p>
            </div>
        </div>
    `;

    // Show/hide return section based on status
    returnSection.style.display = 'block';
    
    if (rental.status === 'delivered') {
        confirmReturnBtn.style.display = 'block';
        confirmReturnBtn.textContent = 'Mark as Returned';
        returnInfo.innerHTML = '<p>Pending return confirmation</p>';
        confirmReturnBtn.onclick = () => updateRentalStatus(rental.rental_id, 'returned');
    } else if (rental.status === 'returned') {
        confirmReturnBtn.style.display = 'block';
        confirmReturnBtn.textContent = 'Confirm Return & Complete';
        returnInfo.innerHTML = '<p>Item returned, pending final inspection</p>';
        confirmReturnBtn.onclick = () => confirmReturn(rental.rental_id);
    } else if (rental.status === 'completed') {
        confirmReturnBtn.style.display = 'none';
        returnInfo.innerHTML = `
            <p>Returned on: ${formatDate(rental.return_date)}</p>
            ${rental.days_late > 0 ? `
                <p class="text-danger">Days Late: ${rental.days_late}</p>
                <p class="text-danger">Late Fee: ₱${parseFloat(rental.late_fee).toFixed(2)}</p>
                <p><strong>Final Amount: ₱${parseFloat(rental.final_amount).toFixed(2)}</strong></p>
            ` : '<p class="text-success">Returned on time</p>'}
        `;
    } else {
        returnSection.style.display = 'none';
    }
}

function updateRentalStatus(rentalId, newStatus) {
    if (confirm(`Confirm marking rental as ${newStatus}?`)) {
        fetch(`/admin/update-rental-status/${rentalId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ status: newStatus })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while updating the status');
        });
    }
}

function confirmReturn(rentalId) {
    if (confirm('Confirm return of this rental?')) {
        fetch(`/admin/confirm-return/${rentalId}`, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message);
                location.reload();
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while confirming the return');
        });
    }
}

// Revenue Analytics
function initializeRevenueAnalytics() {
    // Initialize year select
    const yearSelect = document.getElementById('yearSelect');
    const currentYear = new Date().getFullYear();
    
    // Add last 5 years to select
    for (let year = currentYear; year >= currentYear - 4; year--) {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year;
        yearSelect.appendChild(option);
    }

    // Initialize chart
    const ctx = document.getElementById('revenueChart').getContext('2d');
    const revenueChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Orders Revenue',
                    borderColor: '#36a2eb',
                    backgroundColor: 'rgba(54, 162, 235, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    data: []
                },
                {
                    label: 'Rentals Revenue',
                    borderColor: '#ff6384',
                    backgroundColor: 'rgba(255, 99, 132, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    data: []
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        padding: 20,
                        font: {
                            size: 12
                        }
                    }
                },
                title: {
                    display: true,
                    text: 'Revenue Trends',
                    padding: 20,
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '₱' + value.toLocaleString();
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            },
            elements: {
                point: {
                    radius: 3,
                    hoverRadius: 6
                },
                line: {
                    tension: 0.3
                }
            }
        }
    });

    // Load initial data
    loadRevenueData('weekly', currentYear);

    // Handle period changes
    document.querySelectorAll('[data-period]').forEach(button => {
        button.addEventListener('click', function() {
            // Update active state
            document.querySelectorAll('[data-period]').forEach(btn => 
                btn.classList.remove('active'));
            this.classList.add('active');
            
            // Load data for selected period
            loadRevenueData(this.dataset.period, yearSelect.value);
        });
    });

    // Handle year changes
    yearSelect.addEventListener('change', function() {
        const activePeriod = document.querySelector('[data-period].active').dataset.period;
        loadRevenueData(activePeriod, this.value);
    });
}

function loadRevenueData(period, year) {
    fetch(`/admin/revenue-data?period=${period}&year=${year}`)
        .then(response => response.json())
        .then(data => {
            // Update revenue cards
            document.getElementById('totalRevenue').textContent = 
                '₱' + data.summary.total.toLocaleString(undefined, {minimumFractionDigits: 2});
            document.getElementById('ordersRevenue').textContent = 
                '₱' + data.summary.orders.toLocaleString(undefined, {minimumFractionDigits: 2});
            document.getElementById('rentalsRevenue').textContent = 
                '₱' + data.summary.rentals.toLocaleString(undefined, {minimumFractionDigits: 2});
            document.getElementById('lateFees').textContent = 
                '₱' + data.summary.late_fees.toLocaleString(undefined, {minimumFractionDigits: 2});

            // Update count cards
            document.getElementById('totalOrders').textContent = 
                data.summary.total_orders.toLocaleString();
            document.getElementById('totalRentals').textContent = 
                data.summary.total_rentals.toLocaleString();
            document.getElementById('activeRentals').textContent = 
                data.summary.active_rentals.toLocaleString();
            document.getElementById('lateReturns').textContent = 
                data.summary.late_returns.toLocaleString();

            // Update chart
            const chart = Chart.getChart('revenueChart');
            chart.data.labels = data.chart.labels;
            chart.data.datasets[0].data = data.chart.orders;
            chart.data.datasets[1].data = data.chart.rentals;
            chart.update();
        })
        .catch(error => {
            console.error('Error loading revenue data:', error);
            alert('Error loading revenue data. Please try again.');
        });
}

// Handle edit product button clicks
document.querySelectorAll('.edit-product').forEach(button => {
    button.addEventListener('click', function() {
        const productId = this.dataset.productId;
        const row = this.closest('tr');
        
        // Get current values from the table row
        const regularPrice = row.querySelector('td:nth-child(4)').textContent
            .replace('₱', '').trim();
        const rentalFee = row.querySelector('td:nth-child(5)').textContent
            .replace('₱', '').trim();
        
        // Set values in the edit modal
        document.getElementById('editProductId').value = productId;
        document.getElementById('editRegularPrice').value = regularPrice;
        document.getElementById('editRentalFee').value = rentalFee;
        
        // Show the modal
        new bootstrap.Modal(document.getElementById('editProductModal')).show();
    });
});

// Handle save changes button click
document.getElementById('saveProductChanges').addEventListener('click', function() {
    const form = document.getElementById('editProductForm');
    
    if (form.checkValidity()) {
        const productId = document.getElementById('editProductId').value;
        const regularPrice = document.getElementById('editRegularPrice').value;
        const rentalFee = document.getElementById('editRentalFee').value;
        
        fetch(`/admin/update-product/${productId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                regular_price: regularPrice,
                rental_fee_per_day: rentalFee
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert(data.message || 'Error updating product');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while updating the product');
        });
    } else {
        form.reportValidity();
    }
});

// Appointment Management
function filterAppointments(status) {
    const rows = document.querySelectorAll('.appointment-row');
    rows.forEach(row => {
        if (status === 'all' || row.dataset.status === status) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// View Appointment Details
document.querySelectorAll('.view-appointment').forEach(button => {
    button.addEventListener('click', function() {
        const appointmentId = this.dataset.appointmentId;
        
        fetch(`/admin/appointment-details/${appointmentId}`)
            .then(response => response.json())
            .then(data => {
                const details = document.getElementById('appointmentDetails');
                details.innerHTML = `
                    <div class="order-details-container">
                        <div class="order-section customer-info">
                            <div class="section-header">
                                <i class="fas fa-user-circle"></i>
                                <h5>Customer Information</h5>
                            </div>
                            <div class="info-grid">
                                <div class="info-item">
                                    <label>Name</label>
                                    <span>${data.full_name}</span>
                                </div>
                                <div class="info-item">
                                    <label>Contact</label>
                                    <span>${data.contact_number}</span>
                                </div>
                            </div>
                        </div>

                        <div class="order-section appointment-info">
                            <div class="section-header">
                                <i class="fas fa-calendar-check"></i>
                                <h5>Appointment Details</h5>
                            </div>
                            <div class="info-grid">
                                <div class="info-item">
                                    <label>Category</label>
                                    <span>${data.category_name}</span>
                                </div>
                                <div class="info-item">
                                    <label>Date</label>
                                    <span>${new Date(data.appointment_date).toLocaleDateString()}</span>
                                </div>
                                <div class="info-item">
                                    <label>Time</label>
                                    <span>${data.appointment_time}</span>
                                </div>
                                <div class="info-item">
                                    <label>Budget Range</label>
                                    <span>₱${parseFloat(data.budget_range).toFixed(2)}</span>
                                </div>
                                <div class="info-item full-width">
                                    <label>Design Description</label>
                                    <span>${data.description}</span>
                                </div>
                                ${data.special_requirements ? `
                                    <div class="info-item full-width">
                                        <label>Special Requirements</label>
                                        <span>${data.special_requirements}</span>
                                    </div>
                                ` : ''}
                            </div>
                        </div>

                        ${data.inspiration_image ? `
                            <div class="order-section inspiration-info">
                                <div class="section-header">
                                    <i class="fas fa-image"></i>
                                    <h5>Inspiration Image</h5>
                                </div>
                                <div class="inspiration-image-container">
                                    <img src="/static/${data.inspiration_image}" 
                                         alt="Inspiration Image" 
                                         class="inspiration-image">
                                </div>
                            </div>
                        ` : ''}
                    </div>
                `;
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error loading appointment details');
            });
    });
});

// Update Appointment Status
document.querySelectorAll('.update-appointment').forEach(button => {
    button.addEventListener('click', function() {
        const appointmentId = this.dataset.appointmentId;
        document.getElementById('updateAppointmentId').value = appointmentId;
    });
});

document.getElementById('confirmUpdateAppointment')?.addEventListener('click', function() {
    const appointmentId = document.getElementById('updateAppointmentId').value;
    const status = document.getElementById('appointmentStatus').value;
    
    fetch(`/admin/update-appointment-status/${appointmentId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: status })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error updating appointment status');
    });
});

// Delete Appointment
document.querySelectorAll('.delete-appointment').forEach(button => {
    button.addEventListener('click', function() {
        if (confirm('Are you sure you want to delete this appointment?')) {
            const appointmentId = this.dataset.appointmentId;
            
            fetch(`/admin/delete-appointment/${appointmentId}`, {
                method: 'DELETE'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert(data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error deleting appointment');
            });
        }
    });
});

// Handle reservation info button click
document.querySelectorAll('.view-reservation').forEach(button => {
    button.addEventListener('click', function() {
        const reservationId = this.dataset.reservationId;
        
        fetch(`/admin/reservation-details/${reservationId}`)
            .then(response => response.json())
            .then(data => {
                const details = document.getElementById('reservationDetails');
                details.innerHTML = `
                    <div class="order-details-container">
                        <div class="order-section customer-info">
                            <div class="section-header">
                                <i class="fas fa-user-circle"></i>
                                <h5>Customer Information</h5>
                            </div>
                            <div class="info-grid">
                                <div class="info-item">
                                    <label>Name</label>
                                    <span>${data.full_name}</span>
                                </div>
                                <div class="info-item">
                                    <label>Contact</label>
                                    <span>${data.contact_number}</span>
                                </div>
                                <div class="info-item full-width">
                                    <label>Address</label>
                                    <span>${data.address}</span>
                                </div>
                            </div>
                        </div>

                        <div class="order-section product-info">
                            <div class="section-header">
                                <i class="fas fa-tshirt"></i>
                                <h5>Product Information</h5>
                            </div>
                            <div class="info-grid">
                                <div class="info-item">
                                    <label>Product</label>
                                    <span>${data.product_name}</span>
                                </div>
                                <div class="info-item">
                                    <label>Size</label>
                                    <span>${data.size}</span>
                                </div>
                                <div class="info-item">
                                    <label>Total Amount</label>
                                    <span class="amount">₱${parseFloat(data.total_amount).toFixed(2)}</span>
                                </div>
                                <div class="info-item">
                                    <label>Payment Method</label>
                                    <span>${data.payment_method}</span>
                                </div>
                            </div>
                        </div>

                        ${data.payment_method === 'GCASH' ? `
                            <div class="order-section payment-info">
                                <div class="section-header">
                                    <i class="fas fa-money-bill-wave"></i>
                                    <h5>Payment Information</h5>
                                </div>
                                <div class="info-grid">
                                    <div class="info-item">
                                        <label>GCash Reference</label>
                                        <span>${data.gcash_reference}</span>
                                    </div>
                                    ${data.payment_proof ? `
                                        <div class="info-item full-width">
                                            <label>Payment Proof</label>
                                            <div class="payment-proof-container">
                                                <img src="/static/${data.payment_proof}" 
                                                     alt="Payment Proof" 
                                                     class="payment-proof-image">
                                            </div>
                                        </div>
                                    ` : ''}
                                </div>
                            </div>
                        ` : ''}

                        <div class="order-section id-info">
                            <div class="section-header">
                                <i class="fas fa-id-card"></i>
                                <h5>Valid ID</h5>
                            </div>
                            ${data.valid_id_path ? `
                                <div class="valid-id-container">
                                    <img src="/static/${data.valid_id_path}" 
                                         alt="Valid ID" 
                                         class="valid-id-image">
                                </div>
                            ` : '<p class="text-muted">No valid ID uploaded</p>'}
                        </div>
                    </div>
                `;
            });
    });
});

// Handle reservation status update
document.querySelectorAll('.update-reservation').forEach(button => {
    button.addEventListener('click', function() {
        const reservationId = this.dataset.reservationId;
        document.getElementById('updateReservationId').value = reservationId;
    });
});

document.getElementById('confirmUpdateReservation').addEventListener('click', function() {
    const reservationId = document.getElementById('updateReservationId').value;
    const status = document.getElementById('reservationStatus').value;
    
    fetch(`/admin/update-reservation-status/${reservationId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: status })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error updating reservation status');
    });
});

// Handle reservation deletion
document.querySelectorAll('.delete-reservation').forEach(button => {
    button.addEventListener('click', function() {
        if (confirm('Are you sure you want to delete this reservation?')) {
            const reservationId = this.dataset.reservationId;
            
            fetch(`/admin/delete-reservation/${reservationId}`, {
                method: 'DELETE'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert(data.message);
                }
            });
        }
    });
});

// Handle reservation request info button click
document.querySelectorAll('.view-reservation-request').forEach(button => {
    button.addEventListener('click', function() {
        const requestId = this.dataset.requestId;
        
        fetch(`/admin/request-details/reservation/${requestId}`)
            .then(response => response.json())
            .then(data => {
                const details = document.getElementById('reservationRequestDetails');
                details.innerHTML = `
                    <div class="order-details-container">
                        <div class="order-section customer-info">
                            <div class="section-header">
                                <i class="fas fa-user-circle"></i>
                                <h5>Customer Information</h5>
                            </div>
                            <div class="info-grid">
                                <div class="info-item">
                                    <label>Name</label>
                                    <span>${data.customer_name}</span>
                                </div>
                                <div class="info-item">
                                    <label>Contact</label>
                                    <span>${data.contact_number}</span>
                                </div>
                                <div class="info-item full-width">
                                    <label>Address</label>
                                    <span>${data.address}</span>
                                </div>
                            </div>
                        </div>

                        <div class="order-section product-info">
                            <div class="section-header">
                                <i class="fas fa-tshirt"></i>
                                <h5>Product Information</h5>
                            </div>
                            <div class="info-grid">
                                <div class="info-item">
                                    <label>Product</label>
                                    <span>${data.product_name}</span>
                                </div>
                                <div class="info-item">
                                    <label>Size</label>
                                    <span>${data.size}</span>
                                </div>
                                <div class="info-item">
                                    <label>Total Amount</label>
                                    <span class="amount">₱${parseFloat(data.total_amount).toFixed(2)}</span>
                                </div>
                                <div class="info-item">
                                    <label>Payment Method</label>
                                    <span>${data.payment_method}</span>
                                </div>
                            </div>
                        </div>

                        ${data.payment_method === 'GCASH' ? `
                            <div class="order-section payment-info">
                                <div class="section-header">
                                    <i class="fas fa-money-bill-wave"></i>
                                    <h5>Payment Information</h5>
                                </div>
                                <div class="info-grid">
                                    <div class="info-item">
                                        <label>GCash Reference</label>
                                        <span>${data.gcash_reference}</span>
                                    </div>
                                    ${data.payment_proof ? `
                                        <div class="info-item full-width">
                                            <label>Payment Proof</label>
                                            <div class="payment-proof-container">
                                                <img src="/static/${data.payment_proof}" 
                                                     alt="Payment Proof" 
                                                     class="payment-proof-image">
                                            </div>
                                        </div>
                                    ` : ''}
                                </div>
                            </div>
                        ` : ''}

                        <div class="order-section id-info">
                            <div class="section-header">
                                <i class="fas fa-id-card"></i>
                                <h5>Valid ID</h5>
                            </div>
                            ${data.valid_id_path ? `
                                <div class="valid-id-container">
                                    <img src="/static/${data.valid_id_path}" 
                                         alt="Valid ID" 
                                         class="valid-id-image">
                                </div>
                            ` : '<p class="text-muted">No valid ID uploaded</p>'}
                        </div>
                    </div>
                `;
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error loading reservation request details');
            });
    });
});

// Handle appointment request status update
document.querySelectorAll('.update-appointment-request').forEach(button => {
    button.addEventListener('click', function() {
        const requestId = this.dataset.requestId;
        const status = this.dataset.status;
        const note = document.querySelector(`#note_${requestId}`).value || '';

        fetch(`/admin/update-request-status/appointment/${requestId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ status: status, note: note })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Remove the request row from the table
                const requestRow = document.querySelector(`tr[data-request-id="${requestId}"]`);
                if (requestRow) {
                    requestRow.remove();
                }
                
                // Reload the page to update the appointments table
                location.reload();
            } else {
                alert(data.message || 'Error updating request status');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error updating request status');
        });
    });
}); 