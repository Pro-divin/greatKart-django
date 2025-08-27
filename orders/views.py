from django.shortcuts import render, redirect
from django.http import JsonResponse
from carts.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order, Payment, OrderProduct
import json
from store.models import Product
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import requests
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from urllib.parse import urlencode


# ✅ Helper to finalize order
def finalize_order(order, payment, user):
    order.payment = payment
    order.is_ordered = True
    order.save()

    cart_items = CartItem.objects.filter(user=user)
    for item in cart_items:
        order_product = OrderProduct.objects.create(
            order=order,
            payment=payment,
            user=user,
            product=item.product,
            quantity=item.quantity,
            product_price=item.product.price,
            ordered=True,
        )
        order_product.variations.set(item.variations.all())
        order_product.save()

        # Reduce stock
        item.product.stock -= item.quantity
        item.product.save()

    # Clear cart
    cart_items.delete()

    # Send confirmation email as HTML
    mail_subject = 'Thank you for your order'
    html_message = render_to_string('orders/order_recieved_email.html', {
        'user': user,
        'order': order,
    })
    text_message = f"Hi {user.first_name},\n\nThank you for your order #{order.order_number}."

    to_email = user.email
    from_email = settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'no-reply@yourdomain.com'

    email = EmailMultiAlternatives(mail_subject, text_message, from_email, [to_email])
    email.attach_alternative(html_message, "text/html")
    email.send()


def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['order_id'])

    payment = Payment.objects.create(
        user=request.user,
        payment_id=body['transId'],
        payment_method=body['payment_method'],
        amount_paid=order.order_total,
        status=body['status']
    )

    finalize_order(order, payment, request.user)

    return JsonResponse({
        'order_number': order.order_number,
        'transId': payment.payment_id,
    })


def place_order(request, total=0, quantity=0):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    if not cart_items.exists():
        return redirect('store')

    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total) / 100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order()
            order.user = current_user
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.phone = form.cleaned_data['phone']
            order.email = form.cleaned_data['email']
            order.country = form.cleaned_data['country']
            order.city = form.cleaned_data['city']
            order.district = form.cleaned_data['district']
            order.order_note = form.cleaned_data['order_note']
            order.order_total = grand_total
            order.tax = tax
            order.ip = request.META.get('REMOTE_ADDR')
            order.save()

            current_date = datetime.date.today().strftime("%Y%m%d")
            order_number = current_date + str(order.id)
            order.order_number = order_number
            order.save()

            # Build full callback URL for Flutterwave
            domain = get_current_site(request).domain
            scheme = 'https' if request.is_secure() else 'http'
            callback_url = f"{scheme}://{domain}{reverse('flutterwave_callback')}"

            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
                'callback_url': callback_url,  # pass this to template
            }
            return render(request, 'orders/payments.html', context)
    return redirect('checkout')


def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        subtotal = sum(item.product_price * item.quantity for item in ordered_products)
        payment = Payment.objects.get(payment_id=transID)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')




@csrf_exempt
def flutterwave_callback(request):
    status = request.GET.get('status')
    tx_ref = request.GET.get('tx_ref')
    transaction_id = request.GET.get('transaction_id')

    if status == "successful":
        try:
            order = Order.objects.get(order_number=tx_ref, is_ordered=False)
        except Order.DoesNotExist:
            return redirect('home')

        # Optional: Verify via Flutterwave API here using secret key
        payment = Payment.objects.create(
            user=order.user,
            payment_id=transaction_id,
            payment_method="Flutterwave",
            amount_paid=order.order_total,
            status="Completed"
        )

        finalize_order(order, payment, order.user)
        return redirect(f"{reverse('order_complete')}?order_number={tx_ref}&payment_id={transaction_id}")
    else:
        return redirect('payment_failed')
    
def payment_failed(request):
    return render(request, 'orders/payment_failed.html')


def payment_page(request):
    domain = get_current_site(request).domain
    scheme = 'https' if request.is_secure() else 'http'

    # Get latest unpaid order for the user
    try:
        order = Order.objects.filter(user=request.user, is_ordered=False).latest('created_at')
    except Order.DoesNotExist:
        return redirect('store')  # or some fallback

    query = urlencode({'order_id': order.order_number})
    callback_url = f"{scheme}://{domain}{reverse('flutterwave_callback')}?{query}"

    context = {
        'order': order,
        'callback_url': callback_url,
        # Add total, tax, grand_total if needed
    }

    return render(request, 'orders/payment_page.html', context)
