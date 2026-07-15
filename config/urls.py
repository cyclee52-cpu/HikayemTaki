from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from django.urls import include, path

from core import views
from core.sitemaps import ProductSitemap, StaticViewSitemap


sitemaps = {
    "static": StaticViewSitemap,
    "products": ProductSitemap,
}


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "",
        "Sitemap: https://hikayemtaki.com/sitemap.xml",
    ]
    return HttpResponse(
        "\n".join(lines),
        content_type="text/plain; charset=utf-8",
    )


urlpatterns = [
    path("admin/", admin.site.urls),

    path("robots.txt", robots_txt, name="robots_txt"),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),

    path("", views.home, name="home"),

    path("products/", include("products.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
