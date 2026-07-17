#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${BLOG_PUBLISH_DIR:-/home/hikayemt/public_html/blog}"
RELEASES="${BLOG_RELEASE_DIR:-/home/hikayemt/blog-releases}"
PYTHON="${BLOG_PYTHON:-/home/hikayemt/virtualenv/hikayemtaki/3.12/bin/python}"
STAMP="$(date +%Y%m%d-%H%M%S)"
NEW_RELEASE="$RELEASES/$STAMP"
BACKUP="$RELEASES/previous-$STAMP"

mkdir -p "$RELEASES"
test -x "$PYTHON"
"$PYTHON" "$ROOT/build_blog.py" "$NEW_RELEASE"

test -f "$NEW_RELEASE/index.html"
test -f "$NEW_RELEASE/sitemap.xml"
test "$(find "$NEW_RELEASE/yazi" -mindepth 2 -maxdepth 2 -name index.html | wc -l)" -ge 8

if [ -d "$TARGET" ]; then
  mv "$TARGET" "$BACKUP"
fi

if ! mv "$NEW_RELEASE" "$TARGET"; then
  if [ -d "$BACKUP" ]; then mv "$BACKUP" "$TARGET"; fi
  exit 1
fi

find "$RELEASES" -maxdepth 1 -type d -name 'previous-*' -mtime +28 -exec rm -rf -- {} +
printf 'Blog yayını tamamlandı: %s\n' "$TARGET"
