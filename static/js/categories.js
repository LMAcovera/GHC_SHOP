document.addEventListener('DOMContentLoaded', function() {
    // Handle "View More" buttons
    const viewMoreButtons = document.querySelectorAll('.view-more-btn');
    
    viewMoreButtons.forEach(button => {
        button.addEventListener('click', function() {
            const categoryId = this.dataset.category;
            window.location.href = `/category/${categoryId}`;
        });
    });
}); 