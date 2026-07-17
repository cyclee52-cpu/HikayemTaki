(() => {
  const search = document.querySelector("#search");
  const buttons = [...document.querySelectorAll(".category-button")];
  const cards = [...document.querySelectorAll("#article-grid .article-card")];
  const empty = document.querySelector("#empty-state");
  let category = "Tümü";

  const filter = () => {
    const term = (search?.value || "").trim().toLocaleLowerCase("tr-TR");
    let count = 0;
    cards.forEach((card) => {
      const categoryMatch = category === "Tümü" || card.dataset.category === category;
      const searchMatch = !term || card.dataset.search.includes(term);
      card.hidden = !(categoryMatch && searchMatch);
      if (!card.hidden) count += 1;
    });
    if (empty) empty.hidden = count !== 0;
  };

  search?.addEventListener("input", filter);
  buttons.forEach((button) => button.addEventListener("click", () => {
    category = button.dataset.category;
    buttons.forEach((item) => item.classList.toggle("active", item === button));
    filter();
  }));
})();
