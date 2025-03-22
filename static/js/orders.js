// View Order Details
function viewOrderDetails(orderId) {
    fetch(`/order-details/${orderId}`)
        .then(response => response.json())
        .then(data => {
            const modalContent = document.getElementById('modalContent');
            modalContent.innerHTML = generateOrderDetailsHTML(data);
            new bootstrap.Modal(document.getElementById('detailsModal')).show();
        })
        .catch(error => console.error('Error:', error));
}

// View Request Details
function viewRequestDetails(requestId) {
    fetch(`/request-details/${requestId}`)
        .then(response => response.json())
        .then(data => {
            const modalContent = document.getElementById('modalContent');
            modalContent.innerHTML = generateRequestDetailsHTML(data);
            new bootstrap.Modal(document.getElementById('detailsModal')).show();
        })
        .catch(error => console.error('Error:', error));
}

// View Rental Details
function viewRentalDetails(rentalId) {
    fetch(`/rental-details/${rentalId}`)
        .then(response => response.json())
        .then(data => {
            const modalContent = document.getElementById('modalContent');
            modalContent.innerHTML = generateRentalDetailsHTML(data);
            new bootstrap.Modal(document.getElementById('detailsModal')).show();
        })
        .catch(error => console.error('Error:', error));
}

// Generate HTML for different types of details
function generateOrderDetailsHTML(order) {
    return `
        <div class="details-container">
            <div class="row">
                <div class="col-md-6">
                    <h6>Order Information</h6>
                    <p><strong>Order ID:</strong> #${order.order_id}</p>
                    <p><strong>Date:</strong> ${formatDate(order.created_at)}</p>
                    <p><strong>Status:</strong> <span class="badge bg-${order.status_color}">${order.order_status}</span></p>
                    <p><strong>Total Amount:</strong> ₱${order.total_amount}</p>
                </div>
                <div class="col-md-6">
                    <h6>Shipping Information</h6>
                    <p><strong>Name:</strong> ${order.full_name}</p>
                    <p><strong>Contact:</strong> ${order.contact_number}</p>
                    <p><strong>Address:</strong> ${order.complete_address}</p>
                </div>
            </div>
        </div>
    `;
}

function generateRequestDetailsHTML(request) {
    return `
        <div class="details-container">
            <div class="row">
                <div class="col-md-6">
                    <h6>Request Information</h6>
                    <p><strong>Request ID:</strong> #${request.request_id}</p>
                    <p><strong>Date:</strong> ${formatDate(request.created_at)}</p>
                    <p><strong>Status:</strong> <span class="badge bg-${request.status_color}">${request.status}</span></p>
                    <p><strong>Rental Days:</strong> ${request.rental_days}</p>
                </div>
                <div class="col-md-6">
                    <h6>Contact Information</h6>
                    <p><strong>Name:</strong> ${request.full_name}</p>
                    <p><strong>Contact:</strong> ${request.contact_number}</p>
                    <p><strong>Address:</strong> ${request.address}</p>
                </div>
            </div>
            ${request.status_note ? `
                <div class="mt-3">
                    <h6>Status Note</h6>
                    <p>${request.status_note}</p>
                </div>
            ` : ''}
        </div>
    `;
}

function generateRentalDetailsHTML(rental) {
    return `
        <div class="details-container">
            <div class="row">
                <div class="col-md-6">
                    <h6>Rental Information</h6>
                    <p><strong>Rental ID:</strong> #${rental.rental_id}</p>
                    <p><strong>Date:</strong> ${formatDate(rental.created_at)}</p>
                    <p><strong>Status:</strong> <span class="badge bg-${rental.status_color}">${rental.status}</span></p>
                    <p><strong>Total Amount:</strong> ₱${rental.total_amount}</p>
                </div>
                <div class="col-md-6">
                    <h6>Rental Period</h6>
                    <p><strong>Start Date:</strong> ${formatDate(rental.start_date)}</p>
                    <p><strong>End Date:</strong> ${formatDate(rental.end_date)}</p>
                    <p><strong>Days:</strong> ${rental.rental_days}</p>
                </div>
            </div>
        </div>
    `;
}

function generateReservationDetailsHTML(reservation) {
    return `
        <div class="details-container">
            <div class="row">
                <div class="col-md-6">
                    <h6>Reservation Information</h6>
                    <p><strong>Reservation ID:</strong> #${reservation.reservation_id}</p>
                    <p><strong>Date:</strong> ${formatDate(reservation.created_at)}</p>
                    <p><strong>Status:</strong> <span class="badge bg-${reservation.status_color}">${reservation.status}</span></p>
                    <p><strong>Total Amount:</strong> ₱${reservation.total_amount}</p>
                </div>
                <div class="col-md-6">
                    <h6>Contact Information</h6>
                    <p><strong>Name:</strong> ${reservation.full_name}</p>
                    <p><strong>Contact:</strong> ${reservation.contact_number}</p>
                    <p><strong>Address:</strong> ${reservation.address}</p>
                </div>
            </div>
        </div>
    `;
}

// Helper function to format dates
function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
} 