// CodeTantra Automation Frontend JavaScript

// API Base URL
const API_BASE = '/api';

// Utility functions
function showMessage(message, type = 'info') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `alert alert-${type}`;
    messageDiv.textContent = message;
    
    // Insert at top of page
    const container = document.querySelector('.container') || document.body;
    container.insertBefore(messageDiv, container.firstChild);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        messageDiv.remove();
    }, 5000);
}

function setLoading(button, loading = true) {
    if (loading) {
        button.disabled = true;
        button.dataset.originalText = button.textContent;
        button.textContent = 'Loading...';
    } else {
        button.disabled = false;
        button.textContent = button.dataset.originalText || button.textContent;
    }
}

// Registration form
document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(registerForm);
            const userData = {
                name: formData.get('name'),
                email: formData.get('email'),
                college_name: formData.get('college_name'),
                age: parseInt(formData.get('age')),
                password: formData.get('password'),
                referral_code: formData.get('referral_code') || null
            };
            
            const submitBtn = registerForm.querySelector('button[type="submit"]');
            setLoading(submitBtn, true);
            
            try {
                const response = await fetch(`${API_BASE}/auth/register`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(userData)
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    showMessage(result.message, 'success');
                    registerForm.reset();
                } else {
                    showMessage(result.detail || 'Registration failed', 'error');
                }
            } catch (error) {
                showMessage('Network error. Please try again.', 'error');
                console.error('Registration error:', error);
            } finally {
                setLoading(submitBtn, false);
            }
        });
    }
    
    // Login form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(loginForm);
            const credentials = {
                email: formData.get('email'),
                password: formData.get('password'),
                remember_me: formData.get('remember_me') === 'on'
            };
            
            const submitBtn = loginForm.querySelector('button[type="submit"]');
            setLoading(submitBtn, true);
            
            try {
                const response = await fetch(`${API_BASE}/auth/login`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(credentials)
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    // Store token
                    localStorage.setItem('auth_token', result.access_token);
                    localStorage.setItem('user_data', JSON.stringify(result.user));
                    
                    showMessage('Login successful! Redirecting...', 'success');
                    
                    // Redirect to dashboard
                    setTimeout(() => {
                        window.location.href = '/dashboard.html';
                    }, 1500);
                } else {
                    showMessage(result.detail || 'Login failed', 'error');
                }
            } catch (error) {
                showMessage('Network error. Please try again.', 'error');
                console.error('Login error:', error);
            } finally {
                setLoading(submitBtn, false);
            }
        });
    }
    
    // Forgot password form
    const forgotPasswordForm = document.getElementById('forgotPasswordForm');
    if (forgotPasswordForm) {
        forgotPasswordForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(forgotPasswordForm);
            const email = formData.get('email');
            
            const submitBtn = forgotPasswordForm.querySelector('button[type="submit"]');
            setLoading(submitBtn, true);
            
            try {
                const response = await fetch(`${API_BASE}/auth/forgot-password`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email })
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    showMessage(result.message, 'success');
                    forgotPasswordForm.reset();
                } else {
                    showMessage(result.detail || 'Request failed', 'error');
                }
            } catch (error) {
                showMessage('Network error. Please try again.', 'error');
                console.error('Forgot password error:', error);
            } finally {
                setLoading(submitBtn, false);
            }
        });
    }
    
    // Check if user is logged in
    const token = localStorage.getItem('auth_token');
    if (token && window.location.pathname === '/') {
        // Redirect to dashboard if already logged in
        window.location.href = '/dashboard.html';
    }
});

// Logout function
function logout() {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
    window.location.href = '/';
}

// Check authentication for protected pages
function checkAuth() {
    const token = localStorage.getItem('auth_token');
    if (!token) {
        window.location.href = '/';
        return false;
    }
    return true;
}

// Get user data
function getUserData() {
    const userData = localStorage.getItem('user_data');
    return userData ? JSON.parse(userData) : null;
}

// Make authenticated API calls
async function apiCall(endpoint, options = {}) {
    const token = localStorage.getItem('auth_token');
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` })
        }
    };
    
    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    });
    
    if (response.status === 401) {
        // Token expired, redirect to login
        logout();
        return null;
    }
    
    return response;
}
