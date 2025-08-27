"""
URL configuration for greatKart project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home, name='home'),
    path('store/', include('store.urls')),
    path('cart/', include('carts.urls')),
    path('accounts/', include('accounts.urls')),
    path('orders/', include('orders.urls')),
    path('safe-payments/', views.safe_payments, name='safe-payments'),
    path('footer/', views.footer, name='footer'),
    path('help-center/', views.help_center, name='help_center'),
    # urls.py
    path('corporate-responsibility/', views.corporate_responsibility, name='corporate_responsibility'),
    path('conditions/', views.conditions, name='conditions'),
     path('privacy/', views.privacy, name='privacy'),
    path('cookies/', views.cookies, name='cookies'),
    path('product_policy/', views.product_policy, name='product_policy'),





] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
