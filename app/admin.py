from django.contrib import admin
from .models import CustomUser, OtpToken, Product, ProductImage, ProductVariation, Category
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2')
            }
        ),
    )

class OtpTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "otp_code")

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductVariationInline(admin.TabularInline):
    model = ProductVariation
    extra = 1
    fields = ('product_variation', 'description', 'price', 'stock', 'image')
    list_display = ('product_variation', 'price', 'stock')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'brand', 'category_name', 'price', 'has_3d_model', 'variant_count')
    fieldsets = (
        ('Basic Information', {
            'fields': ('product_name', 'description', 'brand', 'category_name')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'stock')
        }),
        ('Images & Media', {
            'fields': ('image', 'model_3d')
        }),
    )
    inlines = [ProductImageInline, ProductVariationInline]
    actions = ['add_variant_action']
    
    def has_3d_model(self, obj):
        return bool(obj.model_3d)
    has_3d_model.boolean = True
    has_3d_model.short_description = 'Has 3D Model'
    
    def variant_count(self, obj):
        return obj.variations.count()
    variant_count.short_description = 'Variants'
    
    def add_variant_action(self, request, queryset):
        """Action to add variant to selected products"""
        for product in queryset:
            ProductVariation.objects.get_or_create(
                product=product,
                product_variation='New Variant',
                defaults={
                    'price': product.price,
                    'stock': product.stock,
                }
            )
        self.message_user(request, f'Variant creation initiated for {queryset.count()} product(s). Please edit them to customize.')
    add_variant_action.short_description = 'Add new variant to selected products'