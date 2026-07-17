#!/usr/bin/env python3
"""Hikayem Takı blog içeriklerinden bağımsız statik site üretir."""

from __future__ import annotations

import base64
import html
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
ASSETS = ROOT / "assets"
SITE_URL = "https://blog.hikayemtaki.com"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def header(compact: bool = False) -> str:
    cls = " site-header--compact" if compact else ""
    return f"""
    <header class="site-header{cls}">
      <div class="header-inner">
        <a class="brand" href="/" aria-label="Hikayem Takı Blog ana sayfa">
          <span class="brand-mark">H</span>
          <span class="brand-copy"><strong>HİKAYEM TAKI</strong><small>HER TAKININ BİR HİKÂYESİ VAR</small></span>
        </a>
        <nav class="desktop-nav" aria-label="Ana menü">
          <a href="/#yazilar">Yazılar</a><a href="https://hikayemtaki.com">Mağaza</a>
          <a href="https://www.instagram.com/hikayemtaki">Instagram</a>
        </nav>
      </div>
    </header>"""


def footer() -> str:
    return """
    <footer class="site-footer">
      <div class="footer-brand"><span class="brand-mark">H</span><div><strong>HİKAYEM TAKI</strong><small>Her takının bir hikâyesi var.</small></div></div>
      <div class="footer-links"><a href="/">Blog</a><a href="https://hikayemtaki.com">Mağaza</a><a href="https://www.instagram.com/hikayemtaki">Instagram</a></div>
      <p>© 2026 Hikayem Takı. Tüm hakları saklıdır.</p>
    </footer>"""


def page_shell(title: str, description: str, canonical: str, body: str, image: str | None = None, article: bool = False) -> str:
    image_url = f"{SITE_URL}/images/{image}" if image else f"{SITE_URL}/images/editorial-hero.webp"
    article_meta = '<meta property="og:type" content="article">' if article else '<meta property="og:type" content="website">'
    return f"""<!doctype html>
<html lang="tr"><head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{esc(title)}</title><meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{esc(canonical)}"><link rel="stylesheet" href="/assets/style.css">
  {article_meta}<meta property="og:site_name" content="Hikayem Takı Blog">
  <meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{esc(canonical)}"><meta property="og:image" content="{esc(image_url)}">
  <meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(description)}"><meta name="twitter:image" content="{esc(image_url)}">
</head><body><a class="skip-link" href="#icerik">İçeriğe geç</a>{body}</body></html>"""


def card(article: dict, index: int) -> str:
    return f"""
    <article class="article-card" data-category="{esc(article['category'])}" data-search="{esc((article['title'] + ' ' + article['excerpt']).lower())}">
      <a class="card-image" href="/yazi/{esc(article['slug'])}/"><img src="/images/{esc(article['image'])}" alt="{esc(article['imageAlt'])}" loading="lazy"><span>{index:02}</span></a>
      <div class="card-content"><div class="article-meta"><span>{esc(article['category'])}</span><span>{esc(article['readTime'])}</span></div>
      <h3><a href="/yazi/{esc(article['slug'])}/">{esc(article['title'])}</a></h3><p>{esc(article['excerpt'])}</p>
      <a class="text-link" href="/yazi/{esc(article['slug'])}/">Yazıyı oku →</a></div>
    </article>"""


def build_home(articles: list[dict]) -> str:
    featured = [item for item in articles if item.get("featured")][:3]
    featured_html = "".join(card(item, i + 1) for i, item in enumerate(featured))
    cards = "".join(card(item, i + 1) for i, item in enumerate(articles))
    categories = ["Tümü"] + list(dict.fromkeys(item["category"] for item in articles))
    buttons = "".join(f'<button class="category-button{" active" if i == 0 else ""}" data-category="{esc(cat)}">{esc(cat)}</button>' for i, cat in enumerate(categories))
    body = f"""{header()}
    <main id="icerik">
      <section class="hero"><div class="hero-image-wrap"><img class="hero-image" src="/images/editorial-hero.webp" alt="İpek üzerinde zarif takılar"></div>
        <div class="hero-panel"><p class="hero-overline">Hikâyeni taşı</p><h1>Takıların ardındaki <em>hikâyeler</em></h1>
        <p class="hero-lead">Bakım, stil ve anlamlı hediye seçimleri için sakin, güvenilir ve ilham veren notlar.</p><a class="primary-link" href="#yazilar">Yazıları keşfet →</a></div></section>
      <section class="manifesto"><span class="section-kicker">Hikayem Takı Blog</span><p>Her parça bir ana eşlik eder; her an zamanla <em>bir hikâyeye</em> dönüşür.</p></section>
      <section class="featured-grid"><div class="section-heading"><div><span class="section-kicker">Editörün seçimi</span><h2>Öne çıkanlar</h2></div><p>Günlük takı ritüellerinizi daha bilinçli ve kişisel kılan rehberler.</p></div><div class="article-grid">{featured_html}</div></section>
      <section class="journal" id="yazilar"><div class="journal-top"><div><span class="section-kicker">Günlük notlar</span><h2>Tüm yazılar</h2></div>
        <label class="search-box"><span>⌕</span><span class="sr-only">Yazılarda ara</span><input id="search" type="search" placeholder="Bir konu ara…"></label></div>
        <div class="category-tabs">{buttons}</div><div class="article-grid" id="article-grid">{cards}</div><p class="empty-state" id="empty-state" hidden>Aramanızla eşleşen yazı bulunamadı.</p></section>
      <section class="newsletter"><div><span class="section-kicker section-kicker--light">Hikâyeye katılın</span><h2>Yeni notları kaçırmayın.</h2></div><div><p>Yeni yazılar, stil fikirleri ve koleksiyon haberleri için Instagram’da bize katılın.</p><a class="newsletter-instagram" href="https://www.instagram.com/hikayemtaki">@hikayemtaki →</a></div></section>
    </main>{footer()}<script src="/assets/app.js" defer></script>"""
    return page_shell("Hikayem Takı Blog | Takı Bakımı, Stil ve Hediye Rehberi", "Takı bakımı, stil, kombin ve anlamlı hediye seçimleri için Hikayem Takı'nın editoryal rehberleri.", f"{SITE_URL}/", body)


def build_article(article: dict, all_articles: list[dict]) -> str:
    sections = []
    for index, section in enumerate(article["sections"], 1):
        paragraphs = "".join(f"<p>{esc(p)}</p>" for p in section.get("paragraphs", []))
        callout = f"<blockquote>{esc(section['callout'])}</blockquote>" if section.get("callout") else ""
        sections.append(f'<section><span class="section-index">{index:02}</span><h2>{esc(section["heading"])}</h2>{paragraphs}{callout}</section>')
    related = [item for item in all_articles if item["slug"] != article["slug"] and item["category"] == article["category"]][:2]
    if len(related) < 2:
        related += [item for item in all_articles if item["slug"] != article["slug"] and item not in related][:2-len(related)]
    related_html = "".join(card(item, i + 1) for i, item in enumerate(related))
    canonical = f"{SITE_URL}/yazi/{article['slug']}/"
    schema = json.dumps({"@context": "https://schema.org", "@type": "BlogPosting", "headline": article["title"], "description": article["excerpt"], "datePublished": article["date_iso"], "dateModified": article["date_iso"], "inLanguage": "tr-TR", "image": f"{SITE_URL}/images/{article['image']}", "mainEntityOfPage": canonical, "publisher": {"@type": "Organization", "name": "Hikayem Takı"}}, ensure_ascii=False).replace("</", "<\\/")
    share = quote(article["title"] + " " + canonical)
    body = f"""{header(True)}<main id="icerik" class="article-page">
      <section class="article-hero"><div class="article-hero-copy"><a class="back-link" href="/">← Tüm yazılar</a><div class="article-meta article-meta--large"><span>{esc(article['category'])}</span><span>{esc(article['readTime'])}</span></div>
      <h1>{esc(article['title'])}</h1><p>{esc(article['excerpt'])}</p><time class="article-date" datetime="{esc(article['date_iso'])}">{esc(article['date'])}</time></div>
      <div class="article-hero-image"><img src="/images/{esc(article['image'])}" alt="{esc(article['imageAlt'])}"></div></section>
      <div class="article-layout"><aside class="article-aside"><span>Paylaş</span><a href="https://wa.me/?text={share}" aria-label="WhatsApp'ta paylaş">WA</a><a href="mailto:?subject={quote(article['title'])}&body={share}" aria-label="E-posta ile paylaş">@</a></aside>
      <article class="article-body"><p class="article-intro">{esc(article['intro'])}</p>{''.join(sections)}<div class="article-end"><span>✦</span><p>Her takının bir hikâyesi var.</p><a class="primary-link" href="https://hikayemtaki.com">Koleksiyonu keşfet →</a></div></article></div>
      <section class="related"><span class="section-kicker">Okumaya devam edin</span><h2>Benzer yazılar</h2><div class="article-grid">{related_html}</div></section>
    </main>{footer()}<script type="application/ld+json">{schema}</script>"""
    return page_shell(f"{article['title']} | Hikayem Takı", article["excerpt"], canonical, body, article["image"], True)


def build(output: Path) -> None:
    articles = json.loads((CONTENT / "articles.json").read_text(encoding="utf-8"))
    images = json.loads((CONTENT / "images.json").read_text(encoding="utf-8"))
    if output.exists():
        shutil.rmtree(output)
    (output / "assets").mkdir(parents=True)
    (output / "images").mkdir(parents=True)
    shutil.copy2(ASSETS / "style.css", output / "assets" / "style.css")
    shutil.copy2(ASSETS / "app.js", output / "assets" / "app.js")
    for name, payload in images.items():
        (output / "images" / name).write_bytes(base64.b64decode(payload))
    (output / "index.html").write_text(build_home(articles), encoding="utf-8")
    for article in articles:
        article_dir = output / "yazi" / article["slug"]
        article_dir.mkdir(parents=True)
        (article_dir / "index.html").write_text(build_article(article, articles), encoding="utf-8")
    urls = [f"{SITE_URL}/"] + [f"{SITE_URL}/yazi/{item['slug']}/" for item in articles]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(f"  <url><loc>{esc(url)}</loc></url>" for url in urls) + "\n</urlset>\n"
    (output / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (output / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")
    (output / ".htaccess").write_text("Options -Indexes\nDirectoryIndex index.html\nRewriteEngine On\nRewriteCond %{REQUEST_FILENAME} !-f\nRewriteCond %{REQUEST_FILENAME} !-d\nRewriteCond %{REQUEST_FILENAME}/index.html -f\nRewriteRule ^(.+?)/?$ $1/ [R=301,L]\n", encoding="utf-8")
    stamp = datetime.now(timezone.utc).isoformat()
    (output / "build-info.json").write_text(json.dumps({"generated_at": stamp, "article_count": len(articles)}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    target = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT / "dist"
    build(target)
    print(target)
