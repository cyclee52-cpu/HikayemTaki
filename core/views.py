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
        "eyebrow": "Hikayem Takı",
        "title": "Her takının bir hikâyesi var.",
        "description": "Hikayem Takı'nın zarif, modern ve günlük kullanıma uygun parçaları seçme yaklaşımını keşfedin.",
        "lead": "Hikayem Takı, günlük hayatın küçük anlarına eşlik eden zarif parçaları ulaşılabilir bir seçkiyle buluşturmak için kuruldu.",
        "sections": [
            {
                "heading": "Bizim hikâyemiz",
                "paragraphs": [
                    "Bir takının yalnızca görünümüyle değil, eşlik ettiği anlarla anlam kazandığına inanıyoruz. Bazen bir kutlamanın hatırası, bazen günlük stilin küçük imzası, bazen de sevilen birine söylenen sessiz bir cümle olur.",
                    "Bu nedenle koleksiyonumuzu oluştururken modern çizgiyi, günlük kullanım kolaylığını ve farklı stillerle eşleşebilen zarif detayları bir arada düşünürüz.",
                ],
            },
            {
                "heading": "Seçim yaklaşımımız",
                "paragraphs": [
                    "Her parçayı Hikayem Takı üretmiyor; ürünleri görünüm, kullanım alanı ve koleksiyon bütünlüğü açısından özenle seçiyoruz. Ürün sayfalarında mevcut bilgileri açık ve anlaşılır biçimde sunmaya önem veriyoruz."
                ],
                "bullets": [
                    "Günlük stile kolayca eşlik eden tasarımlar",
                    "Zarif ve modern bir koleksiyon dili",
                    "Özenli paketleme ve ulaşılabilir iletişim",
                ],
            },
            {
                "heading": "Senin takın, senin hikâyen",
                "paragraphs": [
                    "Tarzın kurallardan çok hislerle şekillenir. Hikayem Takı olarak amacımız, kendinizi daha çok siz gibi hissettiren parçaları keşfetmenize eşlik etmektir."
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
