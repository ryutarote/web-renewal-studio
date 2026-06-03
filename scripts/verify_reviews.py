#!/usr/bin/env python3
"""
collect_candidates.py が出力した候補CSVに、Google Mapの評価数(google_reviews)を付与する。

評価数は無料の自動取得手段が無いため、本スクリプトは2モードを用意する:

  1. manual (既定):
     候補CSVを開いて google_reviews 列を手で埋める前提のテンプレを整える。
     評価数が空のままの行に "TODO" を入れ、Google Map確認用URLを補助列で出力する。

  2. places-api (任意 / 有料):
     環境変数 GOOGLE_MAPS_API_KEY がある場合のみ、Google Places APIで
     user_ratings_total を取得する。APIキーが無ければ何もしない。
     ※「無料手段だけで」という方針では使わない。必要になった時のための拡張口。

使い方:
  python3 verify_reviews.py data/candidates_pre2015_XXXX.csv
  python3 verify_reviews.py data/candidates_pre2015_XXXX.csv --mode places-api --min-reviews 50
"""

import argparse
import csv
import os
import sys
import urllib.parse

import requests

PLACES_FINDPLACE = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"


def gmaps_search_url(name, address):
    q = urllib.parse.quote_plus(f"{name} {address}")
    return f"https://www.google.com/maps/search/?api=1&query={q}"


def enrich_manual(rows):
    for r in rows:
        if not r.get("google_reviews"):
            r["google_reviews"] = "TODO"
        r["gmap_check_url"] = gmaps_search_url(r.get("name", ""), r.get("address", ""))
    return rows, ["gmap_check_url"]


def fetch_review_count(name, address, api_key):
    params = {
        "input": f"{name} {address}",
        "inputtype": "textquery",
        "fields": "user_ratings_total,name,place_id",
        "language": "ja",
        "key": api_key,
    }
    try:
        resp = requests.get(PLACES_FINDPLACE, params=params, timeout=20)
        data = resp.json()
        cands = data.get("candidates", [])
        if cands:
            return cands[0].get("user_ratings_total", "")
    except (requests.RequestException, ValueError):
        pass
    return ""


def enrich_places_api(rows, min_reviews):
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    if not api_key:
        print("GOOGLE_MAPS_API_KEY が未設定のため places-api モードは実行できません。", file=sys.stderr)
        print("無料方針なら --mode manual を使ってください。", file=sys.stderr)
        sys.exit(1)
    for r in rows:
        count = fetch_review_count(r.get("name", ""), r.get("address", ""), api_key)
        r["google_reviews"] = count
        r["meets_min_reviews"] = "yes" if (str(count).isdigit() and int(count) >= min_reviews) else "no"
    return rows, ["meets_min_reviews"]


def main():
    ap = argparse.ArgumentParser(description="候補CSVに評価数を付与")
    ap.add_argument("csv_path")
    ap.add_argument("--mode", choices=["manual", "places-api"], default="manual")
    ap.add_argument("--min-reviews", type=int, default=50)
    args = ap.parse_args()

    with open(args.csv_path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    if args.mode == "manual":
        rows, extra = enrich_manual(rows)
    else:
        rows, extra = enrich_places_api(rows, args.min_reviews)

    for col in extra:
        if col not in fieldnames:
            fieldnames.append(col)

    base, ext = os.path.splitext(args.csv_path)
    out_path = f"{base}_reviews{ext}"
    with open(out_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print(f"出力: {out_path} ({len(rows)} 件)", file=sys.stderr)
    if args.mode == "manual":
        print("各行の gmap_check_url を開き、google_reviews 列(TODO)を実際の評価数で置き換えてください。", file=sys.stderr)


if __name__ == "__main__":
    main()
