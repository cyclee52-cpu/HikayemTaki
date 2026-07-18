from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.urls import reverse

from products.models import Category, Product


HOME_PRODUCT_VISIBLE_COUNT = 8
HOME_PRODUCT_POOL_LIMIT = 32
PRODUCT_ROTATION_INTERVAL = 20000


CORPORATE_PAGES = {
    "story": {
        "eyebrow": "Nihan & Eda'nın Hikâyesi",
        "title": "Bir arkadaşlıktan doğan ortak hikâye.",
        "description": "Nihan ve Eda'nın aynı iş yerinde başlayan arkadaşlıklarının, ortak takı tutkusu ve Bir Hikayem deneyimiyle Hikayem Takı'ya dönüşen öyküsü.",
        "lead": "Aynı iş yerinde başlayan bir arkadaşlık, yaklaşık bir yıl içinde abla-kardeş sıcaklığında bir bağa; ortak bir tutku ise birlikte kurulan bir hayale dönüştü.",
        "sections": [
            {
                "heading": "Aynı yerde başlayan yakınlık",
                "paragraphs": [
                    "Nihan ve Eda'nın yolu aynı iş yerinde kesişti. İş arkadaşlığıyla başlayan tanışıklıkları, birbirlerini daha yakından tanıdıkça kısa sürede güçlü bir dostluğa dönüştü.",
                    "Yaklaşık bir yıllık arkadaşlıkları, zamanla birbirini anlayan, destekleyen ve tamamlayan bir abla-kardeş bağına ulaştı. Hikayem Takı'nın temelinde de tam olarak bu güven ve birlikte büyüme duygusu var.",
                ],
            },
            {
                "heading": "“Birlikte bir iş kurmalıyız”",
                "paragraphs": [
                    "İkisini buluşturan yalnızca dostlukları değildi. Takılara duydukları ortak ilgi, zarif parçaları keşfetme heyecanı ve bu şıklığı başkalarıyla paylaşma isteği, birlikte kurabilecekleri işin yönünü gösterdi.",
                    "Bir gün dile gelen ‘Birlikte bir iş kurmalıyız’ düşüncesi, ortak zevklerinin ve birbirlerine duydukları güvenin üzerinde büyüdü. Böylece bir fikir, adım adım gerçeğe; iki arkadaşın ortak hikâyesi ise Hikayem Takı'ya dönüştü.",
                ],
            },
            {
                "heading": "İsmimizin taşıdığı hikâye",
                "paragraphs": [
                    "Hikayem Takı ismi, Nihan'ın daha önce yürüttüğü Bir Hikayem organizasyon işinden izler taşıyor. Bir Hikayem, insanların evlilik yolculuğuna hazırlanırken yazdıkları ilk hikâyelere eşlik ediyordu.",
                    "Bugün bu anlam, takılarla yaşamaya devam ediyor. Çünkü bazen bir hikâye bir buluşmayla, bazen yeni bir başlangıçla, bazen de yıllarca saklanacak küçük bir takıyla başlar. Hikayem Takı, insanların kendi hikâyelerinin en başındaki o değerli anlara ulaşmak ve onlara eşlik etmek için bu ismi taşıyor.",
                ],
            },
            {
                "heading": "Şimdi sıra sizin hikâyenizde",
                "paragraphs": [
                    "Nihan ve Eda için Hikayem Takı yalnızca bir iş değil; dostluklarının, ortak tutkularının ve birlikte cesaret etmelerinin somut hâli. Koleksiyondaki her parça da bir stile eşlik etmenin ötesinde, onu seçen kişinin anılarında kendine küçük bir yer bulsun diye özenle seçiliyor.",
                    "Bizim hikâyemiz iki arkadaşla başladı. Bundan sonrası, takılarımızı kendi anlarının parçası yapan herkesle birlikte yazılıyor.",
                ],
                "bullets": [
                    "Dostluktan doğan samimi bir marka",
                    "Ortak takı tutkusuyla oluşturulan zarif bir seçki",
                    "Her müşterinin kendi hikâyesine eşlik etme arzusu",
                ],
            },
        ],
    },
    "shipping": {
        "eyebrow": "Sipariş desteği",
        "title": "Kargo ve Teslimat",
        "description": "Hikayem Takı siparişlerinin hazırlanması, kargoya verilmesi ve teslimat süreci hakkında genel bilgilendirme.",
        "lead": "Sipariş ve ödeme işlemleri Shopier mağazamız üzerinden tamamlanır. Siparişinizle ilgili güncel bilgiler, satış kanalı ve sipariş bildirimi üzerinden paylaşılır.",
        "sections": [
            {
                "heading": "Siparişin hazırlanması",
                "paragraphs": [
                    "Sipariş bilgileri bize ulaştıktan sonra ürünler kontrol edilir ve gönderime uygun biçimde paketlenir. Hazırlık süresi; sipariş zamanı, ürün durumu ve yoğunluğa göre değişebilir."
                ],
            },
            {
                "heading": "Kargo süreci",
                "paragraphs": [
                    "Kargo firması, ücret ve tahmini teslimat bilgileri sipariş sırasında veya sipariş sonrasında iletilen bilgilendirmede yer alır. Resmî tatiller, kampanya dönemleri, bölgesel koşullar ve taşıyıcı operasyonları teslimat süresini etkileyebilir."
                ],
            },
            {
                "heading": "Teslim alırken",
                "paragraphs": [
                    "Pakette belirgin bir hasar fark ederseniz teslimat anında taşıyıcının yönlendirmesini izleyin ve mümkünse durumu kayıt altına alın. Ardından sipariş bilginizle birlikte bizimle iletişime geçin."
                ],
            },
        ],
        "note": "Siparişinize özel en güncel bilgi için Shopier sipariş kaydınızı esas alın.",
    },
    "returns": {
        "eyebrow": "Sipariş desteği",
        "title": "İade ve Değişim",
        "description": "Hikayem Takı siparişlerinde iade ve değişim talebi oluştururken izlenmesi gereken temel adımlar.",
        "lead": "Bir talebiniz olduğunda ürünü göndermeden önce bize ulaşmanız, siparişinizi doğru biçimde inceleyebilmemiz için önemlidir.",
        "sections": [
            {
                "heading": "Talep nasıl oluşturulur?",
                "paragraphs": [
                    "Shopier sipariş bilginiz, talebinizin nedeni ve ürünün güncel durumunu açıklayan kısa bir notla bize ulaşın. Gerekli görülürse ürünü ve paketi gösteren fotoğraflar istenebilir."
                ],
            },
            {
                "heading": "Ürünü koruyun",
                "paragraphs": [
                    "İnceleme tamamlanana kadar ürünü, aksesuarlarını ve paket içeriğini koruyun. Önceden yönlendirme almadan gönderim yapmayın; gönderi bilgileri talebin niteliğine göre paylaşılır."
                ],
            },
            {
                "heading": "Değerlendirme",
                "paragraphs": [
                    "Talepler sipariş bilgileri, ürünün durumu, Shopier süreci ve yürürlükteki tüketici mevzuatı çerçevesinde değerlendirilir. Sonuç ve izlenecek adımlar sizinle paylaşılır."
                ],
            },
        ],
        "note": "Bu sayfa genel bilgilendirme amaçlıdır; sipariş sırasında sunulan sözleşme ve satış koşullarının yerine geçmez.",
    },
    "privacy": {
        "eyebrow": "Şeffaflık",
        "title": "Gizlilik Politikası",
        "description": "Hikayem Takı web sitesinde kullanılan temel trafik, güvenlik ve yönlendirme verileri hakkında bilgilendirme.",
        "lead": "Bu sayfa, hikayemtaki.com ziyaretiniz sırasında hangi teknik araçların kullanıldığını ve satın alma sürecinin nasıl yönlendirildiğini açıklar.",
        "sections": [
            {
                "heading": "Site kullanımı",
                "paragraphs": [
                    "Site güvenliği ve teknik işleyiş için IP adresi, tarayıcı türü, ziyaret zamanı ve talep edilen sayfa gibi standart sunucu kayıtları sınırlı süreyle işlenebilir."
                ],
            },
            {
                "heading": "Analiz araçları",
                "paragraphs": [
                    "Site performansını ve kullanıcı deneyimini geliştirmek amacıyla Google Analytics ve Microsoft Clarity kullanılmaktadır. Bu araçlar ziyaret, sayfa görüntüleme ve site içi etkileşimlere ilişkin teknik veriler oluşturabilir."
                ],
            },
            {
                "heading": "Sipariş ve ödeme",
                "paragraphs": [
                    "Web sitemiz ürünleri tanıtır ve satın alma işlemi için Shopier mağazasına yönlendirir. Ödeme ve sipariş sırasında Shopier'e ilettiğiniz bilgiler, Shopier'in kendi koşulları ve gizlilik uygulamaları kapsamında işlenir."
                ],
            },
            {
                "heading": "Dış bağlantılar",
                "paragraphs": [
                    "Instagram, Shopier ve blog gibi dış bağlantılar kendi gizlilik politikalarına tabidir. Bu sayfa gerektiğinde site araçları ve uygulamalarındaki değişikliklere göre güncellenebilir."
                ],
            },
        ],
        "note": "Son güncelleme: 18 Temmuz 2026. Gizlilikle ilgili sorularınız için İletişim sayfasındaki kanalları kullanabilirsiniz.",
    },
    "faq": {
        "eyebrow": "Yardım merkezi",
        "title": "Sıkça Sorulan Sorular",
        "description": "Hikayem Takı sipariş, ödeme, teslimat, ürün bilgisi ve bakım konularında sıkça sorulan sorular.",
        "lead": "Sipariş öncesinde ve sonrasında en çok merak edilen konuları kısa ve açık cevaplarla bir araya getirdik.",
        "sections": [
            {
                "heading": "Nasıl sipariş verebilirim?",
                "paragraphs": [
                    "Ürün sayfasındaki Shopier üzerinden satın alma bağlantısını kullanarak ilgili ürünün güvenli sipariş ekranına geçebilirsiniz."
                ],
            },
            {
                "heading": "Ödeme seçeneklerini nerede görürüm?",
                "paragraphs": [
                    "Güncel ödeme seçenekleri ve varsa taksit bilgileri Shopier ödeme ekranında gösterilir."
                ],
            },
            {
                "heading": "Siparişimin durumunu nasıl öğrenirim?",
                "paragraphs": [
                    "Shopier sipariş bildiriminizi kontrol edebilir veya sipariş bilginizle Instagram üzerinden bize ulaşabilirsiniz."
                ],
            },
            {
                "heading": "Takılarımın bakımını nasıl yapmalıyım?",
                "paragraphs": [
                    "Öncelikle ürüne özel bakım bilgisini esas alın. Genel olarak parfüm ve bakım ürünlerini takıdan önce uygulamak, kullanım sonrası yumuşak kuru bezle silmek ve parçaları ayrı saklamak iyi bir alışkanlıktır."
                ],
            },
            {
                "heading": "Ürün rengi ekranda farklı görünebilir mi?",
                "paragraphs": [
                    "Ekran ayarları, ışık ve çekim koşulları tonların farklı algılanmasına neden olabilir. Ürün açıklaması ve görsellerini birlikte değerlendirmenizi öneririz."
                ],
            },
        ],
    },
    "contact": {
        "eyebrow": "Size yardımcı olalım",
        "title": "İletişim",
        "description": "Hikayem Takı ürünleri ve siparişleri hakkında Instagram veya Shopier üzerinden iletişime geçin.",
        "lead": "Ürünler, siparişler veya iş birliği talepleri için aşağıdaki resmî kanallardan bize ulaşabilirsiniz.",
        "sections": [
            {
                "heading": "Instagram",
                "paragraphs": [
                    "Ürün ve genel sorularınız için @hikayemtaki hesabımıza doğrudan mesaj gönderebilirsiniz."
                ],
            },
            {
                "heading": "Shopier",
                "paragraphs": [
                    "Siparişle ilgili taleplerinizde sipariş numaranızı belirterek Shopier sipariş kaydı üzerinden iletişim kurabilirsiniz."
                ],
            },
            {
                "heading": "Yanıtınızı hızlandırın",
                "paragraphs": [
                    "Mesajınıza ürün adını veya bağlantısını, siparişle ilgiliyse sipariş numarasını ve talebinizin kısa açıklamasını ekleyin. Hassas ödeme bilgilerini sosyal medya mesajıyla paylaşmayın."
                ],
            },
        ],
        "actions": [
            {
                "label": "Instagram'da mesaj gönder",
                "url": "https://www.instagram.com/hikayemtaki/",
            },
            {
                "label": "Shopier mağazasına git",
                "url": "https://www.shopier.com/hikayemtaki",
            },
        ],
    },
}


def get_category_url(*keywords):
    query = Q()

    for keyword in keywords:
        query |= Q(name__icontains=keyword)
        query |= Q(slug__icontains=keyword)

    category = Category.objects.filter(is_active=True).filter(query).first()

    if not category:
        return reverse("products:list")

    return f"{reverse('products:list')}?category={category.slug}"



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


def corporate_page(request, page_key):
    page = CORPORATE_PAGES.get(page_key)

    if page is None:
        raise Http404

    return render(request, "core/corporate_page.html", {"page": page})
