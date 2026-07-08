from django.shortcuts import render

from products.models import Product


def home(request):
    featured_products = (
        Product.objects.filter(is_active=True)
        .select_related("category")
        .order_by("-created_at")[:8]
    )

    context = {
        "featured_products": featured_products,
    }

    return render(request, "core/home.html", context)