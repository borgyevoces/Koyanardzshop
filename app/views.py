from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, CreateView
from .models import OtpToken, Category, Brand, Product, ProductImage, ProductReview, Appointment, AppointmentProduct, Selling, Favorite
from .forms import RegisterForm, LoginForm, ProfileForm, ProfileUpdateForm, AddCategory, AddBrand, Add, AddVariantForm, ProductReviewForm, AppointmentForm, SellingForm
from .serializers import ProductSerializer
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_POST, require_http_methods
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.urls import reverse_lazy
from datetime import date, time, datetime, timedelta
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate, logout, get_user_model, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.utils.decorators import method_decorator
from django.db.models import Q, Count, Sum, F
from django.db import models
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
import os, json
import random
import urllib.parse

def product_list(request):
    qs = Product.objects.all().values('id','product_name','price','description','image')
    return JsonResponse(list(qs), safe=False)

def get_products(request):
    component = request.GET.get("component")
    products = Product.objects.filter(category=component, stock__gt=0)
    data = [
        {
            "id": p.id,
            "name": p.product_name,
            "price": float(p.price),
            "thumbnail": p.thumbnail.url if p.thumbnail else "",
            "glb": f"/static/images/3D/{p.glb_file}"
        } for p in products
    ]
    return JsonResponse({"products": data})

def save_appointment(request):
    if request.method != "POST":
        return JsonResponse({'error': 'Post required'}, status=400)
    
    data = json.loads(request.body.decode("utf-8"))

    Appointment.objects.create(
        first_name = data.get("first_name"),
        last_name = data.get("last_name"),
        contact = data.get("contact"),
        email = data.get("email"),
        date = data.get("date"),
        time = data.get("time")
    )
    return JsonResponse({"status:" "success"})

def model_viewer(request):
    parts = request.GET.get('parts', '')
    models = [m for m in parts.split(',') if m]
    models = [f"/static/images/3D/{m}" for m in models]
    return render(request, 'app/buying/model_viewer.html', {'models': models})

def products_by_component(request):
    comp = request.GET.get('component_type', '').strip()
    qs = Product.objects.all()

    if comp:
        qs = qs.filter(component_type=comp)

    data = []
    for p in qs:
        data.append({
            "id": p.id,
            "product_name": p.product_name,
            "price": float(p.price),
            "image_url": p.image.url if p.image else None,
            "component_type": p.component_type,
            "stock": p.stock,
        })

    return JsonResponse(data, safe=False)


#ADMIN

def addproduct(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    brands = Brand.objects.all()
    product_form = Add()
    category_form = AddCategory()
    brand_form = AddBrand()
    variant_form = AddVariantForm()

    if request.method == 'POST':
        if 'add_product' in request.POST:
            product_form = Add(request.POST, request.FILES)
            if product_form.is_valid():
                new_product = product_form.save()
                images = request.FILES.getlist('images')

                for idx, image in enumerate(images):
                    ProductImage.objects.create(product=new_product, product_image=image, order=idx)
                return redirect('admin_product')
        elif 'add_category' in request.POST:
            category_form = AddCategory(request.POST)
            if category_form.is_valid():
                category_form.save()
                return redirect('admin_product')
        elif 'add_brand' in request.POST:
            brand_form = AddBrand(request.POST)
            if brand_form.is_valid():
                brand_form.save()
                return redirect('admin_product')
        elif 'add_variant' in request.POST:
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=product_id)

            variant_form = AddVariantForm(request.POST, request.FILES)

            if variant_form.is_valid():
                new_variant = variant_form.save(commit=False)
                new_variant.product = product
                new_variant.save()
                return redirect('admin_product')

    return render(request, 'app/admin/admin_product.html', {
        'products': products,
        'form': product_form,
        'category_form': category_form,
        'categories': categories,
        'brand_form': brand_form,
        'brands': brands,
        'variant_form': variant_form
    })
    
@csrf_exempt
def update_product(request):
    if request.method == 'POST':
        data = request.POST
        product = get_object_or_404(Product, id=data['id'])
        product.product_name = data['product_name']
        product.stock = data['stock']
        product.price = data['price']
        product.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@csrf_protect 
def delete_products(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        ids = data.get('ids', [])
        Product.objects.filter(id__in=ids).delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

#END ADMIN

#REGISTER & LOGIN

def register(request):
    form = RegisterForm()
    otp_code = None 

    if request.method == 'POST':
        if 'otp_code' in request.POST: 
            username = request.POST['username']
            otp_code = request.POST['otp_code']
            user = get_user_model().objects.get(username=username)

            user_otp = OtpToken.objects.filter(user=user).last()

            if user_otp and user_otp.otp_code == otp_code:
                if user_otp.otp_expires_at > timezone.now():
                    user.is_active = True
                    user.save()
                    return redirect("home")
                else:
                    messages.warning(request, "The OTP has expired. Please request a new one.")
            else:
                messages.warning(request, "Invalid OTP entered. Please try again.")

        else: 
            form = RegisterForm(request.POST)
            if form.is_valid():
                user = form.save()
                otp = OtpToken.objects.create(user=user, otp_expires_at=timezone.now() + timezone.timedelta(minutes=5))

                subject = "Email Verification"
                message = f"""  
                                Hi {user.username}, here is your OTP: {otp.otp_code}
                                It expires in 5 minutes. Use the URL below to return to the website:
                                http://127.0.0.1:8000/signup/{user.username}
                            """
                sender = settings.EMAIL_HOST_USER
                receiver = [user.email]

                send_mail(subject, message, sender, receiver, fail_silently=False)

                messages.success(request, "Account created successfully! Please check your email for the OTP.")
                otp_code = otp.otp_code 

    context = {
        "form": form,
        "otp_code": otp_code,
    }
    return render(request, "app/account/signup.html", context)

def resend_otp(request):
    if request.method == 'POST':
        user_email = request.POST["otp_email"]

        if get_user_model().objects.filter(email=user_email).exists():
            user = get_user_model().objects.get(email=user_email)
            otp = OtpToken.objects.create(user=user, otp_expires_at=timezone.now() + timezone.timedelta(minutes=5))

            subject="Email Verification"
            message = f"""  
                                Hi {user.username}, here is your OTP {otp.otp_code}
                                it expires in 5 minute, use the url below to redirect back to the website
                                http://127.0.0.1:8000/verify-email/{user.username}

                                """
            sender = settings.EMAIL_HOST_USER
            receiver = [user.email]

            send_mail(
                    subject,
                    message,
                    sender,
                    receiver,
                    fail_silently=False,
                )

            messages.success(request, "A new OTP has been sent to your email")
            return redirect("verify-email", username=user.username)
        else:
            messages.warning(request, "This email doesn't exist")
            return redirect("resend-otp")

    context = {}
    return render(request, "app/account/resend_otp.html", context)

def login_view(request):
    if request.method == 'POST':
        login_input = request.POST['username_or_email']
        password = request.POST['password']

        user = None
        if '@' in login_input:
            user = get_user_model().objects.filter(email=login_input).first()
        else: 
            user = get_user_model().objects.filter(username=login_input).first()


        if user:
            if user.check_password(password):
                auth_login(request, user)
                
                if user.is_staff:
                    return redirect('admin_dashboard')
                else:
                    return redirect('home')
            else:
                messages.error(request, "Invalid username or password")
                return redirect("login")
        else:
            messages.error(request, "Invalid username or password")
        return redirect("login")

    return render(request, 'app/account/login.html')

def forgot_password(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            users = get_user_model().objects.filter(email=email)
            if users.exists():
                for user in users:
                    token = default_token_generator.make_token(user)
                    uid = user.pk
                    current_site = get_current_site(request)
                    reset_url = f"http://{current_site.domain}/reset-password/{uid}/{token}/"
                    message = f"Click the link to reset your password: {reset_url}"
                    send_mail(
                        "Password Reset Request",
                        message,
                        settings.EMAIL_HOST_USER,
                        [email],
                    )
                messages.success(request, "Password reset link has been sent to your email.")
                return redirect('login')
            else:
                messages.warning(request, "No account with this email exists.")
                return redirect('forgot_password')
    else:
        form = PasswordResetForm()

    return render(request, 'app/account/forgotpassword.html', {'form': form})

def reset_password(request, uid, token):
    UserModel = get_user_model()
    try:
        user = UserModel.objects.get(pk=uid)
    except UserModel.DoesNotExist:
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                auth_login(request, user)
                messages.success(request, "Password has been reset.")
                return redirect('home')
        else:
            form = SetPasswordForm(user)
    else:
        messages.error(request, "The reset link is invalid or has expired.")
        return redirect('forgot_password')

    return render(request, 'app/account/password_reset.html', {'form': form})

@login_required
def user_profile(request):
    profile_form = ProfileForm(instance=request.user)
    password_form = PasswordChangeForm(request.user)

    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if profile_form.is_valid():
            profile_form.save()
            return JsonResponse({
                'success': True,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'contact': request.user.contact,
                'address': request.user.address,
            })
        else:
            return JsonResponse({'success': False})

    if request.method == 'POST':
        if 'save_profile' in request.POST:
            profile_form = ProfileForm(request.POST, request.FILES, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('profile')
            else:
                messages.error(request, 'Error Update')
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password updated successfully!')
                return redirect('profile')
            else:
                messages.error(request, 'Error Update')

    return render(request, 'app/account/profile.html', {
        'profile_form': profile_form,
        'password_form': password_form,
    })

def logout_view(request):
    logout(request)
    return redirect('home') 

#END REGISTER & LOGIN
@csrf_exempt
@require_POST
def add_pc_build_to_cart(request):
    try:
        data = json.loads(request.body)
        parts = data.get('parts', [])

        cart = request.session.get('cart', {})

        for part in parts:
            product_id = str(part['id'])
            quantity = part.get('quantity', 1)

            produkto = Product.objects.get(pk=product_id)

            if product_id in cart:
                cart[product_id]['quantity'] += quantity
                if cart[product_id]['quantity'] > produkto.stock:
                    cart[product_id]['quantity'] = produkto.stock
            else:
                cart[product_id] = {
                    'image': produkto.image.url if produkto.image else None,
                    'product_name': produkto.product_name,
                    'price': float(produkto.price),
                    'quantity': min(quantity, produkto.stock),
                }

        request.session['cart'] = cart

        return JsonResponse({
            'message': 'PC Build added to cart!',
            'cart_count': sum(item['quantity'] for item in cart.values())
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_protect
@require_POST
def add_to_cart(request, product_id):
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            quantity = data.get('quantity', 1)
            variant_id = data.get("variant_id")
        else: 
            quantity = int(request.POST.get('quantity', 1))
            variant_id = request.POST.get("variant_id")

        cart = request.session.get('cart', {})
        if variant_id:
            variant = get_object_or_404(ProductVariation, pk=variant_id)
            cart_key = f"variant-{variant_id}"

            if cart_key in cart:
                cart[cart_key]["quantity"] += quantity
                if cart[cart_key]["quantity"] > variant.stock:
                    cart[cart_key]["quantity"] = variant.stock
            else:
                cart[cart_key] = {
                    "image": variant.image.url if variant.image else None,
                    "product_name": f"{variant.product.product_name} ({variant.product_variation})",
                    "price": float(variant.price),
                    "quantity": min(quantity, variant.stock),
                    "variant_id": variant_id,
                    "product_id": product_id,
                }
        else:
            produkto = get_object_or_404(Product, pk=product_id)

            if str(product_id) in cart:
                cart[str(product_id)]['quantity'] += quantity
                if cart[str(product_id)]['quantity'] > produkto.stock:
                    cart[str(product_id)]['quantity'] = produkto.stock
            else:
                cart[str(product_id)] = {
                    'image': produkto.image.url if produkto.image else None,
                    'product_name': produkto.product_name,
                    'price': float(produkto.price),
                    'quantity': min(quantity, produkto.stock),
                    "product_id": product_id,
                }

        request.session['cart'] = cart

        if request.content_type == 'application/json':
            return JsonResponse({'message': 'Product added successfully!', 'cart_count': sum(item['quantity'] for item in cart.values())})
        return redirect('cart')

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def update_cart(request, product_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})

        cart_key = str(product_id)
        variant_key = f"variant-{product_id}"

        if cart_key in cart:
            item = cart[cart_key]
            stock = get_object_or_404(Product, pk=product_id).stock
        elif variant_key in cart:
            item = cart[variant_key]
            variant = get_object_or_404(ProductVariation, pk=item["variant_id"])
            stock = variant.stock
            cart_key = variant_key
        else:
            return redirect(request.META.get('HTTP_REFERER', 'cart'))

        action = request.POST.get('action')
        current_quantity = item['quantity']

        if action == 'increase':
            if current_quantity < stock:
                item['quantity'] += 1
        elif action == 'decrease':
            if current_quantity > 1:
                item['quantity'] -= 1
        else:
            quantity = int(request.POST.get('quantity', 1))
            item['quantity'] = max(1, min(quantity, stock))
        
        cart[cart_key] = item
        request.session['cart'] = cart
    return redirect(request.META.get('HTTP_REFERER', 'cart'))

def remove_from_cart(request, product_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        cart_key = str(product_id)
        variant_key = f"variant-{product_id}"

        if cart_key in cart:
            del cart[cart_key]
        
        elif variant_key in cart:
            del cart[variant_key]

        request.session['cart'] = cart
    return redirect(request.META.get('HTTP_REFERER', 'cart'))

def get_cart_data(request):
    cart = request.session.get('cart', {})
    return JsonResponse({'cart_products': list(cart.values())})

def direct_checkout(request):
    if request.method == "POST":
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))

        request.session['direct_checkout'] = {
            'product_id': product_id,
            'quantity': quantity
        }
        return redirect('appointment')
    return redirect('product')

@csrf_exempt
def toggle_favorite(request, product_id):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "Login required"}, status=401)
    
    user = request.user
    product = get_object_or_404(Product, id=product_id)

    favorite, created = Favorite.objects.get_or_create(
        user=user,
        product=product
    )

    if not created:
        favorite.delete()
        return JsonResponse({"status": "removed"})
    else:
        return JsonResponse({
            "status": "added",
            "product": {
                "id": product.id,
                "name": product.product_name,
                "img": product.image.url if product.image else ""
            }
        })




@csrf_exempt
def submit_rating_ajax(request, product_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "login_required"}, status=403)

    produkto = get_object_or_404(Product, id=product_id)
    rating = int(request.POST.get("rating", 0))

    review, created = ProductReview.objects.get_or_create(
        product=produkto, user=request.user
    )
    review.rating = rating
    review.save()

    reviews = produkto.reviews.all()
    avg = round(sum(r.rating for r in reviews) / reviews.count(), 1)

    return JsonResponse({
        "success": True,
        "rating": review.rating,
        "average": avg,
        "count": reviews.count(),
    })


@csrf_exempt
def submit_comment_ajax(request, product_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "login_required"}, status=403)

    produkto = get_object_or_404(Product, id=product_id)
    comment = request.POST.get("comment", "")

    review, created = ProductReview.objects.get_or_create(
        product=produkto,
        user=request.user
    )
    review.comment = comment
    review.save()

    return JsonResponse({
        "success": True,
        "comment": review.comment,
        "rating": review.rating,
        "created": review.created_at.strftime("%b %d, %Y"),
        "username": request.user.username
    })


@login_required
def appoint(request):
    form = AppointmentForm()

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            selected_date = form.cleaned_data['date']
            count = Appointment.objects.filter(date=selected_date).count()

            if count >= 10:
                form.add_error('date', 'Maximum appointments reached for this date.')
            else:
                request.session['appointment_data'] = {
                    'first_name': form.cleaned_data['first_name'],
                    'last_name': form.cleaned_data['last_name'],
                    'contact': form.cleaned_data['contact'],
                    'email': form.cleaned_data['email'],
                    'date': selected_date.isoformat(),
                    'time': form.cleaned_data['time']
                }
                return redirect('checkout') 
    
    else:
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        }
        form = AppointmentForm(initial=initial_data)

    appointments = Appointment.objects.all()
    events = [{
            'title': f"{appoint.first_name} {appoint.last_name}",  
            'start': appoint.date.strftime('%Y-%m-%d'),
            'color': 'green'
        }for appoint in appointments]

    return render(request, 'app/buying/appointment.html', {
        'form': form,
        'events': json.dumps(events)  
    })

def appointing(request):
    appointments = Appointment.objects.all()
    events = [{
        'product_name': f"{a.first_name} {a.last_name}",
        'start': f"{a.date}T{a.time}",
    } for a in appointments]
    return JsonResponse(events, safe=False)

def get_available_times(request):
    selected_date = request.GET.get('date')
    
    all_slots = [
        "10:00", "11:00", "12:00", "13:00",
        "14:00", "15:00", "16:00", "17:00"
    ]

    booked = Appointment.objects.filter(date=selected_date).values_list('time', flat=True)
    booked_times = [t.strftime("%H:%M") for t in booked]
    free_slots = [t for t in all_slots if t not in booked_times]

    return JsonResponse({'available_times': free_slots})

def get_booked_dates(request):
    appointments = Appointment.objects.values('date').annotate(count=models.Count('id'))

    fully_booked = [
        a['date'].strftime('%Y-%m-%d')
        for a in appointments
        if a['count'] >= 10
    ]

    return JsonResponse({'blocked_dates': fully_booked})

def get_appointment_counts(user):
    if not user.is_authenticated:
        return {
            'count_all': 0,
            'count_pending': 0,
            'count_completed': 0,
            'count_cancelled': 0
        }

    view_apps = Appointment.objects.filter(email=user.email)
    sell_apps = Selling.objects.filter(email=user.email)

    return {
        'count_all': view_apps.count() + sell_apps.count(),
        'count_pending': view_apps.filter(status="Pending").count() +
                         sell_apps.filter(status="Pending").count(),
        'count_completed': view_apps.filter(status__in=["Completed", "Finished"]).count() +
                           sell_apps.filter(status="Completed").count(),
        'count_cancelled': view_apps.filter(status="Cancelled").count() +
                           sell_apps.filter(status="Cancelled").count(),
    }


@require_POST
def finished_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = 'Finished'
    appointment.save()
    messages.success(request, "Marked as Finished")
    return redirect('admin_appointment')

@require_http_methods(["GET", "POST"])
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == "POST":
        reason = request.POST.get("cancel_reason", "")
        appointment.status = "Cancelled"
        appointment.cancel_reason = reason
        appointment.save()

        send_mail(
            subject='Your Appointment Has Been Cancelled',
            message=f"Hello {appointment.first_name},\n\nYour appointment (Ref: {appointment.reference_number}) has been cancelled.\n\nReason: {reason}\n\nThank you.",
            from_email='koyanardzshop@gmail.com',
            recipient_list=[appointment.email],
            fail_silently=False,
        )

        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)

@require_http_methods(["GET", "POST"])
def cancel_trade(request, selling_id):
    selling = get_object_or_404(Selling, id=selling_id)

    if request.method == "POST":
        reason = request.POST.get("cancel_reason", "")
        selling.status = "Cancelled"
        selling.cancel_reason = reason
        selling.save()

        send_mail(
            subject='Your Trade Has Been Cancelled',
            message=f"Hello {selling.first_name},\n\nYour appointment for trade (Ref: {selling.reference_number}) has been cancelled.\n\nReason: {reason}\n\nThank you.",
            from_email='rlphjhnjhn@gmail.com',
            recipient_list=[selling.email],
            fail_silently=False,
        )

        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)

@require_POST
def complete_trade(request, selling_id):
    trade = get_object_or_404(Selling, id=selling_id)
    trade.status = 'Completed'
    trade.save()
    return redirect('admin_selling')

@login_required
def my_appointment_history(request):
    appointments = Appointment.objects.filter(email=request.user.email).order_by('-date')
    return render(request, 'app/admin/my_historyappointment.html', {'appointments': appointments})

class HomePage(TemplateView):
    template_name = 'app/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['products'] = Product.objects.all().order_by('-id')[:5]
        return context

class ProductPage(TemplateView):
    model = Product
    template_name = 'app/buying/product.html'
    context_object_name = 'products'

    COMPONENT_TO_GBL = {
    "cpu": "cpu.gbl",
    "motherboard": "motherboard.gbl",
    "ram": "ram.gbl",
    "gpu": "gpu.gbl",
    "psu": "psu.gbl",
    "case": "case.gbl",
    "cooling": "cooling.gbl",
    "monitor": "monitor.gbl",
    "storage": "storage.gbl",
}
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
    
        search_query = self.request.GET.get('search', '').strip()
        category_filter = self.request.GET.get('category', '').strip()
        brand_filter = self.request.GET.get('brand', '').strip()
        price_order = self.request.GET.get('price_order', '').strip()
        component_filter = self.request.GET.get('component', '').strip()


        products = Product.objects.all()

        if search_query:
            products = products.filter(
                Q(category_name__category_name__icontains=search_query) |
                Q(brand__brand__icontains=search_query) |
                Q(product_name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(price__icontains=search_query)
            )

        if category_filter:
            products = products.filter(category_name__id=category_filter)
            brands = Brand.objects.filter(product__category_name__id=category_filter).distinct()
        else:
            brands = Brand.objects.annotate(product_count=Count('product')).order_by('-product_count')[:5]
        
        if brand_filter:
            products = products.filter(brand__id=brand_filter)

        if component_filter:
            products = products.filter(component_type=component_filter)

        
        if price_order == 'high':
            products = products.order_by('-price')
        elif price_order == 'low':
            products = products.order_by('price')

        cart = self.request.session.get('cart', {})
        context.update({
            'products': products,
            'brands': brands,
            'search_query': search_query,
            'category_filter': category_filter,
            'brand_filter': brand_filter,
            'component_filter': component_filter,
            'cart_count': sum(produkto['quantity'] for produkto in cart.values()),
        })
        context['price_order'] = price_order
        return context

class ProductItemPage(TemplateView):
    template_name = 'app/buying/product_item.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_id = self.kwargs.get('product_id')
        produkto = get_object_or_404(Product, id=product_id)
        variant_id = self.request.GET.get("variant")

        if variant_id:
            try:
                selected_variant = produkto.variations.get(id=variant_id)
                context["selected_variant"] = selected_variant
                context["price"] = selected_variant.price
                context["stock"] = selected_variant.stock
                context["images"] = [selected_variant]
            except ProductVariation.DoesNotExist:
                context["selected_variant"] = None
                context["price"] = produkto.price
                context["stock"] = produkto.stock
                context["images"] = produkto.images.all()
        else:
            context["selected_variant"] = None
            context["price"] = produkto.price
            context["stock"] = produkto.stock
            context["images"] = produkto.images.all()
        
        context["products"] = Product.objects.exclude(id=produkto.id).order_by('-id')[:30]

        reviews = produkto.reviews.all().order_by("-created_at")
        context["reviews"] = reviews

        if reviews.exists():
            context["average_rating"] = round(sum(r.rating for r in reviews) / reviews.count(), 1)
        else:
            context["average_rating"] = 0
        
        context["review_form"] = ProductReviewForm()
        context["produkto"] = produkto
        context["images"] = produkto.images.all()
        context["variations"] = produkto.variations.all()
        return context
    
    def post(self, request, *args, **kwargs):
        product_id = kwargs.get("product_id")
        produkto = get_object_or_404(Product, id=product_id)

        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = produkto
            review.user = request.user
            review.save()

        return redirect("product_item", product_id=product_id)

class AppointmentPage(TemplateView):
    template_name = 'app/buying/appointment.html'

    def clean_date(self):
        selected_date = self.cleaned_data['date']
        today = date.today()

        if selected_date < today:
            raise ValidationError("You cannot select a past date for an appointment.")
        
        return selected_date

class AIBotPage(TemplateView):
    template_name = 'app/buying/aibot.html'

class CheckoutPage(TemplateView):
    template_name = 'app/buying/checkout.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        appointment_data = self.request.session.get('appointment_data')

        if appointment_data.get('time'):
            time_obj = datetime.strptime(appointment_data['time'], "%H:%M")
            appointment_data['time'] = time_obj.strftime("%I:%M %p")

        context['appointment_datas'] = appointment_data

        direct = self.request.session.get('direct_checkout')

        if direct:
            product = get_object_or_404(Product, pk=direct['product_id'])
            quantity = int(direct.get('quantity', 1))

            checkout_item = {
                'product_name': product.product_name,
                'price': float(product.price),
                'quantity': quantity,
                'image': product.image.url if product.image else None,
                'product_id': product.id,
                'sub_total': float(product.price) * quantity
            }
            context['cart_products'] = [checkout_item]     
            context['total_price'] = checkout_item['sub_total']
            context['is_direct'] = True
            return context
        
        cart = self.request.session.get('cart', {})
            
        for product_id, produkto in cart.items():
            produkto['sub_total'] = float(produkto['price']) * int(produkto['quantity'])
            produkto['product_id'] = product_id

        context['cart_products'] = cart.values()
        context['total_price'] = sum(item['sub_total'] for item in cart.values())
        context['is_direct'] = False
        return context

class AppointmentCompletePage(TemplateView):
    template_name = 'app/buying/appointment_complete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['products'] = Product.objects.all().order_by('-id')[:30]
        return context

    def get(self, request, *args, **kwargs):
        complete_data = request.session.get('appointment_complete')
        if not complete_data:
            return redirect('appointment')
        context = self.get_context_data()
        context['reference_number'] = complete_data.get('reference_number')
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        appointment_data = request.session.get('appointment_data')
        cart = request.session.get('cart', {})
        direct = request.session.get('direct_checkout')

        if not appointment_data and not direct:
            return redirect('appointment')

        if Appointment.objects.filter(
            date=appointment_data['date'], 
            time=appointment_data['time']).exists():
            return redirect('checkout')

        appointment = Appointment.objects.create(
            first_name=appointment_data['first_name'],
            last_name=appointment_data['last_name'],
            contact=appointment_data['contact'],
            email=appointment_data['email'],
            date=date.fromisoformat(appointment_data['date']),
            time=time.fromisoformat(appointment_data['time']), 
        )

        product_list = [] 
        total_price = 0
        
        if direct:
            product = Product.objects.get(id=direct['product_id'])
            quantity = int(direct['quantity'])
            subtotal = product.price * quantity
            total_price += subtotal

            AppointmentProduct.objects.create(
                appointment=appointment,
                product=product,
                quantity=quantity,
                price=product.price
            )
                
            product_list.append({ 
                "name": product.product_name, 
                "quantity": quantity, 
                "price": float(product.price), 
                "subtotal": subtotal, 
            })
            
            del request.session['direct_checkout']
        
        else:
            for product_id, produkto in cart.items():
                product = Product.objects.get(id=product_id)
                quantity = produkto["quantity"]
                price = float(produkto["price"])
                subtotal = quantity * price
                total_price += subtotal

                AppointmentProduct.objects.create(
                    appointment=appointment,
                    product=product,
                    quantity=quantity,
                    price=price
                )

                product_list.append({
                    "name": product.product_name,
                    "quantity": quantity,
                    "price": price,
                    "subtotal": subtotal,
                })

            if "cart" in request.session:
                del request.session['cart']

        email_html = render_to_string( 
            'app/buying/appointment_confirmation.html', 
            { 
                "first_name": appointment.first_name, 
                "reference_number": appointment.reference_number, 
                "date": appointment.date, 
                "time": appointment.time, 
                "products": product_list, 
                "total_price": total_price, 
            }
        ) 
            
        send_mail( 
            subject=f"Appointment Confirmation – Ref #{appointment.reference_number}", 
            message="", from_email=settings.EMAIL_HOST_USER, 
            recipient_list=[appointment.email], 
            html_message=email_html, 
        )
            
        del request.session['appointment_data']

        request.session['appointment_complete'] = {
            'reference_number': appointment.reference_number
        }

        return redirect('appointment_complete')

class SellingPage(TemplateView):
    template_name = 'app/selling/selling.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SellingForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = SellingForm(request.POST, request.FILES)
        if form.is_valid():
            selling_appointment = form.save(commit=False)
            selling_appointment.save()

            selling_appointment.reference_number = selling_appointment.reference_number
            selling_appointment.save()

            messages.success(request, 'Selling appointment submitted successfully!')
            request.session['reference_number'] = selling_appointment.reference_number
            return redirect('selling_complete')

        return self.render_to_response({'form': form})

class SellingCompletePage(TemplateView):
    template_name = 'app/selling/selling_complete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reference_number'] = self.request.session.get('reference_number')
        return context

class SellingInfoPage(TemplateView):
    template_name = 'app/selling/selling_information.html'


class MyAppointmentPage(TemplateView):
    template_name = 'app/appointment/my_appointment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        counts = get_appointment_counts(user)
        context.update(counts)

        status_filter = self.request.GET.get('status', '')
        search_query = self.request.GET.get('q', '')

        if user.is_authenticated:
            appointments = Appointment.objects.filter(email=user.email) \
                .exclude(status__in=['Cancelled', 'Finished']) \
                .order_by('-created_at')

            if status_filter:
                appointments = appointments.filter(status=status_filter)

            if search_query:
                appointments = appointments.filter(
                    Q(reference_number__icontains=search_query)
                )

            context['appointments'] = appointments
        else:
            context['appointments'] = []

        return context


class MySellingAppointmentPage(TemplateView):
    template_name = 'app/appointment/my_sellingappointment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        counts = get_appointment_counts(user)
        context.update(counts)

        status_filter = self.request.GET.get('status', '')
        search_query = self.request.GET.get('q', '')

        if user.is_authenticated:
            sellings = Selling.objects.filter(email=user.email) \
                .exclude(status__in=['Cancelled', 'Completed']) \
                .order_by('-selling_date')

            if status_filter:
                sellings = sellings.filter(status=status_filter)

            if search_query:
                sellings = sellings.filter(
                    Q(reference_number__icontains=search_query)
                )

            context['sellings'] = sellings
        else:
            context['sellings'] = []

        return context

class MyCancelledAppointmentPage(TemplateView):
    template_name = 'app/appointment/my_cancelledappointment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        counts = get_appointment_counts(user)
        context.update(counts)

        if user.is_authenticated:
            c1 = Appointment.objects.filter(email=user.email, status="Cancelled")
            c2 = Selling.objects.filter(email=user.email, status="Cancelled")

            cancellation = sorted(
                list(c1) + list(c2),
                key=lambda x: getattr(x, "created_at", getattr(x, "selling_at", None)),
                reverse=True
            )

            context['cancellation'] = cancellation
        else:
            context['cancellation'] = []

        return context

class MyHistoryAppointmentPage(TemplateView):
    template_name = 'app/appointment/my_historyappointment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        status_filter = self.request.GET.get('status', '')
        search_query = self.request.GET.get('q', '')

        if self.request.user.is_authenticated:
            history_appointments = Appointment.objects.filter(email=self.request.user.email, status__in=['Cancelled', 'Finished']).order_by('-created_at')
            history_sellings = Selling.objects.filter(email=self.request.user.email, status__in=['Cancelled', 'Completed']).order_by('-selling_at')
            
            historyappointment = list(history_appointments) + list(history_sellings)
            historyappointment = sorted(historyappointment, key=lambda x: getattr(x, 'created_at', getattr(x, 'selling_at', None)), reverse=True)
            
            if status_filter:
                appointments = appointments.filter(status=status_filter)
        
            if search_query:
                appointments = appointments.filter(
                    Q(reference_number__icontains=search_query) |
                    Q(products__product__product_name__icontains=search_query)
                ).distinct()

            if not historyappointment:
                context['no_history_appointments'] = True  
        else:
            historyappointment = []
            context['no_history_appointments'] = True  

        context['historyappointment'] = historyappointment
        context['status_filter'] = status_filter
        context['search_query'] = search_query
        return context

class CartPage(TemplateView):
    template_name = 'app/cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = self.request.session.get('cart', {})

        for product_id, produkto in cart.items():
            produkto['sub_total'] = produkto['price'] * produkto['quantity']
            produkto['product_id'] = product_id

        context['cart_products'] = cart
        context['total_price'] = sum(produkto['price'] * produkto['quantity'] for produkto in cart.values())
        context['favorites'] = self.request.session.get('favorites', [])
        context['products'] = Product.objects.all().order_by('-id')[:30]
        return context

class FavoritePage(TemplateView):
    template_name = 'app/favorites.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        favorites = self.request.session.get('favorites', [])
        products = Product.objects.filter(id__in=favorites)

        context['products'] = products
        return context

#ADMIN
class AdminDashboard(TemplateView):
    template_name = 'app/admin/admin_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_appointments = Appointment.objects.exclude(status__in=['Cancelled', 'Pending']).count()
        total_trades = Selling.objects.exclude(status__in=['Cancelled', 'Pending']).count()

        today = timezone.now().date()
        appointed = Appointment.objects.filter(status='Pending', created_at__date=today).count()
        traded = Selling.objects.filter(status='Pending', selling_at__date=today).count()

        days = [today - timedelta(days=i) for i in range(6, -1, -1)]

        appointment_chart_labels = []
        appointment_chart_data = []
        selling_chart_labels = []
        selling_chart_data = []

        for day in days:
            appointment_count = Appointment.objects.filter(created_at__date=day).count()
            selling_count = Selling.objects.filter(selling_at__date=day).count()

            appointment_chart_labels.append(day.strftime('%Y-%m-%d'))
            appointment_chart_data.append(appointment_count)

            selling_chart_labels.append(day.strftime('%Y-%m-%d'))
            selling_chart_data.append(selling_count)
        
        categories = Category.objects.all()
        top_categories = []

        for cat in categories:
            sold = AppointmentProduct.objects.filter(product__category_name=cat).aggregate(total=Sum('quantity'))['total'] or 0
            top_categories.append({"category_name": cat.category_name,"total_sold": sold})
            
        total_sales = AppointmentProduct.objects.aggregate(total=Sum(F('quantity') * F('price')))['total'] or 0
        top_categories = sorted(top_categories, key=lambda x: x['total_sold'], reverse=True)
        
        all_orders = []

        for appt in Appointment.objects.filter(status='Pending'):
            delta_days = (timezone.now().date() - appt.date).days
            progress = 100 if delta_days >= 0 else 0

            total_amount = appt.products.aggregate(total=Sum(F('quantity') * F('price')))['total'] or 0

            first_product = appt.products.first()
            product_image = first_product.product.image.url if first_product and first_product.product and first_product.product.image else ""
            
            product_list = ", ".join([f"{p.product.product_name if p.product else 'Unknown Product'} x {p.quantity}" for p in appt.products.all()])

            all_orders.append({
                "type": "Appointment",
                "product": ", ".join([f"{p.product.product_name if p.product else 'Unknown Product'} x {p.quantity}" for p in appt.products.all()]),
                "photo": product_image,
                "product_id": appt.reference_number,
                "amount": total_amount,
                "date": appt.created_at,
                "shipping_progress": progress,
                "status": appt.status,
            })
        
        for sell in Selling.objects.filter(status='Pending'):
            delta_days = (timezone.now().date() - sell.selling_date).days
            progress = 100 if delta_days >= 0 else 0

            all_orders.append({
                "type": "Selling",
                "product": sell.product_name,
                "photo": sell.image.url if sell.image else "",
                "product_id": sell.reference_number,
                "amount": sell.price,
                "date": sell.selling_at,
                "shipping_progress": progress,
                "status": sell.status,
            })
        
        all_orders = sorted(all_orders, key=lambda x: x['date'], reverse=True)
        context['all_orders'] = all_orders

        context['category_labels'] = [c['category_name'] for c in top_categories]
        context['category_data'] = [c['total_sold'] for c in top_categories]
        context['category_list'] = top_categories
        context['chart_labels'] = appointment_chart_labels
        context['appointment_chart_data'] = appointment_chart_data
        context['selling_chart_data'] = selling_chart_data
        context['total_appointments'] = total_appointments
        context['total_trades'] = total_trades
        context['total_sales'] = total_sales
        context['appointed'] = appointed
        context['traded'] = traded
        return context

class AdminInventory(TemplateView):
    template_name = 'app/admin/admin_inventory.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = Product.objects.all()
        categories = Category.objects.all()
        brands = Brand.objects.all()
        
        category_filter = self.request.GET.get('category')
        brand_filter = self.request.GET.get('brand')
        search_query = self.request.GET.get('search')

        if category_filter:
            products = products.filter(category_name__id=category_filter)
        if brand_filter:
            products = products.filter(brand__id=brand_filter)
        if search_query:
            products = products.filter(product_name__icontains=search_query)

        context['products'] = products
        context['categories'] = categories
        context['brands'] = brands
        context['category_filter'] = category_filter
        context['brand_filter'] = brand_filter
        context['search_query'] = search_query
        return context

class AdminProduct(TemplateView):
    template_name = 'app/admin/admin_product.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['brands'] = Brand.objects.all()

        search_query = self.request.GET.get('search', '').strip()
        category_filter = self.request.GET.get('category', '').strip()
        brand_filter = self.request.GET.get('brand', '').strip()
        products = Product.objects.all()

        if search_query:
            products = products.filter(
                Q(category_name__category_name__icontains=search_query) |
                Q(brand__brand__icontains=search_query) |
                Q(product_name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(price__icontains=search_query) |
                Q(stock__icontains=search_query)
            )
        if category_filter:
            products = products.filter(category_name__id=category_filter)
        if brand_filter:
            products = products.filter(brand__id=brand_filter)
        
        context['products'] = Product.objects.prefetch_related('images').all()
        
        context['form'] = Add()
        context['category_form'] = AddCategory
        context['brand_form'] = AddBrand
        context['variant_form'] = AddVariantForm
        context['search_query'] = search_query
        context['category_filter'] = category_filter
        context['brand_filter'] = brand_filter
        return context

class AdminAppointment(TemplateView):
    template_name = 'app/admin/admin_appointment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('search', '')
        status_filter = self.request.GET.get('status', '')
        appointments = Appointment.objects.all()

        if search_query:
            appointments = appointments.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(reference_number__icontains=search_query) |
                Q(email__icontains=search_query)
            )

        if status_filter:
            appointments = appointments.filter(status=status_filter)

        context['appointments'] = appointments
        context['search_query'] = search_query
        context['status_filter'] = status_filter
        return context

class AdminSellingAppointment(TemplateView):
    template_name = 'app/admin/admin_selling.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('search', '')
        status_filter = self.request.GET.get('status', '')
        sellings = Selling.objects.all()

        if search_query:
            sellings = sellings.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(reference_number__icontains=search_query) |
                Q(email__icontains=search_query)
            )

        if status_filter:
            sellings = sellings.filter(status=status_filter)

        context['sellings'] = sellings
        context['search_query'] = search_query
        context['status_filter'] = status_filter
        return context