#!/usr/bin/env bash
set -euo pipefail

ROOT="${BLOG_REPOSITORY_DIR:-/home/hikayemt/blog-content}"
cd "$ROOT"

git fetch origin blog-content
git merge --ff-only origin/blog-content

bash "$ROOT/blog_automation/deploy_blog.sh"
