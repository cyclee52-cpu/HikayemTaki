document.addEventListener("DOMContentLoaded", function () {
    const detailSection = document.querySelector(".product-detail-section");
    const favoriteButton = document.getElementById("favoriteProductButton");
    const shareButton = document.getElementById("shareProductButton");
    const favoriteStorageKey = "hikayemFavoriteProducts";

    if (!detailSection) {
        return;
    }

    function getCurrentProduct() {
        return {
            slug: detailSection.dataset.productSlug,
            name: detailSection.dataset.productName,
            price: detailSection.dataset.productPrice,
            url: detailSection.dataset.productUrl,
            image: detailSection.dataset.productImage || ""
        };
    }

    function showToast(message) {
        if (window.HikayemToast && typeof window.HikayemToast.show === "function") {
            window.HikayemToast.show(message);
        }
    }

    function getFavorites() {
        try {
            return JSON.parse(localStorage.getItem(favoriteStorageKey)) || [];
        } catch (error) {
            return [];
        }
    }

    function saveFavorites(favorites) {
        localStorage.setItem(favoriteStorageKey, JSON.stringify(favorites));
    }

    function isFavorite(slug) {
        return getFavorites().some(function (item) {
            return item.slug === slug;
        });
    }

    function updateFavoriteButton() {
        if (!favoriteButton) {
            return;
        }

        const product = getCurrentProduct();
        const active = isFavorite(product.slug);
        const icon = favoriteButton.querySelector(".utility-icon");
        const text = favoriteButton.querySelector(".utility-text");

        favoriteButton.classList.toggle("is-active", active);
        favoriteButton.setAttribute("aria-pressed", active ? "true" : "false");
        favoriteButton.setAttribute("title", active ? "Favorilerden çıkar" : "Favorilere ekle");

        if (icon) {
            icon.textContent = active ? "♥" : "♡";
        }

        if (text) {
            text.textContent = active ? "Favorilerde" : "Favorilere Ekle";
        }
    }

    function pulseButton(button) {
        if (!button) {
            return;
        }

        button.classList.remove("is-pulsing");
        window.requestAnimationFrame(function () {
            button.classList.add("is-pulsing");
        });

        window.setTimeout(function () {
            button.classList.remove("is-pulsing");
        }, 450);
    }

    function toggleFavorite() {
        const product = getCurrentProduct();

        if (!product.slug || !product.name) {
            return;
        }

        const favorites = getFavorites();
        const exists = favorites.some(function (item) {
            return item.slug === product.slug;
        });

        if (exists) {
            saveFavorites(favorites.filter(function (item) {
                return item.slug !== product.slug;
            }));
            showToast("Favorilerden çıkarıldı");
        } else {
            saveFavorites([product, ...favorites].slice(0, 48));
            showToast("Favorilere eklendi");
        }

        pulseButton(favoriteButton);
        updateFavoriteButton();
    }

    function getShareUrl() {
        return new URL(detailSection.dataset.productUrl, window.location.origin).href;
    }

    function copyToClipboard(text) {
        if (navigator.clipboard && window.isSecureContext) {
            return navigator.clipboard.writeText(text);
        }

        const textarea = document.createElement("textarea");
        textarea.value = text;
        textarea.setAttribute("readonly", "");
        textarea.style.position = "fixed";
        textarea.style.opacity = "0";
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand("copy");
        document.body.removeChild(textarea);
        return Promise.resolve();
    }

    function shareProduct() {
        const product = getCurrentProduct();
        const shareUrl = getShareUrl();
        const shareData = {
            title: product.name + " | Hikayem Takı",
            text: product.name + " ürününü Hikayem Takı'da incele.",
            url: shareUrl
        };

        pulseButton(shareButton);

        if (navigator.share) {
            navigator.share(shareData)
                .then(function () {
                    showToast("Paylaşım hazırlandı");
                })
                .catch(function () {});
            return;
        }

        copyToClipboard(shareUrl).then(function () {
            showToast("Ürün linki kopyalandı");
        });
    }

    if (favoriteButton) {
        favoriteButton.addEventListener("click", toggleFavorite);
        updateFavoriteButton();
    }

    if (shareButton) {
        shareButton.addEventListener("click", shareProduct);
    }
});