window.HikayemToast = (function () {
    let toastElement;
    let toastTimer;

    function createToast() {
        toastElement = document.createElement("div");
        toastElement.className = "hikayem-toast";
        toastElement.setAttribute("role", "status");
        toastElement.setAttribute("aria-live", "polite");
        document.body.appendChild(toastElement);
    }

    function show(message) {
        if (!toastElement) {
            createToast();
        }

        window.clearTimeout(toastTimer);
        toastElement.textContent = message;
        toastElement.classList.remove("show");

        window.requestAnimationFrame(function () {
            toastElement.classList.add("show");
        });

        toastTimer = window.setTimeout(function () {
            toastElement.classList.remove("show");
        }, 2400);
    }

    return {
        show: show
    };
})();