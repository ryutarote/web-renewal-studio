#!/usr/bin/env python3
"""
古いWebサイト(2015年以前作成)を使っている全国の中小・個人店を収集する。

無料データソースのみ:
  1. OpenStreetMap (Overpass API) ... 全国の店舗 + Webサイトを取得
  2. Wayback Machine (CDX API)    ... サイトの最古スナップショット年を取得し「サイトの古さ」を判定

注意:
  Google Mapの「評価50件以上」は無料の自動取得手段が無いため、ここでは収集しない。
  本スクリプトは候補リスト(店名/住所/サイトURL/推定作成年)を出力する。
  評価数は verify_reviews.py または手動で後から埋める想定。

使い方:
  python3 collect_candidates.py                       # 全国
  python3 collect_candidates.py --prefectures 東京都 京都府
  python3 collect_candidates.py --limit-per-pref 200  # 各県の調査件数を制限(動作確認用)
  python3 collect_candidates.py --no-wayback          # サイト年代判定をスキップ(収集だけ)
"""

import argparse
import csv
import json
import os
import sys
import time
import urllib.parse
from datetime import datetime, timezone

import requests

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(REPO_DIR, "data")

OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]
WAYBACK_CDX = "http://web.archive.org/cdx/search/cdx"

USER_AGENT = "moneytize-leadfinder/1.0 (OSM+Wayback; contact: set-your-email)"


def load_config(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_overpass_query(prefecture, osm_filters, timeout=180):
    """都道府県(admin_level=4)エリア内の対象店舗を取得するOverpass QLを組み立てる。"""
    filters = "\n  ".join(osm_filters)
    return f"""
[out:json][timeout:{timeout}];
area["name"="{prefecture}"]["admin_level"="4"]->.a;
(
  {filters}
);
out center tags;
""".strip()


def run_overpass(query, retries=3):
    """Overpassへクエリ。エンドポイント/リトライを切り替えてレート制限に対応。"""
    last_err = None
    for attempt in range(retries):
        endpoint = OVERPASS_ENDPOINTS[attempt % len(OVERPASS_ENDPOINTS)]
        try:
            resp = requests.post(
                endpoint,
                data={"data": query},
                headers={"User-Agent": USER_AGENT},
                timeout=300,
            )
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code in (429, 504):
                wait = 2 ** (attempt + 2)
                print(f"    Overpass {resp.status_code}, {wait}s 待機して再試行...", file=sys.stderr)
                time.sleep(wait)
                continue
            resp.raise_for_status()
        except requests.RequestException as e:
            last_err = e
            wait = 2 ** (attempt + 2)
            print(f"    Overpass エラー: {e} ({wait}s 待機)", file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError(f"Overpass取得失敗: {last_err}")


def normalize_website(tags):
    return tags.get("website") or tags.get("contact:website") or ""


def is_chain(name, blacklist):
    if not name:
        return False
    return any(token in name for token in blacklist)


def domain_of(url):
    try:
        netloc = urllib.parse.urlparse(url if "://" in url else "http://" + url).netloc
        return netloc.split(":")[0].lstrip("www.")
    except Exception:
        return ""


def oldest_snapshot_year(url, retries=2):
    """Wayback CDXで最古スナップショットの年を返す。無ければNone。"""
    domain = domain_of(url)
    if not domain:
        return None
    params = {
        "url": domain + "/*",
        "output": "json",
        "fl": "timestamp",
        "collapse": "timestamp:4",
        "limit": "1",
        "sort": "ascending",
    }
    for attempt in range(retries + 1):
        try:
            resp = requests.get(
                WAYBACK_CDX, params=params,
                headers={"User-Agent": USER_AGENT}, timeout=30,
            )
            if resp.status_code == 200:
                rows = resp.json()
                # rows[0] はヘッダ ["timestamp"]、rows[1] が最古データ
                if len(rows) >= 2 and rows[1] and rows[1][0]:
                    return int(rows[1][0][:4])
                return None
            time.sleep(1.5 * (attempt + 1))
        except (requests.RequestException, ValueError):
            time.sleep(1.5 * (attempt + 1))
    return None


def collect(config, prefectures, limit_per_pref, use_wayback):
    cutoff = config["site_age_cutoff_year"]
    blacklist = config["chain_blacklist"]
    osm_filters = config["osm_filters"]

    seen_domains = set()
    candidates = []

    for pref in prefectures:
        print(f"[{pref}] Overpass取得中...", file=sys.stderr)
        query = build_overpass_query(pref, osm_filters)
        try:
            data = run_overpass(query)
        except RuntimeError as e:
            print(f"  スキップ: {e}", file=sys.stderr)
            continue

        elements = data.get("elements", [])
        print(f"  Webサイト付き店舗: {len(elements)} 件", file=sys.stderr)

        checked = 0
        for el in elements:
            if limit_per_pref and checked >= limit_per_pref:
                break
            tags = el.get("tags", {})
            name = tags.get("name") or tags.get("name:ja") or ""
            website = normalize_website(tags)
            if not website:
                continue
            if is_chain(name, blacklist):
                continue

            domain = domain_of(website)
            if domain and domain in seen_domains:
                continue  # 同一サイト(=同一事業者)の重複を除去
            if domain:
                seen_domains.add(domain)

            lat = el.get("lat") or (el.get("center") or {}).get("lat")
            lon = el.get("lon") or (el.get("center") or {}).get("lon")
            addr = " ".join(filter(None, [
                tags.get("addr:province", ""), tags.get("addr:city", ""),
                tags.get("addr:suburb", ""), tags.get("addr:block_number", ""),
                tags.get("addr:housenumber", ""),
            ])) or pref

            row = {
                "prefecture": pref,
                "name": name,
                "category": tags.get("shop") or tags.get("amenity")
                or tags.get("craft") or tags.get("office")
                or tags.get("tourism") or tags.get("leisure") or "",
                "website": website,
                "domain": domain,
                "address": addr,
                "lat": lat,
                "lon": lon,
                "phone": tags.get("phone") or tags.get("contact:phone") or "",
                "site_oldest_year": "",
                "site_pre_cutoff": "",
                "google_reviews": "",  # 後段で埋める(無料自動取得不可)
            }

            if use_wayback and website:
                year = oldest_snapshot_year(website)
                time.sleep(0.4)  # Wayback への礼儀
                if year:
                    row["site_oldest_year"] = year
                    row["site_pre_cutoff"] = "yes" if year <= cutoff else "no"
                else:
                    row["site_pre_cutoff"] = "unknown"

            checked += 1
            candidates.append(row)

        print(f"  候補(チェーン除外後): 累計 {len(candidates)} 件", file=sys.stderr)

    return candidates


def write_outputs(candidates, cutoff):
    os.makedirs(DATA_DIR, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    all_path = os.path.join(DATA_DIR, f"candidates_all_{stamp}.csv")
    target_path = os.path.join(DATA_DIR, f"candidates_pre{cutoff}_{stamp}.csv")

    fieldnames = [
        "prefecture", "name", "category", "website", "domain", "address",
        "lat", "lon", "phone", "site_oldest_year", "site_pre_cutoff",
        "google_reviews",
    ]

    def dump(path, rows):
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(rows)

    dump(all_path, candidates)
    targets = [r for r in candidates if r["site_pre_cutoff"] == "yes"]
    dump(target_path, targets)

    return all_path, target_path, len(targets)


def main():
    ap = argparse.ArgumentParser(description="古いサイトを使う中小・個人店の候補を無料データで収集")
    ap.add_argument("--config", default=os.path.join(SCRIPT_DIR, "config.json"))
    ap.add_argument("--prefectures", nargs="*", help="対象都道府県(省略時は全国)")
    ap.add_argument("--limit-per-pref", type=int, default=0, help="各県の調査上限(0=無制限)")
    ap.add_argument("--no-wayback", action="store_true", help="サイト年代判定をスキップ")
    args = ap.parse_args()

    config = load_config(args.config)
    prefectures = args.prefectures or config["prefectures"]
    cutoff = config["site_age_cutoff_year"]

    print(f"対象: {len(prefectures)} 都道府県 / サイト基準年: {cutoff}以前", file=sys.stderr)
    candidates = collect(
        config, prefectures, args.limit_per_pref, use_wayback=not args.no_wayback
    )

    all_path, target_path, n_targets = write_outputs(candidates, cutoff)
    print("\n=== 完了 ===", file=sys.stderr)
    print(f"全候補:           {len(candidates)} 件 -> {all_path}", file=sys.stderr)
    print(f"2015年以前サイト: {n_targets} 件 -> {target_path}", file=sys.stderr)
    print("次のステップ: 出力CSVの google_reviews 列を埋める(Google Mapで確認 or verify_reviews.py)", file=sys.stderr)


if __name__ == "__main__":
    main()
