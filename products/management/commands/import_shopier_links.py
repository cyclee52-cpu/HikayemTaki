from django.core.management.base import BaseCommand
from products.models import Product


SHOPIER_LINKS = {
    "Sedef Deniz Kabuğu Gold Bileklik": "https://www.shopier.com/hikayemtaki/48754686",
    "Luna Clover Işıltısı Çelik Bileklik – Sedef Detaylı Zirkon Taşlı": "https://www.shopier.com/hikayemtaki/48756602",
    "Blue Butterfly Tennis Bileklik": "https://www.shopier.com/hikayemtaki/48756575",
    "Blue Butterfly Tennis Bileklik Silver": "https://www.shopier.com/hikayemtaki/48756591",
    "Star Tennis Çelik Bileklik – Zirkon Taşlı Gold": "https://www.shopier.com/hikayemtaki/48756610",
    "Star Tennis Çelik Bileklik – Zirkon Taşlı Silver": "https://www.shopier.com/hikayemtaki/48756623",
    "Çift Taraflı Sedef Çiçek Gold Bileklik": "https://www.shopier.com/hikayemtaki/48756046",
    "Mint Işıltı Gold Kelepçe Bileklik Turuncu": "https://www.shopier.com/hikayemtaki/48754802",
    "Mint Işıltı Gold Kelepçe Bileklik Yeşil": "https://www.shopier.com/hikayemtaki/48754792",
    "Mint Işıltı Gold Kelepçe Bileklik Renkli": "https://www.shopier.com/hikayemtaki/48754810",
    "Blush Aura Gold Ayarlanabilir Yüzük": "https://www.shopier.com/hikayemtaki/48756374",
    "Mint Aura Gold Ayarlanabilir Yüzük Yeşil": "https://www.shopier.com/hikayemtaki/48756399",
    "Pastel Harmony Gold Ayarlanabilir Yüzük Renkli": "https://www.shopier.com/hikayemtaki/48756389",
    "Deniz Yıldızı Gold Ayarlanabilir Yüzük": "https://www.shopier.com/hikayemtaki/48756152",
    "Modern Gold Ayarlanabilir Yüzük": "https://www.shopier.com/hikayemtaki/48756167",
    "Aura Gold Ayarlanabilir Yüzük": "https://www.shopier.com/hikayemtaki/48756249",
    "Harmony Çift Renk Ayarlanabilir Yüzük": "https://www.shopier.com/hikayemtaki/48756182",
    "Silver ÇayFincanı Rozet": "https://www.shopier.com/hikayemtaki/48756102",
    "Kırmızı Kahve Fincanı Gold Rozet": "https://www.shopier.com/hikayemtaki/48756079",
    "Aurora Güneş Katmanlı Kolye Gold": "https://www.shopier.com/hikayemtaki/48755699",
    "Aurora Güneş Katmanlı Kolye Silver": "https://www.shopier.com/hikayemtaki/48755640",
    "Galaksi Gold Kolye": "https://www.shopier.com/hikayemtaki/48755833",
    "Galaksi Silver Kolye": "https://www.shopier.com/hikayemtaki/48755790",
    "Şans Yoncası Gold Kolye": "https://www.shopier.com/hikayemtaki/48755754",
    "Love Charm 6'lı Gold Küpe Seti": "https://www.shopier.com/hikayemtaki/48756413",
    "Luna Blossom 3'lü Gold Küpe Seti": "https://www.shopier.com/hikayemtaki/48756404",
    "Sedef Aura Gold Küpe": "https://www.shopier.com/hikayemtaki/48756117",
    "Mercan Nautilus Gold Küpe": "https://www.shopier.com/hikayemtaki/48754723",
    "Mint Deniz Kabuğu Gold Detaylı Küpe": "https://www.shopier.com/hikayemtaki/48754641",
}


class Command(BaseCommand):
    help = "Shopier ürün linklerini ürünlere ekler."

    def handle(self, *args, **options):
        updated_count = 0
        not_found = []

        for product_name, shopier_url in SHOPIER_LINKS.items():
            product = Product.objects.filter(name__iexact=product_name).first()

            if not product:
                not_found.append(product_name)
                continue

            product.shopier_url = shopier_url
            product.save(update_fields=["shopier_url"])
            updated_count += 1

        self.stdout.write(self.style.SUCCESS(f"{updated_count} ürün güncellendi."))

        if not_found:
            self.stdout.write(self.style.WARNING("Eşleşmeyen ürünler:"))
            for name in not_found:
                self.stdout.write(f"- {name}")