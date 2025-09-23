"""
Views for products app
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q, Avg
from django.core.paginator import Paginator

from .models import Product, Category, Size, Review
from .forms import ReviewForm


def all_products(request):
    """A view to show all products, including sorting and search queries"""
    
    # Performance optimization: select_related for foreign keys
    products = Product.objects.select_related('category').filter(in_stock=True)
    query = None
    categories = None
    sort = None
    direction = None

    if request.GET:
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'name':
                sortkey = 'lower_name'
                products = products.extra(select={'lower_name': 'lower(name)'})
            if sortkey == 'category':
                sortkey = 'category__name'
            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            products = products.order_by(sortkey)

        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            products = products.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect('products')
            
            queries = Q(name__icontains=query) | Q(description__icontains=query)
            products = products.filter(queries)

    # Pagination
    paginator = Paginator(products, 12)  # Show 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    current_sorting = f'{sort}_{direction}'

    context = {
        'products': page_obj,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
        'page_obj': page_obj,
    }

    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    """A view to show individual product details"""
    
    # Performance optimization: select_related and prefetch_related
    product = get_object_or_404(
        Product.objects.select_related('category').prefetch_related('sizes', 'reviews__user'), 
        pk=product_id
    )
    
    # Get related products from the same category with optimization
    related_products = Product.objects.select_related('category').filter(
        category=product.category,
        in_stock=True
    ).exclude(pk=product.pk)[:4]
    
    # Get reviews for this product
    reviews = Review.objects.filter(product=product).order_by('-created_at')
    
    # Calculate average rating
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    if avg_rating:
        avg_rating = round(avg_rating, 1)
    
    # Check if user has already reviewed this product
    user_has_reviewed = False
    if request.user.is_authenticated:
        user_has_reviewed = Review.objects.filter(
            product=product, 
            user=request.user
        ).exists()
    
    # Initialize review form
    review_form = ReviewForm()

    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'user_has_reviewed': user_has_reviewed,
        'review_form': review_form,
    }

    return render(request, 'products/product_detail.html', context)


@login_required
def add_review(request, product_id):
    """Add a review for a product"""
    
    product = get_object_or_404(Product, pk=product_id)
    
    # Check if user has already reviewed this product
    if Review.objects.filter(product=product, user=request.user).exists():
        messages.error(request, 'You have already reviewed this product.')
        return redirect('product_detail', product_id=product_id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            
            # Update product rating
            avg_rating = Review.objects.filter(product=product).aggregate(
                Avg('rating')
            )['rating__avg']
            product.rating = round(avg_rating, 1)
            product.save()
            
            messages.success(request, 'Your review has been added successfully!')
            return redirect('product_detail', product_id=product_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    
    return redirect('product_detail', product_id=product_id)


@staff_member_required
def product_management(request):
    """Product management view with advanced logic"""
    
    # Performance optimization: select_related and prefetch_related for admin interface
    products = Product.objects.select_related('category').prefetch_related('sizes').order_by('name')
    
    # Pagination
    paginator = Paginator(products, 20)  # Show 20 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'page_obj': page_obj,
    }
    
    return render(request, 'products/product_management.html', context)


@staff_member_required
def edit_product(request, product_id):
    """Edit product with context-aware advanced logic"""
    
    product = get_object_or_404(Product, pk=product_id)
    all_sizes = Size.objects.all()
    
    # Capture initial state for context-aware logic
    initial_has_sizes = product.has_sizes
    initial_sizes = list(product.sizes.all())
    initially_had_sizes = initial_has_sizes and len(initial_sizes) > 0
    
    if request.method == 'POST':
        # Handle form submission with advanced logic
        has_sizes = request.POST.get('has_sizes') == 'on'
        selected_sizes = request.POST.getlist('sizes')
        
        # Apply context-aware auto-adjustment logic
        if initially_had_sizes:
            # Product originally had sizes - more restrictive behavior
            if not has_sizes and selected_sizes:
                # Removing "Has Sizes" but sizes are selected - clear sizes with warning
                messages.warning(request, 
                    'Data Protection: Removing "Has Sizes" cleared all size selections to prevent data inconsistency.')
                selected_sizes = []
            elif has_sizes and not selected_sizes:
                # Has sizes enabled but no sizes selected - disable has_sizes
                messages.info(request, 
                    'Auto-adjustment: "Has Sizes" disabled because no sizes were selected.')
                has_sizes = False
        else:
            # Product originally had no sizes - more flexible behavior
            if has_sizes and not selected_sizes:
                # Has sizes enabled but no sizes selected - provide guidance
                messages.info(request, 
                    'Configuration Guidance: Please select at least one size when "Has Sizes" is enabled.')
            elif not has_sizes and selected_sizes:
                # Sizes selected but has_sizes not enabled - auto-enable
                messages.success(request, 
                    'Auto-adjustment: "Has Sizes" automatically enabled because sizes were selected.')
                has_sizes = True
        
        # Update product
        product.has_sizes = has_sizes
        product.sizes.clear()
        if has_sizes and selected_sizes:
            for size_id in selected_sizes:
                try:
                    size = Size.objects.get(id=size_id)
                    product.sizes.add(size)
                except Size.DoesNotExist:
                    pass
        
        product.save()
        messages.success(request, f'Product "{product.name}" updated successfully!')
        return redirect('edit_product', product_id=product_id)
    
    context = {
        'product': product,
        'all_sizes': all_sizes,
        'initially_had_sizes': initially_had_sizes,
    }
    
    return render(request, 'products/edit_product.html', context)