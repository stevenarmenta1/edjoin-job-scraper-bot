//  JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Page loaded!');
    
    // Add interactivity here
    const jobCards = document.querySelectorAll('.job-card');
    jobCards.forEach(card => {
        card.addEventListener('click', function() {
            console.log('Job clicked!');
        });
    });
});