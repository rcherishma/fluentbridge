// ==================== UTILITY FUNCTIONS ====================

/**
 * Toggle dark mode and persist user preference.
 */
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    const enabled = document.body.classList.contains('dark-mode');
    localStorage.setItem('linguaDarkMode', enabled ? 'enabled' : 'disabled');
}

function loadDarkModePreference() {
    const stored = localStorage.getItem('linguaDarkMode');
    if (stored === 'enabled') {
        document.body.classList.add('dark-mode');
    }
}


/**
 * Initialize page animations
 * Adds fade-in effects to cards on page load
 */
document.addEventListener('DOMContentLoaded', function () {
    loadDarkModePreference();
    const cards = document.querySelectorAll('.language-card, .lesson-card, .feature-card');
    cards.forEach((card, index) => {
        card.style.animation = `slideUp 0.5s ease ${index * 0.05}s backwards`;
    });

});

/**
 * Shuffle array helper function
 * Used for randomizing quiz questions
 */
function shuffleArray(array) {
    let arr = [...array];
    for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
}

/**
 * Format percentage for display
 */
function formatPercentage(value) {
    return Math.round(value * 100) / 100;
}

/**
 * Show notification message
 */
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

console.log('FluentBridge - Professional Language Learning Platform Loaded');
