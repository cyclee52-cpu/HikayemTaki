# Hikayem Takı Blog Otomasyonu

Bu klasör `blog-content` dalında tutulur ve ana Django uygulamasından bağımsızdır.

- `content/articles.json`: Yazılar ve SEO alanları
- `content/images.json`: WebP görsellerin Base64 karşılıkları
- `build_blog.py`: Statik blog üreticisi
- `deploy_blog.sh`: Doğrulama, yedekleme ve geri dönüşlü Veridyen yayını
- `dist/`: Yerel üretim çıktısı; Git'e eklenmez

Yerel doğrulama:

```bash
python3 blog_automation/build_blog.py /tmp/hikayem-blog-test
```

Veridyen yayınında `BLOG_PUBLISH_DIR` cPanel'in `blog.hikayemtaki.com` belge köküyle aynı olmalıdır. Betik mevcut yayını önce `previous-*` klasörüne taşır; yeni üretim başarısız olursa önceki yayını geri getirir.
