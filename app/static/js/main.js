document.addEventListener('DOMContentLoaded', function() {
    // Handle flash messages auto-hide
    const flashMessages = document.querySelectorAll('.alert');
    
    flashMessages.forEach(function(message) {
        setTimeout(function() {
            message.style.opacity = '0';
            setTimeout(function() {
                message.style.display = 'none';
            }, 500);
        }, 5000);
    });
    
    // Tab handling in the animal detail page
    const tabItems = document.querySelectorAll('.tab-item');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabItems.forEach(function(tab) {
        tab.addEventListener('click', function() {
            // Remove active class from all tabs
            tabItems.forEach(function(item) {
                item.classList.remove('active');
            });
            
            // Hide all tab contents
            tabContents.forEach(function(content) {
                content.style.display = 'none';
            });
            
            // Add active class to clicked tab
            this.classList.add('active');
            
            // Show the corresponding tab content
            const tabId = this.getAttribute('data-tab');
            document.getElementById(tabId).style.display = 'block';
        });
    });
    
    // Initialize the first tab as active if tabs exist
    if (tabItems.length > 0) {
        tabItems[0].click();
    }
    
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
            }
        });
    }
    
    // Helper function to show input errors
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
            input.parentNode.insertBefore(errorElement, input.nextSibling);
        }
        
        errorElement.textContent = message;
        
        // Clear error on input change
        input.addEventListener('input', function() {
            this.classList.remove('is-invalid');
            errorElement.textContent = '';
        }, { once: true });
    }
});