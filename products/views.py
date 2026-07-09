from django.shortcuts import get_object_or_404, render

from .models import Category, Product


def product_list(request):
    selected_category_slug = request.GET.get("category")

    categories = Category.objects.filter(is_active=True).order_by("name")

    selected_category = None
    grouped_categories = []

    if selected_category_slug:
        selected_category = get_object_or_404(
            Category,
            slug=selected_category_slug,
            is_active=True,
        )

        products = (
            Product.objects.filter(
                category=selected_category,
                is_active=True,
            )
            .select_related("category")
            .order_by("-created_at")
        )

        grouped_categories.append(
            {
                "category": selected_category,
                "products": products,
            }
        )

    else:
        for category in categories:
            products = (
                Product.objects.filter(
                    category=category,
                    is_active=True,
                )
                .select_related("category")
                .order_by("-created_at")
            )

            if products.exists():
                grouped_categories.append(
                    {
                        "category": category,
                        "products": products,
                    }
                )

    context = {
        "categories": categories,
        "selected_category": selected_category,
        "grouped_categories": grouped_categories,
    }

    return render(request, "products/list.html", context)


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
        .select_related("category")
        .order_by("-created_at")[:4]
    )

    context = {
        "product": product,
        "related_products": related_products,
    }

    return render(request, "products/detail.html", context)