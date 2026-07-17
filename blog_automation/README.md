# Hikayem Takı Blog Otomasyonu

Bu klasör `blog-content` dalında tutulur ve ana Django uygulamasından bağımsızdır.

- `content/articles.json`: Yazılar ve SEO alanları
- `content/images.json`: WebP görsellerin Base64 karşılıkları
- `content/images/*.webp.b64`: Haftalık yeni kapak görselleri; her görsel ayrı Base64 dosyasıdır
- `build_blog.py`: Statik blog üreticisi
- `deploy_blog.sh`: Doğrulama, yedekleme ve geri dönüşlü Veridyen yayını
- `update_and_deploy.sh`: `blog-content` dalını hızlı ileri alıp yayını başlatır
- `dist/`: Yerel üretim çıktısı; Git'e eklenmez

Yerel doğrulama:

```bash
python3 blog_automation/build_blog.py /tmp/hikayem-blog-test
```

Veridyen yayınında `BLOG_PUBLISH_DIR` cPanel'in `blog.hikayemtaki.com` belge köküyle aynı olmalıdır. Betik varsayılan olarak production sanal ortamındaki `/home/hikayemt/virtualenv/hikayemtaki/3.12/bin/python` yorumlayıcısını kullanır; gerekirse `BLOG_PYTHON` ile değiştirilebilir. Betik mevcut yayını önce `previous-*` klasörüne taşır; yeni üretim başarısız olursa önceki yayını geri getirir.
