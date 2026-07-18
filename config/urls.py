from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from core import views
from core.sitemaps import ProductSitemap, StaticViewSitemap


sitemaps = {
    "static": StaticViewSitemap,
    "products": ProductSitemap,
}



urlpatterns = [
    path("admin/", admin.site.urls),

    path("robots.txt", views.robots_txt, name="robots_txt"),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),

    path("", views.home, name="home"),
    path("hikayemiz/", views.corporate_page, {"page_key": "story"}, name="story"),
    path("kargo-ve-teslimat/", views.corporate_page, {"page_key": "shipping"}, name="shipping"),
    path("iade-ve-degisim/", views.corporate_page, {"page_key": "returns"}, name="returns"),
    path("gizlilik-politikasi/", views.corporate_page, {"page_key": "privacy"}, name="privacy"),
    path("sikca-sorulan-sorular/", views.corporate_page, {"page_key": "faq"}, name="faq"),
    path("iletisim/", views.corporate_page, {"page_key": "contact"}, name="contact"),

    path("products/", include("products.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
