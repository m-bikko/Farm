document.addEventListener('DOMContentLoaded', function() {
    // Add animation classes to elements as they enter viewport
    const animateOnScroll = function() {
        const animatableElements = document.querySelectorAll('.card, .animal-info, .table, form');
        
        animatableElements.forEach(function(element) {
            const elementPosition = element.getBoundingClientRect().top;
            const screenPosition = window.innerHeight;
            
            if (elementPosition < screenPosition - 50) {
                element.classList.add('animate-in');
            }
        });
    };
    
    // Call once on page load
    animateOnScroll();
    
    // Call on scroll
    window.addEventListener('scroll', animateOnScroll);
    
    // Handle flash messages with enhanced animations
    const flashMessages = document.querySelectorAll('.alert');
    
    flashMessages.forEach(function(message, index) {
        // Staggered appearance
        message.style.animationDelay = (index * 0.2) + 's';
        
        // Dismiss on click
        message.addEventListener('click', function() {
            dismissAlert(message);
        });
        
        // Auto-dismiss after delay
        setTimeout(function() {
            dismissAlert(message);
        }, 5000 + (index * 500));
    });
    
    function dismissAlert(alert) {
        alert.style.opacity = '0';
        alert.style.transform = 'translateX(30px)';
        setTimeout(function() {
            alert.style.display = 'none';
        }, 500);
    }
    
    // Enhanced tab handling with animations
    const tabItems = document.querySelectorAll('.tab-item');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabItems.forEach(function(tab) {
        tab.addEventListener('click', function() {
            // Don't do anything if this tab is already active
            if (this.classList.contains('active')) return;
            
            // Remove active class from all tabs
            tabItems.forEach(function(item) {
                item.classList.remove('active');
            });
            
            // Hide all tab contents with animation
            tabContents.forEach(function(content) {
                content.classList.remove('tab-content-active');
                content.classList.add('tab-content-inactive');
                setTimeout(function() {
                    content.style.display = 'none';
                }, 300); // Match with CSS transition time
            });
            
            // Add active class to clicked tab
            this.classList.add('active');
            
            // Show the corresponding tab content with animation
            const tabId = this.getAttribute('data-tab');
            const activeContent = document.getElementById(tabId);
            
            setTimeout(function() {
                activeContent.style.display = 'block';
                // Trigger reflow
                void activeContent.offsetWidth;
                activeContent.classList.remove('tab-content-inactive');
                activeContent.classList.add('tab-content-active');
            }, 300);
        });
    });
    
    // Initialize the first tab as active if tabs exist
    if (tabItems.length > 0) {
        tabItems[0].click();
    }
    
    // Card hover effects enhancement
    const cards = document.querySelectorAll('.card');
    cards.forEach(function(card) {
        card.addEventListener('mouseenter', function(e) {
            const cardRect = card.getBoundingClientRect();
            const mouseX = e.clientX - cardRect.left;
            const mouseY = e.clientY - cardRect.top;
            
            // Calculate rotations based on mouse position (subtle effect)
            const rotateY = ((mouseX / cardRect.width) - 0.5) * 5; // -2.5 to 2.5 degrees
            const rotateX = ((mouseY / cardRect.height) - 0.5) * -5; // 2.5 to -2.5 degrees
            
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-5px)`;
        });
        
        card.addEventListener('mouseleave', function() {
            card.style.transform = '';
        });
    });
    
    // Form field focus animations
    const formInputs = document.querySelectorAll('input, textarea, select');
    formInputs.forEach(function(input) {
        const formGroup = input.closest('.form-group');
        
        input.addEventListener('focus', function() {
            if (formGroup) {
                formGroup.classList.add('focused');
            }
        });
        
        input.addEventListener('blur', function() {
            if (formGroup) {
                formGroup.classList.remove('focused');
            }
        });
    });
    
    // Date input fields - set max date to today
    const dateInputs = document.querySelectorAll('input[type="date"]');
    const today = new Date().toISOString().split('T')[0];
    
    dateInputs.forEach(function(input) {
        if (!input.hasAttribute('max')) {
            input.setAttribute('max', today);
        }
    });
    
    // Animal form validation
    const animalForm = document.getElementById('animal-form');
    if (animalForm) {
        animalForm.addEventListener('submit', function(event) {
            const tagInput = document.getElementById('animal_tag_id');
            const speciesInput = document.getElementById('species');
            const birthDateInput = document.getElementById('birth_date');
            
            let isValid = true;
            
            if (!tagInput.value.trim()) {
                showInputError(tagInput, 'Animal Tag ID is required');
                isValid = false;
            } else if (!/^[A-Za-z0-9\-]+$/.test(tagInput.value.trim())) {
                showInputError(tagInput, 'Animal Tag ID should only contain letters, numbers, and hyphens');
                isValid = false;
            }
            
            if (!speciesInput.value.trim()) {
                showInputError(speciesInput, 'Species is required');
                isValid = false;
            }
            
            if (!birthDateInput.value) {
                showInputError(birthDateInput, 'Birth date is required');
                isValid = false;
            }
            
            if (!isValid) {
                event.preventDefault();
                // Shake the form on validation error
                animalForm.classList.add('shake-animation');
                setTimeout(function() {
                    animalForm.classList.remove('shake-animation');
                }, 500);
            }
        });
    }
    
    // Feeding log form validation
    const feedingForm = document.getElementById('feeding-form');
    if (feedingForm) {
        feedingForm.addEventListener('submit', function(event) {
            const feedTypeInput = document.getElementById('feed_type');
            const quantityInput = document.getElementById('quantity_kg');
            
            let isValid = true;
            
            if (!feedTypeInput.value.trim()) {
                showInputError(feedTypeInput, 'Feed type is required');
                isValid = false;
            }
            
            if (!quantityInput.value.trim()) {
                showInputError(quantityInput, 'Quantity is required');
                isValid = false;
            } else if (isNaN(quantityInput.value) || parseFloat(quantityInput.value) <= 0) {
                showInputError(quantityInput, 'Quantity must be a positive number');
                isValid = false;
            }
            
            if (!isValid) {
                event.preventDefault();
                // Shake the form on validation error
                feedingForm.classList.add('shake-animation');
                setTimeout(function() {
                    feedingForm.classList.remove('shake-animation');
                }, 500);
            }
        });
    }
    
    // Health record form validation
    const healthForm = document.getElementById('health-form');
    if (healthForm) {
        healthForm.addEventListener('submit', function(event) {
            const behaviorInput = document.getElementById('behavior_observation');
            const weightInput = document.getElementById('weight_kg');
            const tempInput = document.getElementById('temperature_celsius');
            
            let isValid = true;
            
            if (!behaviorInput.value.trim()) {
                showInputError(behaviorInput, 'Behavior observation is required');
                isValid = false;
            }
            
            if (weightInput.value.trim() && (isNaN(weightInput.value) || parseFloat(weightInput.value) <= 0)) {
                showInputError(weightInput, 'Weight must be a positive number');
                isValid = false;
            }
            
            if (tempInput.value.trim() && (isNaN(tempInput.value) || parseFloat(tempInput.value) < 30 || parseFloat(tempInput.value) > 45)) {
                showInputError(tempInput, 'Temperature must be a reasonable value (30-45°C)');
                isValid = false;
            }
            
            if (!isValid) {
                event.preventDefault();
                // Shake the form on validation error
                healthForm.classList.add('shake-animation');
                setTimeout(function() {
                    healthForm.classList.remove('shake-animation');
                }, 500);
            }
        });
    }
    
    // Enhanced error message display with animation
    function showInputError(input, message) {
        input.classList.add('is-invalid');
        
        // Check if error message element already exists
        let errorElement = input.nextElementSibling;
        if (!errorElement || !errorElement.classList.contains('error-message')) {
            errorElement = document.createElement('div');
            errorElement.className = 'error-message';
            errorElement.style.color = 'red';
            errorElement.style.fontSize = '0.8rem';
            errorElement.style.marginTop = '4px';
            errorElement.style.opacity = '0';
            errorElement.style.transform = 'translateY(-10px)';
            errorElement.style.transition = 'all 0.3s ease';
            input.parentNode.insertBefore(errorElement, input.nextSibling);
            
            // Trigger animation
            setTimeout(function() {
                errorElement.style.opacity = '1';
                errorElement.style.transform = 'translateY(0)';
            }, 10);
        }
        
        errorElement.textContent = message;
        
        // Clear error on input change with animation
        input.addEventListener('input', function() {
            this.classList.remove('is-invalid');
            errorElement.style.opacity = '0';
            errorElement.style.transform = 'translateY(-10px)';
            setTimeout(function() {
                errorElement.textContent = '';
            }, 300);
        }, { once: true });
    }
    
    // Add ripple effect to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            const rect = button.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const ripple = document.createElement('span');
            ripple.className = 'ripple-effect';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            
            button.appendChild(ripple);
            
            setTimeout(function() {
                ripple.remove();
            }, 600);
        });
    });
});