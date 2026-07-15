from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from products.models import Product


class StaticViewSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return ["home", "products:list"]

    def location(self, item):
        return reverse(item)


class ProductSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Product.objects.filter(is_active=True).order_by("-updated_at")

    def location(self, item):
        return reverse("products:detail", kwargs={"slug": item.slug})

    def lastmod(self, item):
        return item.updated_at
