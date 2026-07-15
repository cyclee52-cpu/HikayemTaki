document.addEventListener("DOMContentLoaded", function () {
    const detailSection = document.querySelector(".product-detail-section");

    if (!detailSection) {
        return;
    }

    function parsePrice(value) {
        if (!value) {
            return 0;
        }

        const normalizedValue = String(value)
            .trim()
            .replace(/\s/g, "")
            .replace("₺", "")
            .replace(",", ".");

        const parsedValue = Number.parseFloat(normalizedValue);

        return Number.isFinite(parsedValue) ? parsedValue : 0;
    }

    function getProductData() {
        const price = parsePrice(detailSection.dataset.productPrice);

        return {
            currency: "TRY",
            value: price,
            items: [
                {
                    item_id: detailSection.dataset.productSlug || "",
                    item_name: detailSection.dataset.productName || "",
                    item_category: detailSection.dataset.productCategory || "",
                    price: price,
                    quantity: 1
                }
            ]
        };
    }

    function sendGa4Event(eventName, parameters) {
        if (typeof window.gtag !== "function") {
            return;
        }

        window.gtag("event", eventName, parameters);
    }

    const shopierButtons = document.querySelectorAll(".product-shopier-btn");

    shopierButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            const productData = getProductData();

            sendGa4Event("begin_checkout", {
                currency: productData.currency,
                value: productData.value,
                items: productData.items,
                checkout_option: "Shopier",
                outbound_url: button.href
            });
        });
    });
});