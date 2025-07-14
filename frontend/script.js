// Bhai Jaan Academy Frontend JavaScript

// Configuration
const API_BASE_URL = 'http://localhost:8000'; // Change this for production

// DOM Elements
const form = document.getElementById('learningForm');
const emailInput = document.getElementById('email');
const topicInput = document.getElementById('topic');
const submitBtn = document.getElementById('submitBtn');
const submitText = document.getElementById('submitText');
const loadingText = document.getElementById('loadingText');
const successMessage = document.getElementById('successMessage');
const errorMessage = document.getElementById('errorMessage');
const successText = document.getElementById('successText');
const errorText = document.getElementById('errorText');
const emailError = document.getElementById('emailError');
const topicError = document.getElementById('topicError');

// Utility functions
function showLoading() {
    submitBtn.disabled = true;
    submitText.classList.add('hidden');
    loadingText.classList.remove('hidden');
    submitBtn.classList.add('loading');
}

function hideLoading() {
    submitBtn.disabled = false;
    submitText.classList.remove('hidden');
    loadingText.classList.add('hidden');
    submitBtn.classList.remove('loading');
}

function showMessage(type, message) {
    // Hide all messages first
    successMessage.classList.add('hidden');
    errorMessage.classList.add('hidden');
    
    if (type === 'success') {
        successText.textContent = message;
        successMessage.classList.remove('hidden');
        successMessage.classList.add('success-message');
    } else {
        errorText.textContent = message;
        errorMessage.classList.remove('hidden');
        errorMessage.classList.add('error-message');
    }
}

function clearErrors() {
    emailError.classList.add('hidden');
    topicError.classList.add('hidden');
    emailInput.classList.remove('border-red-500');
    topicInput.classList.remove('border-red-500');
}

function showFieldError(field, message) {
    const errorElement = field === 'email' ? emailError : topicError;
    const inputElement = field === 'email' ? emailInput : topicInput;
    
    errorElement.textContent = message;
    errorElement.classList.remove('hidden');
    inputElement.classList.add('border-red-500');
}

// Validation functions
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function validateTopic(topic) {
    return topic.trim().length >= 3;
}

function validateForm() {
    clearErrors();
    let isValid = true;
    
    const email = emailInput.value.trim();
    const topic = topicInput.value.trim();
    
    // Email validation
    if (!email) {
        showFieldError('email', 'Email is required');
        isValid = false;
    } else if (!validateEmail(email)) {
        showFieldError('email', 'Please enter a valid email address');
        isValid = false;
    }
    
    // Topic validation
    if (!topic) {
        showFieldError('topic', 'Topic is required');
        isValid = false;
    } else if (!validateTopic(topic)) {
        showFieldError('topic', 'Topic must be at least 3 characters long');
        isValid = false;
    }
    
    return isValid;
}

// API communication
async function submitForm(email, topic) {
    try {
        const response = await fetch(`${API_BASE_URL}/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                topic: topic
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            return { success: true, data };
        } else {
            return { success: false, error: data.detail || 'An error occurred' };
        }
    } catch (error) {
        console.error('Network error:', error);
        return { success: false, error: 'Network error. Please check your connection.' };
    }
}

// Form submission handler
async function handleSubmit(event) {
    event.preventDefault();
    
    if (!validateForm()) {
        return;
    }
    
    const email = emailInput.value.trim();
    const topic = topicInput.value.trim();
    
    showLoading();
    
    try {
        const result = await submitForm(email, topic);
        
        if (result.success) {
            showMessage('success', result.data.message);
            // Clear form on success
            form.reset();
        } else {
            showMessage('error', result.error);
        }
    } catch (error) {
        showMessage('error', 'An unexpected error occurred. Please try again.');
    } finally {
        hideLoading();
    }
}

// Event listeners
form.addEventListener('submit', handleSubmit);

// Real-time validation
emailInput.addEventListener('blur', () => {
    const email = emailInput.value.trim();
    if (email && !validateEmail(email)) {
        showFieldError('email', 'Please enter a valid email address');
    } else {
        emailError.classList.add('hidden');
        emailInput.classList.remove('border-red-500');
    }
});

topicInput.addEventListener('blur', () => {
    const topic = topicInput.value.trim();
    if (topic && !validateTopic(topic)) {
        showFieldError('topic', 'Topic must be at least 3 characters long');
    } else {
        topicError.classList.add('hidden');
        topicInput.classList.remove('border-red-500');
    }
});

// Clear errors when user starts typing
emailInput.addEventListener('input', () => {
    if (emailError.classList.contains('hidden') === false) {
        emailError.classList.add('hidden');
        emailInput.classList.remove('border-red-500');
    }
});

topicInput.addEventListener('input', () => {
    if (topicError.classList.contains('hidden') === false) {
        topicError.classList.add('hidden');
        topicInput.classList.remove('border-red-500');
    }
});

// Health check on page load
window.addEventListener('load', async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/`);
        if (response.ok) {
            console.log('Backend is running');
        } else {
            console.warn('Backend health check failed');
        }
    } catch (error) {
        console.warn('Backend not available:', error.message);
    }
});

// Add some nice animations on page load
document.addEventListener('DOMContentLoaded', () => {
    // Animate form elements
    const formElements = document.querySelectorAll('#learningForm > div');
    formElements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            element.style.transition = 'all 0.5s ease';
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, index * 100);
    });
}); 