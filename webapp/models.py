from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.conf import settings
import secrets

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    contact = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, default='avatars/user_default.png')

    USERNAME_FIELD = ("email")
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

class OtpToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="otps")
    otp_code = models.CharField(max_length=6, default=secrets.token_hex(3))
    tp_created_at = models.DateTimeField(auto_now_add=True)
    otp_expires_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.user.username

class Category(models.Model):
    category_name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.category_name
    
    class Meta:
        verbose_name_plural = "Categories"

class Brand(models.Model):
    brand = models.CharField(max_length=100)

    def __str__(self):
        return self.brand

class Product(models.Model):
    COMPONENT_CHOICES = [
        ('cpu', 'Processor'),
        ('motherboard', 'Motherboard'),
        ('ram', 'RAM'),
        ('gpu', 'Graphics Card'),
        ('psu', 'Power Supply'),
        ('case', 'PC Case'),
        ('cooling', 'Cooling'),
        ('monitor', 'Monitor'),
        ('storage', 'Storage'),
    ]

    category_name = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    component_type = models.CharField(max_length=50, choices=COMPONENT_CHOICES, default="motherboard")
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    product_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    model_file = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.product_name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    product_image = models.ImageField(upload_to="product_images/")
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Image for {self.product.product_name} ({self.id})"

class ProductVariation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variations")
    product_variation = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="products/variants", blank=True, null=True)

    def __str__(self):
        return f"{self.product.product_name} - {self.product_variation}"

class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=1)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.product.product_name} - {self.rating} Stars"

class Cart(models.Model):
    produkto = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.produkto.product_name}"

class Favorite(models.Model):
    favorite_product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return self.favorite_product.product_name

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Finished', 'Finished'),
        ('Cancelled', 'Cancelled'),
    ]

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    contact = models.CharField(max_length=20)
    email = models.EmailField()
    date = models.DateField()
    time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    reference_number = models.CharField(max_length=30, unique=True, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    reason = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('date', 'time')
        ordering = ['date', 'time']
    
    def save(self, *args, **kwargs):
        if not self.reference_number:
            import uuid
            from datetime import date
            str_today = date.today().strftime('%Y%m%d')
            unique_id = str(uuid.uuid4()).split('-')[0].upper()
            self.reference_number = f"{str_today}-{unique_id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.date} {self.time}"

class AppointmentProduct(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='products')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product} x {self.quantity}"

class Selling(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    product_name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    contact = models.CharField(max_length=20)
    address = models.TextField(null=True, blank=True)
    email = models.EmailField()
    selling_date = models.DateField()
    selling_time = models.TimeField()
    selling_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    reference_number = models.CharField(max_length=30, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.reference_number:
            import uuid
            from datetime import date
            str_today = date.today().strftime('%Y%m%d')
            unique_id = str(uuid.uuid4()).split('-')[0].upper()
            self.reference_number = f"{str_today}-{unique_id}"
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.product_name}"