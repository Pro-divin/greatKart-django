from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, ReviewRating, Subscriber
from category.models import Category
from carts.models import CartItem
from django.db.models import Q
from carts.views import _cart_id
from django.core.paginator import Paginator
from django.contrib import messages
from .forms import SubscribeForm, ReviewForm
from orders.models import OrderProduct


# Store page
def store(request, category_slug=None):
    categories = None
    products = None
    
    if category_slug is not None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        paginator = Paginator(products, 10)
    else:
        products = Product.objects.filter(is_available=True).order_by('id')
        paginator = Paginator(products, 5)
    
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    product_count = products.count()
     
    context = {
        'products': paged_products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)


# About page
def about(request):
    return render(request, 'store/about.html')


# Product detail page
def product_detail(request, category_slug, product_slug):
    single_product = get_object_or_404(Product, category__slug=category_slug, slug=product_slug)
    in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()

    orderproduct = False
    if request.user.is_authenticated:
        orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()

    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'orderproduct': orderproduct,
        'reviews': reviews,
    }
    return render(request, 'store/product_detail.html', context)


# Search products
def search(request):
    products = Product.objects.none()
    product_count = 0

    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.filter(
                Q(description__icontains=keyword) | Q(product_name__icontains=keyword)
            ).order_by('-create_date')
            product_count = products.count()
    
    context = {
        'products': products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)


# Home page
def home(request):
    latest_fashions = Product.objects.filter(category__slug='latest', is_available=True).order_by('-created_date')[:8]
    vip_fashions = Product.objects.filter(category__slug='vip', is_available=True).order_by('-created_date')[:8]
    popular_products = Product.objects.filter(is_available=True).order_by('?')[:8]

    context = {
        'latest_fashions': latest_fashions,
        'vip_fashions': vip_fashions,
        'products': popular_products,
    }
    return render(request, 'home.html', context)


# About page subscription
def about_view(request):
    if request.method == 'POST':
        form = SubscribeForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            subscriber, created = Subscriber.objects.get_or_create(email=email)
            if created:
                messages.success(request, 'Thanks for subscribing!')
            else:
                messages.info(request, 'You are already subscribed.')
            return redirect('about')
    else:
        form = SubscribeForm()
    return render(request, 'store/about.html', {'form': form})


# Submit or update product review
def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)


# Generic subscription view (can be used on any page)
def subscribe(request):
    if request.method == 'POST':
        form = SubscribeForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            subscriber, created = Subscriber.objects.get_or_create(email=email)
            if created:
                messages.success(request, 'Thanks for subscribing!')
            else:
                messages.info(request, 'You are already subscribed.')
        else:
            messages.error(request, 'Please enter a valid email.')
    return redirect('store')  # or any page you want to redirect after subscribing
