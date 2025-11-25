from .models import Product

def favorites_context(request):
    favorites = request.session.get('favorites', [])
    products = Product.objects.filter(id__in=favorites)
    return {
        'products_favorite': products
    }
