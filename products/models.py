from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True, verbose_name="Kategori Adı")
    slug = models.SlugField(max_length=140, unique=True, blank=True, db_index=True)
    description = models.TextField(blank=True, verbose_name="Açıklama")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        verbose_name = "Kategori"
        verbose_name_plural = "Kategoriler"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
        verbose_name="Kategori",
    )
    name = models.CharField(max_length=160, verbose_name="Ürün Adı")
    slug = models.SlugField(max_length=180, unique=True, blank=True, db_index=True)
    description = models.TextField(blank=True, verbose_name="Ürün Açıklaması")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Fiyat")
    stock = models.PositiveIntegerField(default=0, verbose_name="Stok")
    image = models.ImageField(upload_to="products/", blank=True, null=True, verbose_name="Ana Görsel")

    shopier_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name="Shopier Ürün Linki",
        help_text="Ürünün Shopier satış linkini buraya ekleyin.",
    )

    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        verbose_name = "Ürün"
        verbose_name_plural = "Ürünler"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="gallery_images",
        verbose_name="Ürün",
    )
    image = models.ImageField(upload_to="products/gallery/", verbose_name="Galeri Görseli")
    alt_text = models.CharField(max_length=180, blank=True, verbose_name="Alternatif Metin")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="Sıralama")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")

    class Meta:
        verbose_name = "Ürün Galeri Görseli"
        verbose_name_plural = "Ürün Galeri Görselleri"
        ordering = ["sort_order", "created_at"]

    def __str__(self):
        return f"{self.product.name} - Galeri Görseli"