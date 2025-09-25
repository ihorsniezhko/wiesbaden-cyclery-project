// Minimal Stripe Implementation
console.log('🚀 Minimal Stripe script starting...');

// Function to wait for Stripe to be available
function waitForStripe(callback, maxAttempts = 50) {
    let attempts = 0;
    
    function checkStripe() {
        attempts++;
        console.log(`🔍 Checking for Stripe (attempt ${attempts}/${maxAttempts})...`);
        
        if (typeof Stripe !== 'undefined') {
            console.log('✅ Stripe is available!');
            callback();
        } else if (attempts < maxAttempts) {
            console.log('⏳ Stripe not ready yet, waiting...');
            setTimeout(checkStripe, 200);
        } else {
            console.error('❌ Stripe failed to load after maximum attempts');
            const cardContainer = document.getElementById('card-element');
            if (cardContainer) {
                cardContainer.innerHTML = '<div style="padding: 10px; color: #dc3545;">Payment system failed to load. Please refresh the page.</div>';
            }
        }
    }
    
    checkStripe();
}

// Simple function to initialize Stripe
function initStripe() {
    console.log('🔧 initStripe called');
    
    // Get the elements we need
    const cardContainer = document.getElementById('card-element');
    const errorContainer = document.getElementById('card-errors');
    
    if (!cardContainer) {
        console.error('❌ Card container not found');
        return;
    }
    
    // Show loading
    cardContainer.innerHTML = '<div style="padding: 10px; color: #666;">Initializing payment form...</div>';
    
    // Get Stripe keys from script tags
    const pkElement = document.getElementById('id_stripe_public_key');
    const csElement = document.getElementById('id_client_secret');
    
    if (!pkElement || !csElement) {
        console.error('❌ Stripe configuration not found');
        cardContainer.innerHTML = '<div style="padding: 10px; color: #dc3545;">Payment configuration missing</div>';
        return;
    }
    
    const publicKey = pkElement.textContent.slice(1, -1);
    const clientSecret = csElement.textContent.slice(1, -1);
    
    console.log('🔑 Keys found:', {
        pk: publicKey.substring(0, 10) + '...',
        cs: clientSecret.substring(0, 10) + '...'
    });
    
    if (!publicKey || !clientSecret) {
        console.error('❌ Invalid keys');
        cardContainer.innerHTML = '<div style="padding: 10px; color: #dc3545;">Invalid payment configuration</div>';
        return;
    }
    
    // Stripe should be available at this point since we waited for it
    if (typeof Stripe === 'undefined') {
        console.error('❌ Stripe still not loaded after waiting');
        cardContainer.innerHTML = '<div style="padding: 10px; color: #dc3545;">Payment system not loaded</div>';
        return;
    }
    
    try {
        // Create Stripe instance
        const stripe = Stripe(publicKey);
        const elements = stripe.elements();
        
        // Create card element
        const card = elements.create('card', {
            hidePostalCode: true,
            style: {
                base: {
                    fontSize: '16px',
                    color: '#000',
                    '::placeholder': {
                        color: '#aab7c4'
                    }
                }
            }
        });
        
        // Clear container and mount
        cardContainer.innerHTML = '';
        card.mount('#card-element');
        
        console.log('✅ Card mounted successfully');
        
        // Handle changes
        card.on('change', function(event) {
            if (event.error) {
                errorContainer.textContent = event.error.message;
                errorContainer.style.display = 'block';
            } else {
                errorContainer.textContent = '';
                errorContainer.style.display = 'none';
            }
        });
        
        // Store references globally for form submission
        window.stripeCard = card;
        window.stripeInstance = stripe;
        window.stripeClientSecret = clientSecret;
        
        // Add form submission handler
        const form = document.getElementById('payment-form');
        if (form) {
            form.addEventListener('submit', function(event) {
                event.preventDefault();
                console.log('📤 Form submission intercepted');
                
                const submitButton = document.getElementById('submit-button');
                if (submitButton) {
                    submitButton.disabled = true;
                    submitButton.textContent = 'Processing...';
                }
                
                stripe.confirmCardPayment(clientSecret, {
                    payment_method: {
                        card: card,
                        billing_details: {
                            name: form.full_name.value,
                            email: form.email.value,
                        }
                    }
                }).then(function(result) {
                    if (result.error) {
                        console.error('❌ Payment error:', result.error);
                        errorContainer.textContent = result.error.message;
                        errorContainer.style.display = 'block';
                        
                        if (submitButton) {
                            submitButton.disabled = false;
                            submitButton.textContent = 'Complete Order';
                        }
                    } else {
                        console.log('✅ Payment successful');
                        form.submit();
                    }
                });
            });
        }
        
        console.log('✅ Stripe initialization complete');
        
    } catch (error) {
        console.error('❌ Stripe initialization error:', error);
        cardContainer.innerHTML = '<div style="padding: 10px; color: #dc3545;">Failed to initialize: ' + error.message + '</div>';
    }
}

// Wait for everything to be ready
function waitForReady() {
    console.log('⏳ Waiting for ready state...');
    
    if (document.readyState === 'complete') {
        console.log('✅ Document complete, waiting for Stripe...');
        waitForStripe(initStripe);
    } else {
        console.log('⏳ Document not ready, waiting...');
        setTimeout(waitForReady, 100);
    }
}

// Start the process
waitForReady();