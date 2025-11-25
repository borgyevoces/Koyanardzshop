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
    list_display = ('product_name', 'brand', 'category_name', 'price')
    inlines = [ProductImageInline]