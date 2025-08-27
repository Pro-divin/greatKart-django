from django.contrib import admin
from .models import Product, Variation, ProductGallery, ReviewRating, Subscriber

# Inline for multiple images in product admin
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1
    fields = ['image', 'alt_text']

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'modified_date', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}
    inlines = [ProductGalleryInline]

class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'variation_value')

class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at')   # ✅ Show email + date
    search_fields = ('email',)                  # ✅ Search by email
    list_per_page = 25                          # ✅ Pagination
    ordering = ('-subscribed_at',)              # ✅ Newest first

admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ProductGallery)
admin.site.register(ReviewRating)
admin.site.register(Subscriber, SubscriberAdmin)  # ✅ Improved
