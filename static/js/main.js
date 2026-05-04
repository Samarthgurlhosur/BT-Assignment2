// Main JavaScript for Land Registration System

// Initialize Socket.IO connection
const socket = io();

// Socket event handlers
socket.on('connect', () => {
    console.log('Connected to server');
});

socket.on('connected', (data) => {
    console.log('User connected:', data);
});

socket.on('new_offer', (data) => {
    console.log('New offer received:', data);
    showNotification(`New offer: $${data.offer.offered_price}`, 'success');
});

socket.on('offer_response', (data) => {
    console.log('Offer response:', data);
    showNotification(`Offer ${data.status}`, 'info');
});

socket.on('new_message', (data) => {
    console.log('New message:', data);
    displayChatMessage(data.sender_name, data.message, data.timestamp);
});

socket.on('price_offer', (data) => {
    console.log('Price offer:', data);
});

socket.on('negotiation_joined', (data) => {
    console.log('Negotiation room joined:', data);
    showNotification(`${data.username} joined the negotiation`, 'info');
});

// Utility Functions

/**
 * Show notification to user
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.top = '80px';
    notification.style.right = '20px';
    notification.style.zIndex = '1000';
    notification.style.minWidth = '300px';

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}

/**
 * Format currency
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

/**
 * Format date
 */
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

/**
 * Display chat message
 */
function displayChatMessage(sender, message, timestamp) {
    const messagesContainer = document.getElementById('messages-list');
    if (messagesContainer) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message';
        messageElement.innerHTML = `
            <strong>${sender}</strong> <small>${formatDate(timestamp)}</small>
            <p>${message}</p>
        `;
        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}

/**
 * Start negotiation for a land
 */
function startNegotiation(landId) {
    socket.emit('join_negotiation', { land_id: landId });
    showNotification(`Joined negotiation for land ${landId}`, 'success');
}

/**
 * Send negotiation message
 */
function sendNegotiationMessage(landId, receiverId, message) {
    socket.emit('send_message', {
        land_id: landId,
        receiver_id: receiverId,
        message: message
    });
}

/**
 * Send price offer
 */
function sendPriceOffer(landId, price) {
    socket.emit('send_offer', {
        land_id: landId,
        offered_price: price
    });
}

/**
 * Fetch with error handling
 */
async function fetchData(url, options = {}) {
    try {
        const response = await fetch(url, options);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Fetch error:', error);
        showNotification('An error occurred. Please try again.', 'error');
        return null;
    }
}

/**
 * Post data
 */
async function postData(url, data) {
    return fetchData(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    });
}

/**
 * Put data
 */
async function putData(url, data) {
    return fetchData(url, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    });
}

/**
 * Delete data
 */
async function deleteData(url) {
    return fetchData(url, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        }
    });
}

/**
 * Validate email
 */
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Validate form
 */
function validateForm(formData) {
    const errors = [];

    for (const [key, value] of Object.entries(formData)) {
        if (value === null || value === undefined || value === '') {
            errors.push(`${key} is required`);
        }
    }

    return errors;
}

/**
 * Display errors
 */
function displayErrors(errors) {
    const errorContainer = document.getElementById('errors');
    if (errorContainer) {
        errorContainer.innerHTML = errors
            .map(error => `<div class="alert alert-error">${error}</div>`)
            .join('');
    }
}

/**
 * Clear errors
 */
function clearErrors() {
    const errorContainer = document.getElementById('errors');
    if (errorContainer) {
        errorContainer.innerHTML = '';
    }
}

/**
 * Format file size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Copy to clipboard
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard', 'success');
    }).catch(() => {
        showNotification('Failed to copy to clipboard', 'error');
    });
}

/**
 * Generate UUID
 */
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        const r = Math.random() * 16 | 0,
            v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

/**
 * Initialize date picker
 */
function initDatePicker(element) {
    if (element) {
        element.type = 'date';
    }
}

/**
 * Parse query parameters from URL
 */
function getQueryParams() {
    const params = new URLSearchParams(window.location.search);
    const obj = {};

    for (const [key, value] of params) {
        obj[key] = value;
    }

    return obj;
}

/**
 * Check if user is authenticated
 */
async function checkAuthentication() {
    try {
        const response = await fetch('/api/user/profile');
        return response.ok;
    } catch {
        return false;
    }
}

/**
 * Redirect to login if not authenticated
 */
async function requireAuth() {
    const isAuth = await checkAuthentication();
    if (!isAuth) {
        window.location.href = '/login';
    }
}

/**
 * Initialize tooltips
 */
function initTooltips() {
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(element => {
        const tooltip = element.getAttribute('data-tooltip');
        element.title = tooltip;
    });
}

/**
 * Debounce function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Validate phone number
 */
function validatePhoneNumber(phone) {
    const phoneRegex = /^\d{10}$/;
    return phoneRegex.test(phone.replace(/\D/g, ''));
}

/**
 * Format phone number
 */
function formatPhoneNumber(phone) {
    const cleaned = ('' + phone).replace(/\D/g, '');
    const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/);
    if (match) {
        return '(' + match[1] + ') ' + match[2] + '-' + match[3];
    }
    return phone;
}

/**
 * Page initialization
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log('Page loaded');
    initTooltips();

    // Check authentication for protected pages
    const protectedPages = ['/dashboard', '/owner_dashboard', '/buyer_dashboard'];
    if (protectedPages.some(page => window.location.href.includes(page))) {
        checkAuthentication();
    }
});

// Export functions for use in other files
window.API = {
    fetchData,
    postData,
    putData,
    deleteData,
    showNotification,
    formatCurrency,
    formatDate,
    validateEmail,
    validateForm,
    formatFileSize,
    copyToClipboard,
    startNegotiation,
    sendNegotiationMessage,
    sendPriceOffer
};
