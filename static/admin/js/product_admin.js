/**
 * Django Admin JavaScript for Product model
 * Handles conditional visibility for stock quantity and sizes
 */

document.addEventListener('DOMContentLoaded', function() {
    // Stock Management Logic
    const inStockCheckbox = document.getElementById('id_in_stock');
    const stockQuantityField = document.querySelector('.field-stock_quantity');
    const stockQuantityInput = document.getElementById('id_stock_quantity');
    
    // Size Management Logic
    const hasSizesCheckbox = document.getElementById('id_has_sizes');
    const sizesField = document.querySelector('.field-sizes');
    const sizeCheckboxes = document.querySelectorAll('input[name="sizes"]');
    
    function toggleStockQuantityField() {
        if (inStockCheckbox && stockQuantityField) {
            if (inStockCheckbox.checked) {
                stockQuantityField.style.display = 'block';
                stockQuantityField.style.opacity = '1';
                if (stockQuantityInput) {
                    stockQuantityInput.required = true;
                    // Set minimum value if empty or zero
                    if (!stockQuantityInput.value || stockQuantityInput.value === '0') {
                        stockQuantityInput.value = '1';
                    }
                }
            } else {
                stockQuantityField.style.display = 'none';
                stockQuantityField.style.opacity = '0.5';
                if (stockQuantityInput) {
                    stockQuantityInput.required = false;
                    stockQuantityInput.value = '0';
                }
            }
        }
    }
    
    function toggleSizesField() {
        if (hasSizesCheckbox && sizesField) {
            if (hasSizesCheckbox.checked) {
                sizesField.style.display = 'block';
                sizesField.style.opacity = '1';
            } else {
                sizesField.style.display = 'none';
                sizesField.style.opacity = '0.5';
                // Clear all size selections
                sizeCheckboxes.forEach(cb => cb.checked = false);
            }
        }
    }
    
    function validateStockQuantity() {
        if (inStockCheckbox && inStockCheckbox.checked && stockQuantityInput) {
            const quantity = parseInt(stockQuantityInput.value);
            if (isNaN(quantity) || quantity <= 0) {
                stockQuantityInput.setCustomValidity('Stock quantity must be greater than 0 when product is in stock');
                return false;
            } else {
                stockQuantityInput.setCustomValidity('');
                return true;
            }
        }
        return true;
    }
    
    function checkSizeSelection() {
        if (hasSizesCheckbox && sizeCheckboxes.length > 0) {
            const anySizeSelected = Array.from(sizeCheckboxes).some(cb => cb.checked);
            if (anySizeSelected && !hasSizesCheckbox.checked) {
                hasSizesCheckbox.checked = true;
                toggleSizesField();
            } else if (!anySizeSelected && hasSizesCheckbox.checked) {
                // Don't auto-uncheck has_sizes in admin to prevent data loss
                // Just show a warning
                console.log('Warning: Has Sizes is enabled but no sizes are selected');
            }
        }
    }
    
    // Initial state
    toggleStockQuantityField();
    toggleSizesField();
    
    // Event listeners
    if (inStockCheckbox) {
        inStockCheckbox.addEventListener('change', toggleStockQuantityField);
    }
    
    if (stockQuantityInput) {
        stockQuantityInput.addEventListener('input', validateStockQuantity);
        stockQuantityInput.addEventListener('blur', validateStockQuantity);
    }
    
    if (hasSizesCheckbox) {
        hasSizesCheckbox.addEventListener('change', toggleSizesField);
    }
    
    sizeCheckboxes.forEach(cb => {
        cb.addEventListener('change', checkSizeSelection);
    });
    
    // Form validation before submit
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            if (!validateStockQuantity()) {
                e.preventDefault();
                alert('Stock quantity must be greater than 0 when product is in stock.');
                if (stockQuantityInput) {
                    stockQuantityInput.focus();
                }
                return false;
            }
        });
    }
    
    // Add visual indicators
    function addVisualIndicators() {
        // Add required indicator to stock quantity when in stock
        if (inStockCheckbox && stockQuantityField) {
            const label = stockQuantityField.querySelector('label');
            if (label && inStockCheckbox.checked) {
                if (!label.querySelector('.required-indicator')) {
                    const indicator = document.createElement('span');
                    indicator.className = 'required-indicator';
                    indicator.style.color = 'red';
                    indicator.textContent = ' *';
                    label.appendChild(indicator);
                }
            } else if (label) {
                const indicator = label.querySelector('.required-indicator');
                if (indicator) {
                    indicator.remove();
                }
            }
        }
    }
    
    // Update visual indicators when stock status changes
    if (inStockCheckbox) {
        inStockCheckbox.addEventListener('change', addVisualIndicators);
        addVisualIndicators(); // Initial state
    }
});