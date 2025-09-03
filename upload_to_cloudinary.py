import os
import django
from django.core.files import File

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greatKart.settings')
django.setup()

from store.models import Product, ProductGallery

MEDIA_ROOT = os.path.join(os.getcwd(), 'media')  # adjust if needed

# Upload main product images
for p in Product.objects.all():
    if p.images:
        local_path = os.path.join(MEDIA_ROOT, p.images.name)
        if os.path.exists(local_path):
            with open(local_path, 'rb') as f:
                p.images.save(os.path.basename(local_path), File(f), save=True)
            print(f'Uploaded {p.product_name} main image')
        else:
            print(f'File not found for {p.product_name}: {local_path}')

# Upload gallery images
for g in ProductGallery.objects.all():
    if g.image:
        local_path = os.path.join(MEDIA_ROOT, g.image.name)
        if os.path.exists(local_path):
            with open(local_path, 'rb') as f:
                g.image.save(os.path.basename(local_path), File(f), save=True)
            print(f'Uploaded {g.product.product_name} gallery image')
        else:
            print(f'File not found for {g.product.product_name}: {local_path}')
import os
import django
from django.core.files import File

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greatKart.settings')
django.setup()

from store.models import Product, ProductGallery

MEDIA_ROOT = os.path.join(os.getcwd(), 'media')  # adjust if needed

# Upload main product images
for p in Product.objects.all():
    if p.images:
        local_path = os.path.join(MEDIA_ROOT, p.images.name)
        if os.path.exists(local_path):
            with open(local_path, 'rb') as f:
                p.images.save(os.path.basename(local_path), File(f), save=True)
            print(f'Uploaded {p.product_name} main image -> Cloudinary URL: {p.images.url}')
        else:
            print(f'File not found for {p.product_name}: {local_path}')

# Upload gallery images
for g in ProductGallery.objects.all():
    if g.image:
        local_path = os.path.join(MEDIA_ROOT, g.image.name)
        if os.path.exists(local_path):
            with open(local_path, 'rb') as f:
                g.image.save(os.path.basename(local_path), File(f), save=True)
            print(f'Uploaded {g.product.product_name} gallery image -> Cloudinary URL: {g.image.url}')
        else:
            print(f'File not found for {g.product.product_name}: {local_path}')
