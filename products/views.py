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
from .forms import ReviewForm, ProductForm


def all_products(request):
    """A view to show all products, including sorting and search queries"""
    
    # Performance optimization: select_related for foreign keys
    products = Product.objects.select_related('category').filter(in_stock=True)
    query = None
    current_category = None
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
            category_name = request.GET['category']
            products = products.filter(category__name=category_name)
            # Try to get the category - if filtering worked, we should be able to get it
            current_category = Category.objects.filter(name=category_name).first()

        if 'size' in request.GET:
            size_name = request.GET['size']
            if size_name:
                products = products.filter(sizes__name=size_name, has_sizes=True)

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect('products')
            
            queries = Q(name__icontains=query) | Q(description__icontains=query)
            products = products.filter(queries)

    # Determine if we should show size filters
    current_size = request.GET.get('size', '')
    
    # Show size filter only for bicycle categories or when products with sizes are present
    show_size_filter = False
    bicycle_categories = ['road_bikes', 'mountain_bikes', 'electric_bikes', 'bmx_bikes', 'kids_bikes']
    
    # Check if we're in a bicycle category or have sized products
    category_name = request.GET.get('category', '')
    if category_name in bicycle_categories:
        show_size_filter = True
    elif not category_name:
        # On all products page, show if there are any sized products
        has_sized_products = Product.objects.filter(in_stock=True, has_sizes=True).exists()
        if has_sized_products:
            show_size_filter = True
    
    available_sizes = Size.objects.all().order_by('sort_order') if show_size_filter else []

    # Pagination
    paginator = Paginator(products, 12)  # Show 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    current_sorting = f'{sort}_{direction}'

    context = {
        'products': page_obj,
        'search_term': query,
        'current_category': current_category,
        'current_sorting': current_sorting,
        'page_obj': page_obj,
        'show_size_filter': show_size_filter,
        'available_sizes': available_sizes,
        'current_size': current_size,
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
def add_product(request):
    """Add new product with comprehensive form"""
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" created successfully!')
            return redirect('edit_product', product_id=product.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm()
    
    context = {
        'form': form,
        'is_editing': False,
    }
    
    return render(request, 'products/add_edit_product.html', context)


@staff_member_required
def edit_product(request, product_id):
    """Edit product with comprehensive form and context-aware advanced logic"""
    
    product = get_object_or_404(Product, pk=product_id)
    
    # Capture initial state for context-aware logic
    initial_has_sizes = product.has_sizes
    initial_sizes = list(product.sizes.all())
    initially_had_sizes = initial_has_sizes and len(initial_sizes) > 0
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            # Apply context-aware auto-adjustment logic before saving
            has_sizes = form.cleaned_data.get('has_sizes')
            selected_sizes = form.cleaned_data.get('sizes')
            
            if initially_had_sizes:
                # Product originally had sizes - more restrictive behavior
                if not has_sizes and selected_sizes:
                    # Removing "Has Sizes" but sizes are selected - clear sizes with warning
                    form.cleaned_data['sizes'] = []
                    messages.warning(request, 
                        'Data Protection: Removing "Has Sizes" cleared all size selections to prevent data inconsistency.')
                elif has_sizes and not selected_sizes:
                    # Has sizes enabled but no sizes selected - disable has_sizes
                    form.cleaned_data['has_sizes'] = False
                    messages.info(request, 
                        'Auto-adjustment: "Has Sizes" disabled because no sizes were selected.')
            else:
                # Product originally had no sizes - more flexible behavior
                if not has_sizes and selected_sizes:
                    # Sizes selected but has_sizes not enabled - auto-enable
                    form.cleaned_data['has_sizes'] = True
                    messages.success(request, 
                        'Auto-adjustment: "Has Sizes" automatically enabled because sizes were selected.')
            
            # Save the product with adjusted data
            product = form.save()
            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('edit_product', product_id=product_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'product': product,
        'initially_had_sizes': initially_had_sizes,
        'is_editing': True,
    }
    
    return render(request, 'products/add_edit_product.html', context)


@staff_member_required
def delete_product(request, product_id):
    """Delete product with confirmation"""
    
    product = get_object_or_404(Product, pk=product_id)
    
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully!')
        return redirect('product_management')
    
    context = {
        'product': product,
    }
    
    return render(request, 'products/delete_product.html', context)