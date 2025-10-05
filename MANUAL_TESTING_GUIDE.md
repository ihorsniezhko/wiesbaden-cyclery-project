# Manual Testing Guide - Wiesbaden Cyclery

## Overview
This guide provides essential manual tests to verify critical functionality of the Wiesbaden Cyclery e-commerce platform.

**Estimated Time:** 30-45 minutes for complete testing

---

## Test 1: Product Browsing and Search

**Objective:** Verify users can browse and search for products

**Steps:**
1. Navigate to homepage
2. Click "Shop Now" or "Products" in navigation
3. Verify products are displayed with images, names, and prices
4. Use search bar to search for "bike"
5. Verify search results show relevant products
6. Click on a category filter (e.g., "Road Bikes")
7. Verify only products from that category are shown

**Expected Results:**
- ✅ Products display correctly with all information
- ✅ Search returns relevant results
- ✅ Category filtering works correctly
- ✅ Product images load properly

---

## Test 2: Product Detail View

**Objective:** Verify product detail pages show complete information

**Steps:**
1. From products page, click on any product
2. Verify product detail page loads
3. Check that all information is displayed:
   - Product name
   - Price
   - Description
   - Stock status
   - Rating (if available)
   - Size options (if applicable)
4. Verify "Add to Cart" button is present

**Expected Results:**
- ✅ Product detail page loads without errors
- ✅ All product information is visible
- ✅ Images display correctly
- ✅ Add to Cart button is functional

---

## Test 3: Add to Cart Functionality

**Objective:** Verify products can be added to shopping cart

**Steps:**
1. On product detail page, select quantity (e.g., 2)
2. If product has sizes, select a size
3. Click "Add to Cart" button
4. Verify success message appears
5. Check cart icon shows updated item count
6. Navigate to cart page
7. Verify product appears in cart with correct quantity

**Expected Results:**
- ✅ Product is added to cart successfully
- ✅ Success message displays
- ✅ Cart count updates correctly
- ✅ Cart page shows correct items and quantities

---

## Test 4: Shopping Cart Management

**Objective:** Verify cart can be updated and managed

**Steps:**
1. In shopping cart, update quantity of an item
2. Verify line total updates automatically
3. Verify cart subtotal updates
4. Verify delivery cost is calculated correctly:
   - €4.99 for orders under €50
   - Free for orders over €50
5. Remove an item from cart
6. Verify item is removed and totals update

**Expected Results:**
- ✅ Quantity updates work correctly
- ✅ Totals recalculate automatically
- ✅ Delivery cost calculation is correct
- ✅ Items can be removed successfully

---

## Test 5: User Registration and Login

**Objective:** Verify user authentication works correctly

**Steps:**
1. Click "Register" or "Sign Up"
2. Fill in registration form with valid data
3. Submit registration
4. Verify confirmation email is sent (check console in development)
5. Log out
6. Log in with registered credentials
7. Verify successful login and redirect to homepage

**Expected Results:**
- ✅ Registration form validates correctly
- ✅ User account is created successfully
- ✅ Login works with correct credentials
- ✅ User is redirected after login

---

## Test 6: Checkout Process (Without Payment)

**Objective:** Verify checkout form and order creation

**Steps:**
1. Add products to cart (total over €50 for free delivery)
2. Navigate to checkout
3. Fill in all required fields:
   - Full name
   - Email
   - Phone number
   - Address details
   - Country
4. Verify form validation works (try submitting with missing fields)
5. Verify order summary shows correct items and totals

**Expected Results:**
- ✅ Checkout page loads correctly
- ✅ Form validation works
- ✅ Order summary displays correctly
- ✅ All required fields are marked

---

## Test 7: Stripe Payment Integration

**Objective:** Verify Stripe payment processing works

**Steps:**
1. Complete checkout form
2. Enter Stripe test card: `4242 4242 4242 4242`
3. Enter any future expiry date (e.g., 12/25)
4. Enter any 3-digit CVC (e.g., 123)
5. Click "Complete Order"
6. Verify payment processes successfully
7. Verify redirect to order confirmation page
8. Verify order confirmation shows correct details

**Expected Results:**
- ✅ Stripe payment form loads correctly
- ✅ Test card is accepted
- ✅ Payment processes without errors
- ✅ Order confirmation page displays
- ✅ Order is created in database

---

## Test 8: Order History and Tracking

**Objective:** Verify users can view their order history

**Steps:**
1. Log in as a user who has placed orders
2. Navigate to "My Account" or "Order History"
3. Verify list of orders is displayed
4. Click on an order to view details
5. Verify order details are correct:
   - Order number
   - Date
   - Items
   - Totals
   - Status

**Expected Results:**
- ✅ Order history page loads
- ✅ All orders are listed
- ✅ Order details are accurate
- ✅ Order status is displayed correctly

---

## Test 9: Responsive Design

**Objective:** Verify site works on different screen sizes

**Steps:**
1. Open site in browser
2. Use browser dev tools to test different screen sizes:
   - Mobile (375px width)
   - Tablet (768px width)
   - Desktop (1920px width)
3. Verify navigation menu works on mobile (hamburger menu)
4. Verify product grid adjusts to screen size
5. Verify cart and checkout forms are usable on mobile

**Expected Results:**
- ✅ Site is responsive on all screen sizes
- ✅ Navigation works on mobile
- ✅ Content is readable and accessible
- ✅ Forms are usable on mobile devices

---

## Browser Compatibility Testing

Test the site in multiple browsers:
- ✅ Chrome/Edge (Chromium)
- ✅ Firefox
- ✅ Safari (if available)

---

## Test Data

### Test Credit Cards (Stripe Test Mode)
- **Success:** 4242 4242 4242 4242
- **Decline:** 4000 0000 0000 0002
- **Insufficient Funds:** 4000 0000 0000 9995

### Test User Credentials
- **Email:** test@example.com
- **Password:** testpass123

---

## Reporting Issues

When reporting issues, include:
1. Test number and name
2. Steps to reproduce
3. Expected vs actual result
4. Browser and device information
5. Screenshots if applicable

---

## Notes

- All tests should be performed in both development and production environments
- Payment tests should use Stripe test mode only
- Clear browser cache if experiencing unexpected behavior
- Check browser console for JavaScript errors
