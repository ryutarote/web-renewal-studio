#!/usr/bin/env python3
"""返信がない既送信先から、少数の追客メール対象を選ぶ。

出力CSVは data/.gitignore の対象なので公開しない。既送信ログから重複送信済みの
実態を見つつ、不達アドレスと通販/転送窓口寄りの宛先を避けて、返信しやすい順に
上位N件を選ぶ。
"""
import argparse
import csv
import os
import urllib.parse
from email.utils import parsedate_to_datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECIPIENTS = os.path.join(ROOT, "data", "recipients.csv")
SENT_LOG = os.path.join(ROOT, "data", "sent_log.csv")
BOUNCES = os.path.join(ROOT, "data", "bounces.csv")

OUT_FIELDS = [
    "slug",
    "shop_name",
    "area_genre",
    "demo_url",
    "tracked_demo_url",
    "email",
    "first_sent_at",
    "last_sent_at",
    "sent_count",
    "notes",
    "score",
]


def read_csv(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def load_bounces(path):
    rows = read_csv(path)
    return {
        (r.get("email") or r.get("to") or "").strip().lower()
        for r in rows
        if (r.get("email") or r.get("to") or "").strip()
    }


def sent_summary(path):
    by_slug = {}
    for r in read_csv(path):
        if r.get("status") != "sent":
            continue
        slug = r.get("slug", "")
        if not slug:
            continue
        by_slug.setdefault(slug, []).append(r)
    out = {}
    for slug, rows in by_slug.items():
        dates = []
        for r in rows:
            try:
                dates.append(parsedate_to_datetime(r["ts"]))
            except Exception:
                pass
        out[slug] = {
            "count": len(rows),
            "first": min(dates).isoformat() if dates else "",
            "last": max(dates).isoformat() if dates else "",
        }
    return out


def score_row(row):
    notes = row.get("notes", "")
    email = row.get("email", "").lower()
    score = 0
    positive = ("お問い合わせ", "問い合わせ", "会社概要", "公式サイト", "公式連絡先", "公式mailto", "プライバシー")
    negative = ("通販", "特商法", "楽天", "Yahoo", "オンラインショップ", "転送", "shopserve")
    if any(k in notes for k in positive):
        score += 40
    if any(k in notes for k in negative):
        score -= 22
    if email.startswith(("info@", "contact@", "inquiry@")):
        score += 12
    if any(domain in email for domain in ("gmail.com", "nifty.com", "ocn.ne.jp", "shop.rakuten.co.jp")):
        score -= 12
    if row.get("area_genre"):
        score += 4
    return score


def tracking_url(base, campaign, slug):
    parsed = urllib.parse.urlsplit(base)
    params = dict(urllib.parse.parse_qsl(parsed.query, keep_blank_values=True))
    params.update({
        "utm_source": "outreach",
        "utm_medium": "email",
        "utm_campaign": campaign,
        "utm_content": slug,
    })
    return urllib.parse.urlunsplit(parsed._replace(query=urllib.parse.urlencode(params)))


def main():
    ap = argparse.ArgumentParser(description="追客メールの少数バッチを生成")
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--campaign", default="followup_20260702")
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "followup_20260702.csv"))
    ap.add_argument("--recipients", default=RECIPIENTS)
    ap.add_argument("--sent-log", default=SENT_LOG)
    ap.add_argument("--bounces", default=BOUNCES)
    args = ap.parse_args()

    sent = sent_summary(args.sent_log)
    bounces = load_bounces(args.bounces)
    rows = []
    for r in read_csv(args.recipients):
        email = r.get("email", "").strip().lower()
        slug = r.get("slug", "")
        if not email or email in bounces or slug not in sent:
            continue
        item = {k: r.get(k, "") for k in ("slug", "shop_name", "area_genre", "demo_url", "email", "notes")}
        item["tracked_demo_url"] = tracking_url(item["demo_url"], args.campaign, slug)
        item["first_sent_at"] = sent[slug]["first"]
        item["last_sent_at"] = sent[slug]["last"]
        item["sent_count"] = str(sent[slug]["count"])
        item["score"] = str(score_row(r))
        rows.append(item)

    rows.sort(key=lambda r: (int(r["score"]), r["shop_name"]), reverse=True)
    rows = rows[:args.limit]

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=OUT_FIELDS)
        w.writeheader()
        w.writerows(rows)

    print(f"wrote {len(rows)} follow-up targets -> {args.out}")
    for r in rows:
        print(f"{r['score']:>3}  {r['slug']}  {r['shop_name']}  {r['email']}")


if __name__ == "__main__":
    main()
