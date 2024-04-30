// Function to toggle the description of a resource
function toggleDescription(event) {
    const card = event.target.closest('.resource-card');
    const description = card.querySelector('.description');
    description.classList.toggle('show');
}

// Add event listeners to resource cards
const resourceCards = document.querySelectorAll('.resource-card');
resourceCards.forEach(card => {
    card.addEventListener('click', toggleDescription);
});