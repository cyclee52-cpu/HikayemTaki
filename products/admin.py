from django.contrib import admin

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price",
        "stock",
        "has_shopier_url",
        "is_active",
        "created_at",
    )
    list_filter = ("category", "is_active")
    search_fields = ("name", "description", "shopier_url")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Ürün Bilgileri", {
            "fields": (
                "category",
                "name",
                "slug",
                "description",
                "price",
                "stock",
                "image",
                "shopier_url",
            )
        }),
        ("Durum", {
            "fields": (
                "is_active",
            )
        }),
        ("Tarihler", {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )

    @admin.display(description="Shopier Link")
    def has_shopier_url(self, obj):
        return "Var" if obj.shopier_url else "Yok"