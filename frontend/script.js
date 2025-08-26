// Bhai Jaan Academy Frontend JavaScript

// Import constants
import { ABOUT_TEXT } from './constants.js';

// Set about text content
document.getElementById('aboutText').innerHTML = ABOUT_TEXT;

// Video modal functionality
const demoButton = document.getElementById('demoButton');
const videoModal = document.getElementById('videoModal');
const closeModal = document.getElementById('closeModal');

// Show video modal
function showVideoModal() {
    videoModal.classList.remove('hidden');
    // Small delay to ensure DOM is ready for transition
    setTimeout(() => {
        videoModal.classList.add('show');
    }, 10);
}

// Hide video modal
function hideVideoModal() {
    videoModal.classList.remove('show');
    // Wait for transition to complete before hiding
    setTimeout(() => {
        videoModal.classList.add('hidden');
    }, 300);
}

// Event listeners
demoButton.addEventListener('click', showVideoModal);
closeModal.addEventListener('click', hideVideoModal);

// Close modal when clicking backdrop
videoModal.addEventListener('click', (e) => {
    if (e.target === videoModal) {
        hideVideoModal();
    }
});

// Close modal with Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !videoModal.classList.contains('hidden')) {
        hideVideoModal();
    }
});

// Configuration
const API_BASE_URL = 'https://bhai-jaan-academy.onrender.com'; // Production backend URL

// DOM Elements
const learningForm = document.getElementById('learningForm');
const emailInput = document.getElementById('email');
const topicInput = document.getElementById('topic');
const submitBtn = document.getElementById('submitBtn');
const submitText = document.getElementById('submitText');
const loadingText = document.getElementById('loadingText');
const successMessage = document.getElementById('successMessage');
const successText = document.getElementById('successText');
const errorMessage = document.getElementById('errorMessage');
const errorText = document.getElementById('errorText');
const emailError = document.getElementById('emailError');
const topicError = document.getElementById('topicError');

// Utility functions
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

// API communication for payment creation
async function createPayment(email, topic) {
    try {
        const response = await fetch(`${API_BASE_URL}/create-payment`, {
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

// API communication for payment verification
async function verifyPayment(paymentId, payerId) {
    try {
        const response = await fetch(`${API_BASE_URL}/verify-payment`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                payment_id: paymentId,
                payer_id: payerId
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

    // Show loading state
    submitBtn.disabled = true;
    submitText.classList.add('hidden');
    loadingText.classList.remove('hidden');
    showMessage('success', 'Creating payment... Please wait.');

    // Create payment
    const paymentResult = await createPayment(email, topic);
    
    console.log('Payment creation result:', paymentResult);
    
    if (paymentResult.success && paymentResult.data.success) {
        // Log the approval URL before redirecting
        console.log('Redirecting to PayPal approval URL:', paymentResult.data.approval_url);
        
        // Redirect to PayPal
        window.location.href = paymentResult.data.approval_url;
    } else {
        // Show error message
        const errorMessage = paymentResult.error || paymentResult.data.message || 'Payment creation failed. Please try again.';
        showMessage('error', errorMessage);
        
        // Reset form state
        submitBtn.disabled = false;
        submitText.classList.remove('hidden');
        loadingText.classList.add('hidden');
    }
}

// Event listeners
learningForm.addEventListener('submit', handleSubmit);

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

// Header expansion/collapse functionality
let isExpanded = false;
const headerElement = document.querySelector('.header-expandable');

function expandHeader() {
    if (!isExpanded) {
        headerElement.classList.add('expanded');
        isExpanded = true;
    }
}

function collapseHeader() {
    if (isExpanded) {
        headerElement.classList.remove('expanded');
        isExpanded = false;
    }
}

function toggleHeader(event) {
    event.preventDefault();
    if (isExpanded) {
        collapseHeader();  // Collapse on click/touch if already expanded
    } else {
        expandHeader();    // Expand on click/touch if collapsed
    }
}

// Desktop behavior (unchanged)
headerElement.addEventListener('mouseenter', expandHeader);
headerElement.addEventListener('mouseleave', collapseHeader);
headerElement.addEventListener('click', toggleHeader);

// Mobile touch handling with scroll detection
let touchStartTime = 0;
let touchStartX = 0;
let touchStartY = 0;

headerElement.addEventListener('touchstart', (e) => {
    touchStartTime = Date.now();
    touchStartX = e.touches[0].clientX;
    touchStartY = e.touches[0].clientY;
});

headerElement.addEventListener('touchend', (e) => {
    const touchEndTime = Date.now();
    const touchEndX = e.changedTouches[0].clientX;
    const touchEndY = e.changedTouches[0].clientY;
    
    const duration = touchEndTime - touchStartTime;
    const distance = Math.sqrt(
        Math.pow(touchEndX - touchStartX, 2) + 
        Math.pow(touchEndY - touchStartY, 2)
    );
    
    // Only toggle if it's a genuine tap (short duration, minimal movement)
    if (duration < 300 && distance < 10) {
        toggleHeader(e);
    }
});

// Handle payment success/cancel from URL parameters
function handlePaymentReturn() {
    const urlParams = new URLSearchParams(window.location.search);
    
    // Log ALL parameters to see what PayPal actually sends
    console.log('All URL parameters:', Object.fromEntries(urlParams.entries()));
    
    const paymentStatus = urlParams.get('payment');
    
    // Try multiple possible parameter names for payment ID
    const paymentId = urlParams.get('paymentId') || 
                     urlParams.get('token') || 
                     urlParams.get('PayerID') ||
                     urlParams.get('payment_id');
                     
    const payerId = urlParams.get('PayerID') || 
                    urlParams.get('payerId');
    
    console.log('Extracted paymentId:', paymentId);
    console.log('Extracted payerId:', payerId);
    console.log('Payment status:', paymentStatus);
    
    if (paymentStatus === 'success' && paymentId && payerId) {
        // Payment was successful, verify it
        showMessage('success', 'Payment successful! Processing payment, please DO NOT close this window...');
        
        verifyPayment(paymentId, payerId).then(result => {
            if (result.success && result.data.success) {
                showMessage('success', `We have successfully registered you! We will send you a learning plan when it's ready. You can close this page.`);
                learningForm.reset();
                submitBtn.disabled = true;
            } else {
                const errorMessage = result.error || result.data.message || 'Payment verification failed. Please try registering again.';
                showMessage('error', errorMessage);
            }
        }).catch(error => {
            showMessage('error', 'Payment verification failed. Please try registering again.');
        });
        
        // Clean up URL
        window.history.replaceState({}, document.title, window.location.pathname);
    } else if (paymentStatus === 'cancel') {
        // Payment was cancelled
        showMessage('error', 'Payment was cancelled. Please try registering again.');
        
        // Clean up URL
        window.history.replaceState({}, document.title, window.location.pathname);
    } else {
        // Log when parameters are missing
        console.log('Missing parameters:', {
            paymentStatus,
            paymentId,
            payerId,
            hasPaymentStatus: !!paymentStatus,
            hasPaymentId: !!paymentId,
            hasPayerId: !!payerId
        });
    }
}

// Add some nice animations on page load
document.addEventListener('DOMContentLoaded', () => {
    // Handle payment return
    handlePaymentReturn();
    
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