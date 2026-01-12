from django.contrib import admin
from .models import CustomUser, OtpToken, Product, ProductImage, Category
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

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'brand', 'category_name', 'price', 'has_3d_model')
    fieldsets = (
        ('Basic Information', {
            'fields': ('product_name', 'description', 'brand', 'category_name', 'component_type')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'stock')
        }),
        ('Images & Media', {
            'fields': ('image', 'model_3d')
        }),
    )
    inlines = [ProductImageInline]
    
    def has_3d_model(self, obj):
        return bool(obj.model_3d)
    has_3d_model.boolean = True
    has_3d_model.short_description = 'Has 3D Model'