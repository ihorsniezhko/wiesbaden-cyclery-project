// Checkout Stripe Integration
console.log('🚀 External Stripe script loaded');

// Update debug info immediately
document.addEventListener('DOMContentLoaded', function() {
    const debugElement = document.getElementById('js-debug');
    if (debugElement) {
        debugElement.textContent = 'External JavaScript loaded ✅';
    }
    
    console.log('🔧 DOM loaded, starting Stripe initialization...');
    
    // Get keys from the page (they should be in script tags)
    const pkElement = document.getElementById('id_stripe_public_key');
    const csElement = document.getElementById('id_client_secret');
    
    if (!pkElement || !csElement) {
        console.error('❌ Stripe configuration script tags not found');
        if (debugElement) {
            debugElement.innerHTML += '<br>Config: ❌ Missing script tags';
        }
        return;
    }
    
    const publicKey = pkElement.textContent.slice(1, -1); // Remove quotes
    const clientSecret = csElement.textContent.slice(1, -1); // Remove quotes
    
    console.log('🔑 Keys extracted:', {
        pk: publicKey.substring(0, 20) + '...',
        cs: clientSecret.substring(0, 20) + '...'
    });
    
    // Update debug with actual values
    if (debugElement) {
        debugElement.innerHTML = 
            'External JavaScript loaded ✅<br>' +
            'PK: ' + (publicKey ? publicKey.substring(0, 20) + '...' : 'MISSING') + '<br>' +
            'CS: ' + (clientSecret ? clientSecret.substring(0, 20) + '...' : 'MISSING');
    }
    
    if (!publicKey || !publicKey.startsWith('pk_')) {
        console.error('❌ Invalid public key:', publicKey);
        document.getElementById('card-element').innerHTML = '<div style="padding: 10px; color: #dc3545;">Invalid payment configuration</div>';
        return;
    }
    
    if (!clientSecret || !clientSecret.startsWith('pi_')) {
        console.error('❌ Invalid client secret:', clientSecret);
        document.getElementById('card-element').innerHTML = '<div style="padding: 10px; color: #dc3545;">Payment intent not created</div>';
        return;
    }
    
    console.log('✅ Keys valid, waiting for Stripe library...');
    
    // Wait for Stripe to load
    function initStripe() {
        if (typeof Stripe === 'undefined') {
            console.log('⏳ Waiting for Stripe library to load...');
            setTimeout(initStripe, 100);
            return;
        }
        
        console.log('✅ Stripe library available, initializing...');
        
        try {
            const stripe = Stripe(publicKey);
            const elements = stripe.elements();
            const cardElement = elements.create('card', {
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
            
            cardElement.mount('#card-element');
            console.log('✅ Stripe Elements mounted successfully');
            
            // Update debug info
            if (debugElement) {
                debugElement.innerHTML += '<br>Stripe Elements: ✅';
            }
            
            // Handle card changes
            cardElement.on('change', function(event) {
                const displayError = document.getElementById('card-errors');
                if (event.error) {
                    displayError.textContent = event.error.message;
                    displayError.style.display = 'block';
                } else {
                    displayError.textContent = '';
                    displayError.style.display = 'none';
                }
            });
            
            // Handle form submission
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
                            card: cardElement,
                            billing_details: {
                                name: form.full_name.value,
                                email: form.email.value,
                            }
                        }
                    }).then(function(result) {
                        if (result.error) {
                            console.error('❌ Payment error:', result.error);
                            const errorElement = document.getElementById('card-errors');
                            errorElement.textContent = result.error.message;
                            errorElement.style.display = 'block';
                            
                            if (submitButton) {
                                submitButton.disabled = false;
                                submitButton.textContent = 'Complete Order';
                            }
                        } else {
                            console.log('✅ Payment successful:', result.paymentIntent);
                            // Submit the form to complete the order
                            form.submit();
                        }
                    });
                });
            }
            
        } catch (error) {
            console.error('❌ Stripe initialization error:', error);
            document.getElementById('card-element').innerHTML = '<div style="padding: 10px; color: #dc3545;">Failed to initialize: ' + error.message + '</div>';
            if (debugElement) {
                debugElement.innerHTML += '<br>Error: ' + error.message;
            }
        }
    }
    
    // Start initialization
    initStripe();
});