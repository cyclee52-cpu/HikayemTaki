document.addEventListener("DOMContentLoaded", function () {
    const detailSection = document.querySelector(".product-detail-section");
    const galleryMain = document.getElementById("productGalleryMain");
    const mainImage = document.getElementById("mainProductImage");
    const thumbs = Array.from(document.querySelectorAll(".product-gallery-thumb"));

    let activeIndex = Math.max(0, thumbs.findIndex(function (thumb) {
        return thumb.classList.contains("active");
    }));
    let touchStartX = 0;

    function setImageLoadedState() {
        if (!galleryMain || !mainImage) {
            return;
        }

        galleryMain.classList.add("is-loading");

        if (mainImage.complete) {
            galleryMain.classList.remove("is-loading");
        }

        mainImage.addEventListener("load", function () {
            galleryMain.classList.remove("is-loading");
        });
    }

    function changeImage(index) {
        const thumb = thumbs[index];

        if (!mainImage || !thumb) {
            return;
        }

        const imageUrl = thumb.dataset.image;
        const imageAlt = thumb.dataset.alt || "";

        if (!imageUrl || mainImage.src.includes(imageUrl)) {
            return;
        }

        activeIndex = index;
        mainImage.classList.add("is-changing");
        galleryMain.classList.add("is-loading");

        window.setTimeout(function () {
            mainImage.src = imageUrl;
            mainImage.alt = imageAlt;
            mainImage.classList.remove("is-changing");
        }, 140);

        thumbs.forEach(function (item) {
            item.classList.remove("active");
        });

        thumb.classList.add("active");
    }

    thumbs.forEach(function (thumb, index) {
        thumb.addEventListener("mouseenter", function () {
            changeImage(index);
        });

        thumb.addEventListener("focus", function () {
            changeImage(index);
        });

        thumb.addEventListener("click", function () {
            changeImage(index);
        });
    });

    if (galleryMain && mainImage) {
        setImageLoadedState();

        galleryMain.addEventListener("mousemove", function (event) {
            const rect = galleryMain.getBoundingClientRect();
            const x = ((event.clientX - rect.left) / rect.width) * 100;
            const y = ((event.clientY - rect.top) / rect.height) * 100;

            mainImage.style.transformOrigin = x + "% " + y + "%";
        });

        galleryMain.addEventListener("mouseleave", function () {
            mainImage.style.transformOrigin = "center center";
        });

        galleryMain.addEventListener("touchstart", function (event) {
            touchStartX = event.changedTouches[0].screenX;
        }, { passive: true });

        galleryMain.addEventListener("touchend", function (event) {
            const touchEndX = event.changedTouches[0].screenX;
            const diff = touchStartX - touchEndX;

            if (Math.abs(diff) < 45 || thumbs.length < 2) {
                return;
            }

            if (diff > 0) {
                changeImage((activeIndex + 1) % thumbs.length);
            } else {
                changeImage((activeIndex - 1 + thumbs.length) % thumbs.length);
            }
        }, { passive: true });
    }

    document.addEventListener("keydown", function (event) {
        if (thumbs.length < 2) {
            return;
        }

        if (event.key === "ArrowRight") {
            changeImage((activeIndex + 1) % thumbs.length);
        }

        if (event.key === "ArrowLeft") {
            changeImage((activeIndex - 1 + thumbs.length) % thumbs.length);
        }
    });

    const storageKey = "hikayemRecentlyViewed";
    const recentSection = document.getElementById("recentlyViewedSection");
    const recentGrid = document.getElementById("recentlyViewedGrid");

    function getRecentProducts() {
        try {
            return JSON.parse(localStorage.getItem(storageKey)) || [];
        } catch (error) {
            return [];
        }
    }

    function saveCurrentProduct() {
        if (!detailSection) {
            return;
        }

        const product = {
            slug: detailSection.dataset.productSlug,
            name: detailSection.dataset.productName,
            price: detailSection.dataset.productPrice,
            url: detailSection.dataset.productUrl,
            image: detailSection.dataset.productImage || ""
        };

        if (!product.slug || !product.name) {
            return;
        }

        const filteredProducts = getRecentProducts().filter(function (item) {
            return item.slug !== product.slug;
        });

        const updatedProducts = [product, ...filteredProducts].slice(0, 6);
        localStorage.setItem(storageKey, JSON.stringify(updatedProducts));
    }

    function escapeHtml(value) {
        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function renderRecentProducts() {
        if (!recentSection || !recentGrid || !detailSection) {
            return;
        }

        const currentSlug = detailSection.dataset.productSlug;
        const products = getRecentProducts()
            .filter(function (item) {
                return item.slug !== currentSlug;
            })
            .slice(0, 4);

        if (!products.length) {
            return;
        }

        recentGrid.innerHTML = products.map(function (item) {
            const safeName = escapeHtml(item.name);
            const safePrice = escapeHtml(item.price);
            const safeUrl = escapeHtml(item.url);
            const safeImage = escapeHtml(item.image || "");
            const imageHtml = safeImage
                ? `<img src="${safeImage}" alt="${safeName}">`
                : `<div class="product-image-placeholder"><span>Hikayem Takı</span><small>Görsel yakında</small></div>`;

            return `
                <article class="home-product-card">
                    <div class="home-product-image">
                        <span class="product-badge">Son Bakılan</span>
                        ${imageHtml}
                    </div>

                    <div class="home-product-info">
                        <span class="product-category">Hikayem Takı</span>
                        <h3>${safeName}</h3>

                        <div class="product-card-footer">
                            <p>${safePrice}</p>
                            <a href="${safeUrl}" class="product-detail-link">İncele</a>
                        </div>
                    </div>
                </article>
            `;
        }).join("");

        recentSection.hidden = false;
    }

    renderRecentProducts();
    saveCurrentProduct();
});