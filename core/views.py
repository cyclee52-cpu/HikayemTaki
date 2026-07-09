from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse

from products.models import Category, Product


HOME_PRODUCT_VISIBLE_COUNT = 8
HOME_PRODUCT_POOL_LIMIT = 32
PRODUCT_ROTATION_INTERVAL = 20000


def get_category_url(*keywords):
    query = Q()

    for keyword in keywords:
        query |= Q(name__icontains=keyword)
        query |= Q(slug__icontains=keyword)

    category = Category.objects.filter(is_active=True).filter(query).first()

    if not category:
        return reverse("products:list")

    return f"{reverse('products:list')}?category={category.slug}"


def home(request):
    featured_products = (
        Product.objects.filter(is_active=True)
        .select_related("category")
        .order_by("-created_at")[:HOME_PRODUCT_POOL_LIMIT]
    )

    collection_urls = {
        "new": reverse("products:list"),
        "earrings": get_category_url("küpe", "kupe"),
        "necklaces": get_category_url("kolye"),
        "rings": get_category_url("yüzük", "yuzuk"),
    }

    context = {
        "featured_products": featured_products,
        "collection_urls": collection_urls,
        "home_product_visible_count": HOME_PRODUCT_VISIBLE_COUNT,
        "product_rotation_interval": PRODUCT_ROTATION_INTERVAL,
    }

    return render(request, "core/home.html", context)