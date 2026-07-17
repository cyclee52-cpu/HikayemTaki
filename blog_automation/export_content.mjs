import { mkdir, readFile, writeFile } from "node:fs/promises";
import { basename, join } from "node:path";
import { articles } from "../lib/articles.js";

const root = new URL(".", import.meta.url).pathname;
const contentDir = join(root, "content");
await mkdir(contentDir, { recursive: true });

const dates = [
  "2026-07-17", "2026-07-15", "2026-07-12", "2026-07-09",
  "2026-07-06", "2026-07-02", "2026-06-28", "2026-06-24",
];

const normalized = articles.map((article, index) => ({
  ...article,
  image: basename(article.image),
  date_iso: dates[index],
}));

const imageNames = [...new Set(normalized.map((article) => article.image))];
const images = {};
for (const imageName of imageNames) {
  const bytes = await readFile(join(root, "..", "public", "images", imageName));
  images[imageName] = bytes.toString("base64");
}

await writeFile(join(contentDir, "articles.json"), JSON.stringify(normalized, null, 2) + "\n");
await writeFile(join(contentDir, "images.json"), JSON.stringify(images) + "\n");
