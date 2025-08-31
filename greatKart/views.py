from django.shortcuts import render
from store.models import Product

def home(request):
    Products = Product.objects.all().filter(is_available=True)

    context = {
        'products': Products,
    }
    return render(request, 'home.html', context)

def safe_payments(request):
    return render(request, 'store/safe-payments.html')
def footer(request):
    return render(request, 'footer.html')
def help_center(request):
    return render(request, 'help_center.html')

def corporate_responsibility(request):
    return render(request, 'corporate_responsibility.html')



def conditions(request):
    return render(request, 'conditions.html')

def privacy(request):
    return render(request, 'privacy.html')

def cookies(request):
    return render(request, 'cookies.html')

def product_policy(request):
    return render(request, 'product_policy.html')


