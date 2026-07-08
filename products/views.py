from django.shortcuts import get_object_or_404, render

from .models import Product


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("category"),
        slug=slug,
        is_active=True,
    )

    related_products = (
        Product.objects.filter(
            category=product.category,
            is_active=True,
        )
        .exclude(id=product.id)
        .order_by("-created_at")[:4]
    )

    context = {
        "product": product,
        "related_products": related_products,
    }

    return render(request, "products/detail.html", context)