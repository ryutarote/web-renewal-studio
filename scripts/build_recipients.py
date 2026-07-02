#!/usr/bin/env python3
"""
sites/index.html をパースして営業宛先CSV (data/recipients.csv) を生成する。

- 全サイトの slug / 店名 / エリア・ジャンル / 公開デモURL を埋める。
- email / official_url / contact_name は「手動で埋める」列として空で出力。
- 既に data/recipients.csv があれば、その email / official_url / contact_name /
  status / notes を slug をキーに引き継ぐ（再生成でも手入力を失わない）。

宛先CSVは data/.gitignore で除外されており、公開リポジトリには含めない方針。
"""
import csv
import html
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "sites", "index.html")
OUT = os.path.join(ROOT, "data", "recipients.csv")

# 公開ベースURL（GitHub Pages）。末尾スラッシュ必須。
BASE_URL = "https://ryutarote.github.io/web-renewal-studio/"

# 引き継ぐ列（手入力を保持する）
CARRY = ["email", "official_url", "contact_name", "status", "notes"]

FIELDS = ["slug", "shop_name", "area_genre", "demo_url"] + CARRY

# <a ... href="slug/"> ... <span class="emoji" ...>絵文字</span>店名<span class="sub">エリア・ジャンル</span></a>
CARD_RE = re.compile(
    r'<a\s+class="card[^"]*"[^>]*href="([a-z0-9-]+)/"[^>]*>'
    r'\s*<span class="emoji"[^>]*>.*?</span>'
    r'(.*?)'
    r'<span class="sub">(.*?)</span>\s*</a>',
    re.DOTALL,
)


def load_existing():
    existing = {}
    if os.path.exists(OUT):
        with open(OUT, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                existing[row.get("slug", "")] = row
    return existing


def main():
    with open(INDEX, encoding="utf-8") as f:
        doc = f.read()

    existing = load_existing()
    rows = []
    for slug, name, sub in CARD_RE.findall(doc):
        shop = html.unescape(re.sub(r"<[^>]+>", "", name)).strip()
        area_genre = html.unescape(sub).strip()
        prev = existing.get(slug, {})
        row = {
            "slug": slug,
            "shop_name": shop,
            "area_genre": area_genre,
            "demo_url": f"{BASE_URL}{slug}/",
        }
        for col in CARRY:
            row[col] = prev.get(col, "")
        rows.append(row)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

    filled = sum(1 for r in rows if r["email"].strip())
    print(f"wrote {len(rows)} rows -> {OUT}")
    print(f"  email filled: {filled} / {len(rows)}")
    print(f"  email empty : {len(rows) - filled} (要・宛先メール入力)")


if __name__ == "__main__":
    main()
