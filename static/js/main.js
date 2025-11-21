/**
 * MET Articles - Main JavaScript File
 * Handles client-side interactions and enhancements
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeFileUpload();
    initializeFormValidation();
    initializeTooltips();
    initializeSearchEnhancements();
    initializeArticleInteractions();
    initializeDashboardFeatures();
});

/**
 * File Upload Enhancements
 */
function initializeFileUpload() {
    const fileInput = document.querySelector('input[type="file"]');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                validateFileUpload(file);
                updateFileUploadDisplay(file);
            }
        });

        // Drag and drop functionality
        const formContainer = fileInput.closest('.card-body');
        if (formContainer) {
            formContainer.addEventListener('dragover', function(e) {
                e.preventDefault();
                formContainer.classList.add('bg-light');
            });

            formContainer.addEventListener('dragleave', function(e) {
                e.preventDefault();
                formContainer.classList.remove('bg-light');
            });

            formContainer.addEventListener('drop', function(e) {
                e.preventDefault();
                formContainer.classList.remove('bg-light');
                
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    fileInput.files = files;
                    validateFileUpload(files[0]);
                    updateFileUploadDisplay(files[0]);
                }
            });
        }
    }
}

/**
 * Validate uploaded file
 */
function validateFileUpload(file) {
    const maxSize = 16 * 1024 * 1024; // 16MB
    const allowedTypes = ['application/pdf'];

    if (!allowedTypes.includes(file.type)) {
        showAlert('Please select a PDF file only.', 'danger');
        return false;
    }

    if (file.size > maxSize) {
        showAlert('File size must be less than 16MB.', 'danger');
        return false;
    }

    return true;
}

/**
 * Update file upload display
 */
function updateFileUploadDisplay(file) {
    const fileInput = document.querySelector('input[type="file"]');
    const feedback = document.createElement('div');
    feedback.className = 'mt-2 text-success small';
    feedback.innerHTML = `
        <i class="fas fa-check-circle me-1"></i>
        Selected: ${file.name} (${formatFileSize(file.size)})
    `;

    // Remove existing feedback
    const existingFeedback = fileInput.parentNode.querySelector('.text-success');
    if (existingFeedback) {
        existingFeedback.remove();
    }

    fileInput.parentNode.appendChild(feedback);
}

/**
 * Format file size in human readable format
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

/**
 * Form Validation Enhancements
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(form)) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });

        // Real-time validation
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(input);
            });
        });
    });
}

/**
 * Validate individual form field
 */
function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    let message = '';

    // Username validation
    if (field.name === 'username' && value) {
        if (value.length < 4) {
            isValid = false;
            message = 'Username must be at least 4 characters long.';
        } else if (!/^[a-zA-Z0-9_]+$/.test(value)) {
            isValid = false;
            message = 'Username can only contain letters, numbers, and underscores.';
        }
    }

    // Email validation
    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            message = 'Please enter a valid email address.';
        }
    }

    // Password validation
    if (field.type === 'password' && value) {
        if (value.length < 6) {
            isValid = false;
            message = 'Password must be at least 6 characters long.';
        }
    }

    // Show validation feedback
    updateFieldValidation(field, isValid, message);
    return isValid;
}

/**
 * Update field validation display
 */
function updateFieldValidation(field, isValid, message) {
    field.classList.remove('is-valid', 'is-invalid');
    
    // Remove existing feedback
    const existingFeedback = field.parentNode.querySelector('.invalid-feedback, .valid-feedback');
    if (existingFeedback && !existingFeedback.textContent.includes('error')) {
        existingFeedback.remove();
    }

    if (field.value.trim()) {
        if (isValid) {
            field.classList.add('is-valid');
        } else {
            field.classList.add('is-invalid');
            if (message) {
                const feedback = document.createElement('div');
                feedback.className = 'invalid-feedback';
                feedback.textContent = message;
                field.parentNode.appendChild(feedback);
            }
        }
    }
}

/**
 * Validate entire form
 */
function validateForm(form) {
    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!validateField(input)) {
            isValid = false;
        }
    });

    return isValid;
}

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"], [title]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        if (!tooltipTriggerEl.hasAttribute('data-bs-toggle')) {
            tooltipTriggerEl.setAttribute('data-bs-toggle', 'tooltip');
        }
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Search Enhancements
 */
function initializeSearchEnhancements() {
    const searchInput = document.querySelector('input[name="search"]');
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                // Auto-submit search after 500ms of inactivity
                if (this.value.length > 2 || this.value.length === 0) {
                    this.form.submit();
                }
            }, 500);
        });

        // Clear search button
        const clearBtn = document.createElement('button');
        clearBtn.type = 'button';
        clearBtn.className = 'btn btn-outline-secondary btn-sm ms-2';
        clearBtn.innerHTML = '<i class="fas fa-times"></i>';
        clearBtn.title = 'Clear search';
        clearBtn.addEventListener('click', function() {
            searchInput.value = '';
            searchInput.form.submit();
        });

        if (searchInput.value) {
            searchInput.parentNode.appendChild(clearBtn);
        }
    }
}

/**
 * Article Interactions
 */
function initializeArticleInteractions() {
    // Article card hover effects
    const articleCards = document.querySelectorAll('.article-card');
    articleCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Download tracking
    const downloadLinks = document.querySelectorAll('a[href*="/download/"]');
    downloadLinks.forEach(link => {
        link.addEventListener('click', function() {
            // Track download analytics (if needed)
            console.log('Article downloaded:', this.href);
        });
    });

    // Article sharing functionality
    if (navigator.share) {
        const shareButtons = document.querySelectorAll('.share-article');
        shareButtons.forEach(button => {
            button.addEventListener('click', function() {
                const articleTitle = this.dataset.title;
                const articleUrl = this.dataset.url;
                
                navigator.share({
                    title: articleTitle,
                    url: articleUrl
                });
            });
        });
    }
}

/**
 * Dashboard Features
 */
function initializeDashboardFeatures() {
    // Auto-refresh pending count
    const pendingBadges = document.querySelectorAll('.pending-count');
    if (pendingBadges.length > 0) {
        setInterval(updatePendingCount, 60000); // Check every minute
    }

    // Quick actions
    const quickActionButtons = document.querySelectorAll('.quick-action');
    quickActionButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Add loading state
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Loading...';
            this.disabled = true;

            // Restore after navigation
            setTimeout(() => {
                this.innerHTML = originalText;
                this.disabled = false;
            }, 1000);
        });
    });
}

/**
 * Update pending article count
 */
function updatePendingCount() {
    // This would typically make an AJAX call to get updated counts
    // For now, we'll just add a visual indicator that data is being refreshed
    const badges = document.querySelectorAll('.pending-count');
    badges.forEach(badge => {
        badge.style.opacity = '0.5';
        setTimeout(() => {
            badge.style.opacity = '1';
        }, 500);
    });
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info') {
    const alertContainer = document.querySelector('.container');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show mt-3`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    alertContainer.insertBefore(alert, alertContainer.firstChild);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

/**
 * Template download functionality
 */
function downloadTemplate() {
    // Download the official DOCX template from the static directory
    const a = document.createElement('a');
    a.href = '/static/MET_Articles_Template.docx';
    a.download = 'MET_Articles_Template.docx';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    showAlert('Template (DOCX) downloaded successfully!', 'success');
}

/**
 * Keyboard shortcuts
 */
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K for search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('input[name="search"]');
        if (searchInput) {
            searchInput.focus();
        }
    }

    // Escape to close modals
    if (e.key === 'Escape') {
        const openModal = document.querySelector('.modal.show');
        if (openModal) {
            const modal = bootstrap.Modal.getInstance(openModal);
            if (modal) {
                modal.hide();
            }
        }
    }
});

/**
 * Smooth scrolling for anchor links
 */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

/**
 * Form auto-save functionality (for article submission)
 */
function initializeAutoSave() {
    const articleForm = document.querySelector('form[enctype="multipart/form-data"]');
    if (articleForm && window.localStorage) {
        const formData = {};
        const inputs = articleForm.querySelectorAll('input[type="text"], textarea, select');
        
        // Load saved data
        inputs.forEach(input => {
            const savedValue = localStorage.getItem(`metarticles_${input.name}`);
            if (savedValue && !input.value) {
                input.value = savedValue;
            }
        });

        // Save data on input
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                localStorage.setItem(`metarticles_${this.name}`, this.value);
            });
        });

        // Clear saved data on successful submission
        articleForm.addEventListener('submit', function() {
            inputs.forEach(input => {
                localStorage.removeItem(`metarticles_${input.name}`);
            });
        });
    }
}

// Initialize auto-save
initializeAutoSave();

/**
 * Utility Functions
 */
window.MetArticles = {
    showAlert: showAlert,
    downloadTemplate: downloadTemplate,
    formatFileSize: formatFileSize
};
