from decimal import Decimal

from django.core.management.base import BaseCommand

from products.models import Category, Product


class Command(BaseCommand):
    help = "Hikayem Takı başlangıç ürünlerini içeri aktarır."

    def handle(self, *args, **options):
        products = [
            ("Sedef Deniz Kabuğu Gold Bileklik", "Bileklik", 4, "385.00"),
            ("Luna Clover Işıltısı Çelik Bileklik – Sedef Detaylı Zirkon Taşlı", "Bileklik", 5, "350.00"),
            ("Blue Butterfly Tennis Bileklik", "Bileklik", 5, "350.00"),
            ("Blue Butterfly Tennis Bileklik Silver", "Bileklik", 5, "350.00"),
            ("Star Tennis Çelik Bileklik – Zirkon Taşlı Gold", "Bileklik", 5, "470.00"),
            ("Star Tennis Çelik Bileklik – Zirkon Taşlı Silver", "Bileklik", 5, "470.00"),
            ("Çift Taraflı Sedef Çiçek Gold Bileklik", "Bileklik", 5, "660.00"),
            ("Mint Işıltı Gold Kelepçe Bileklik Turuncu", "Kelepçe", 5, "605.00"),
            ("Mint Işıltı Gold Kelepçe Bileklik Yeşil", "Kelepçe", 5, "605.00"),
            ("Mint Işıltı Gold Kelepçe Bileklik Renkli", "Kelepçe", 4, "605.00"),
            ("Blush Aura Gold Ayarlanabilir Yüzük", "Yüzük", 4, "279.00"),
            ("Mint Aura Gold Ayarlanabilir Yüzük Yeşil", "Yüzük", 3, "279.00"),
            ("Pastel Harmony Gold Ayarlanabilir Yüzük Renkli", "Yüzük", 5, "279.00"),
            ("Deniz Yıldızı Gold Ayarlanabilir Yüzük", "Yüzük", 5, "279.00"),
            ("Modern Gold Ayarlanabilir Yüzük", "Yüzük", 3, "279.00"),
            ("Aura Gold Ayarlanabilir Yüzük", "Yüzük", 3, "279.00"),
            ("Harmony Çift Renk Ayarlanabilir Yüzük", "Yüzük", 3, "279.00"),
            ("Silver ÇayFincanı Rozet", "Broş", 3, "300.00"),
            ("Kırmızı Kahve Fincanı Gold Rozet", "Broş", 2, "300.00"),
            ("Aurora Güneş Katmanlı Kolye Gold", "Kolye", 5, "330.00"),
            ("Aurora Güneş Katmanlı Kolye Silver", "Kolye", 5, "330.00"),
            ("Galaksi Gold Kolye", "Kolye", 4, "385.00"),
            ("Galaksi Silver Kolye", "Kolye", 5, "385.00"),
            ("Şans Yoncası Gold Kolye", "Kolye", 5, "440.00"),
            ("Love Charm 6'lı Gold Küpe Seti", "Küpe", 5, "550.00"),
            ("Luna Blossom 3'lü Gold Küpe Seti", "Küpe", 5, "280.00"),
            ("Sedef Aura Gold Küpe", "Küpe", 5, "280.00"),
            ("Mercan Nautilus Gold Küpe", "Küpe", 5, "260.00"),
            ("Mint Deniz Kabuğu Gold Detaylı Küpe", "Küpe", 5, "225.00"),
        ]

        created_count = 0
        updated_count = 0

        for name, category_name, stock, price in products:
            category, _ = Category.objects.get_or_create(
                name=category_name.strip(),
                defaults={"is_active": True},
            )

            product, created = Product.objects.update_or_create(
                name=name.strip(),
                defaults={
                    "category": category,
                    "price": Decimal(price),
                    "stock": stock,
                    "is_active": True,
                },
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"{created_count} ürün eklendi, {updated_count} ürün güncellendi."
            )
        )