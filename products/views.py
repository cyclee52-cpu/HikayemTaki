import json

from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.text import Truncator

from .models import Category, Product


SITE_URL = "https://hikayemtaki.com"
DEFAULT_PRODUCT_DESCRIPTION = (
    "Zarif detaylarıyla günlük şıklığını tamamlayan, "
    "Hikayem Takı koleksiyonundan özel bir parça."
)


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

    products_url = f"{SITE_URL}{reverse('products:list')}"

    if selected_category:
        seo_title = f"{selected_category.name} Koleksiyonu | Hikayem Takı"
        seo_description = (
            f"{selected_category.name} koleksiyonunu keşfedin. "
            "Kararmaya dayanıklı, zarif ve modern çelik takılar Hikayem Takı'da."
        )
        seo_robots = "noindex, follow"
    else:
        seo_title = "Çelik Takı Koleksiyonları | Hikayem Takı"
        seo_description = (
            "Kararmaya dayanıklı çelik küpe, kolye, bileklik ve yüzük "
            "koleksiyonlarını keşfedin. Zarif tasarımlar Hikayem Takı'da."
        )
        seo_robots = (
            "index, follow, max-image-preview:large, "
            "max-snippet:-1, max-video-preview:-1"
        )

    context = {
        "categories": categories,
        "selected_category": selected_category,
        "grouped_categories": grouped_categories,
        "seo_title": seo_title,
        "seo_description": seo_description,
        "seo_robots": seo_robots,
        "products_url": products_url,
    }

    return render(request, "products/list.html", context)


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("category"),
        slug=slug,
        is_active=True,
    )

    gallery_images = product.gallery_images.filter(is_active=True)

    related_products = (
        Product.objects.filter(
            category=product.category,
            is_active=True,
        )
        .exclude(id=product.id)
        .select_related("category")
        .order_by("-created_at")[:4]
    )

    raw_description = product.description or DEFAULT_PRODUCT_DESCRIPTION
    seo_description = Truncator(strip_tags(raw_description)).chars(160)

    product_url = f"{SITE_URL}{reverse('products:detail', kwargs={'slug': product.slug})}"
    products_url = f"{SITE_URL}{reverse('products:list')}"

    product_image_url = None

    if product.image:
        product_image_url = request.build_absolute_uri(product.image.url)
    else:
        first_gallery_image = gallery_images.first()

        if first_gallery_image:
            product_image_url = request.build_absolute_uri(
                first_gallery_image.image.url
            )

    product_schema = {
        "@context": "https://schema.org",
        "@type": "Product",
        "@id": f"{product_url}#product",
        "name": product.name,
        "description": seo_description,
        "sku": product.slug,
        "url": product_url,
        "brand": {
            "@type": "Brand",
            "name": "Hikayem Takı",
        },
        "offers": {
            "@type": "Offer",
            "url": product_url,
            "priceCurrency": "TRY",
            "price": str(product.price),
            "availability": (
                "https://schema.org/InStock"
                if product.stock > 0
                else "https://schema.org/OutOfStock"
            ),
            "itemCondition": "https://schema.org/NewCondition",
            "seller": {
                "@id": f"{SITE_URL}/#organization",
            },
        },
    }

    if product.category:
        product_schema["category"] = product.category.name

    if product_image_url:
        product_schema["image"] = [product_image_url]

    breadcrumb_schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "name": "Ana Sayfa",
                "item": f"{SITE_URL}/",
            },
            {
                "@type": "ListItem",
                "position": 2,
                "name": "Tüm Ürünler",
                "item": products_url,
            },
            {
                "@type": "ListItem",
                "position": 3,
                "name": product.name,
                "item": product_url,
            },
        ],
    }

    context = {
        "product": product,
        "gallery_images": gallery_images,
        "related_products": related_products,
        "seo_description": seo_description,
        "product_url": product_url,
        "product_image_url": product_image_url,
        "product_schema_json": json.dumps(
            product_schema,
            ensure_ascii=False,
        ),
        "breadcrumb_schema_json": json.dumps(
            breadcrumb_schema,
            ensure_ascii=False,
        ),
    }

    return render(request, "products/detail.html", context)
