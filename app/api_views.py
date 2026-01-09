# API endpoint for getting product 3D model data
# Add this to your views.py or create a separate api_views.py file

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q
from .models import Product

@require_http_methods(["GET"])
def api_product_3d_model(request, product_id):
    """
    API endpoint to get product 3D model and details
    Returns: {
        "success": true/false,
        "product_id": id,
        "product_name": name,
        "model_url": "/media/3d_models/...",
        "description": "...",
        "price": 0.00,
        "brand": "...",
        "has_model": true/false
    }
    """
    try:
        product = get_object_or_404(Product, id=product_id)
        
        model_url = None
        has_model = False
        
        if product.model_3d:
            model_url = request.build_absolute_uri(product.model_3d.url)
            has_model = True
        
        return JsonResponse({
            "success": True,
            "product_id": product.id,
            "product_name": product.product_name,
            "model_url": model_url,
            "description": product.description or "",
            "price": str(product.price),
            "brand": product.brand.brand if product.brand else "Unknown",
            "has_model": has_model,
            "component_type": product.component_type,
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=400)

@require_http_methods(["GET"])
def api_search_products_with_3d(request):
    """
    Search products that have 3D models
    Query params:
    - q: search query
    - component: filter by component type
    - limit: max results (default 50)
    """
    search_query = request.GET.get('q', '')
    component = request.GET.get('component', '')
    limit = int(request.GET.get('limit', 50))
    
    products = Product.objects.filter(model_3d__isnull=False).exclude(model_3d='')
    
    if search_query:
        products = products.filter(
            Q(product_name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    if component:
        products = products.filter(component_type=component)
    
    results = []
    for p in products[:limit]:
        results.append({
            "id": p.id,
            "product_name": p.product_name,
            "price": str(p.price),
            "brand": p.brand.brand if p.brand else "Unknown",
            "component_type": p.component_type,
            "description": p.description or "",
            "has_model": True,
            "model_url": p.model_3d.url if p.model_3d else None,
        })
    
    return JsonResponse({
        "success": True,
        "products": results,
        "total": len(results)
    })
