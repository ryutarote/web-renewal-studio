#!/usr/bin/env python3
"""営業リード抽出（APIなし）: 地方中核市の飲食店で「サイト無し/古い/要改善」を列挙。

データ源（無料）:
  - OpenStreetMap (Overpass API): 指定bbox内の飲食店 + website タグ
  - 各店サイトを軽量HTTP点検: SSL有無 / viewport(モバイル対応) / 文字コード / Copyright年 / 旧記法

Google Mapレビュー数は無料の自動取得手段が無いため、各店に「Google Map確認リンク」を付与し
レビュー数は TODO(手動確認) とする。チェーンは config.json の blacklist で除外。
"""
import json, re, csv, os, sys, time, urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
UA = {"User-Agent": "renewal-leadfinder/1.0 (OSM; site-audit)"}
OVERPASS = "https://overpass-api.de/api/interpreter"

# 中心部bbox (south, west, north, east)
CITIES = {
    "仙台市中心部": (38.250, 140.860, 38.275, 140.892),
    "名古屋市中心部": (35.155, 136.878, 35.185, 136.918),
    "福岡市中心部": (33.578, 130.392, 33.606, 130.430),
}

with open(os.path.join(ROOT, "scripts", "config.json"), encoding="utf-8") as f:
    BLACK = json.load(f)["chain_blacklist"]
# 追加のチェーン/全国系（飲食特化の補強）
BLACK += ["スターバックス","ドトール","タリーズ","コメダ","サンマルク","エクセルシオール",
          "マクドナルド","モスバーガー","ロッテリア","ケンタッキー","フレッシュネス","バーガーキング",
          "すき家","吉野家","松屋","なか卯","てんや","かつや","松のや","日高屋","リンガーハット",
          "丸亀製麺","はなまる","餃子の王将","大阪王将","ガスト","サイゼリヤ","ジョナサン","バーミヤン",
          "ココス","デニーズ","ロイヤルホスト","ジョイフル","びっくりドンキー","大戸屋","やよい軒",
          "スシロー","くら寿司","はま寿司","かっぱ寿司","魚べい","銚子丸","元気寿司",
          "鳥貴族","ワタミ","白木屋","魚民","笑笑","千年の宴","montoku","ミライザカ","三代目鳥メロ",
          "一風堂","一蘭","天下一品","スガキヤ","ミスタードーナツ","サーティワン","KFC",
          "willer","スタバ","スシロー","スシロー","Starbucks","McDonald","モリバ","プロント","ベローチェ",
          "やきとり","串カツ田中","磯丸水産","チムニー","とりからケンちゃん","willvii"]
BLACK = list(dict.fromkeys(BLACK))

def is_chain(name):
    return any(b and b.lower() in name.lower() for b in BLACK)

def overpass(bbox):
    s,w,n,e = bbox
    q = f"""
[out:json][timeout:90];
(
  nwr["amenity"~"restaurant|cafe|bar|pub|fast_food"]["name"]({s},{w},{n},{e});
);
out center tags;"""
    for attempt in range(3):
        try:
            r = requests.post(OVERPASS, data={"data": q}, headers=UA, timeout=120)
            if r.status_code == 200:
                return r.json().get("elements", [])
        except Exception as ex:
            print("  overpass retry:", ex)
        time.sleep(3*(attempt+1))
    return []

def audit_site(url):
    """サイトを点検して問題シグナルを返す。"""
    sig = []
    if url.startswith("http://"):
        sig.append("http(非SSL)")
    try:
        r = requests.get(url, headers=UA, timeout=8, allow_redirects=True)
        final = r.url
        if url.startswith("http://") and final.startswith("https://"):
            sig = [s for s in sig if s != "http(非SSL)"]  # httpsへ自動昇格していればSSLはOK
        html = r.text[:200000]
        low = html.lower()
        # モバイル対応(viewport)
        if "name=\"viewport\"" not in low and "name='viewport'" not in low:
            sig.append("モバイル非対応(viewport無)")
        # 旧文字コード
        m = re.search(r'charset=["\']?\s*(shift_jis|shift-jis|x-sjis|euc-jp)', low)
        if m: sig.append(f"旧エンコーディング({m.group(1)})")
        # 旧記法
        if "<frameset" in low or "<frame " in low: sig.append("frameset(旧)")
        if "<font" in low: sig.append("<font>タグ(旧)")
        if ".swf" in low or "shockwave-flash" in low: sig.append("Flash(廃止)")
        if low.count("<table") >= 3 and "name=\"viewport\"" not in low:
            sig.append("テーブルレイアウト疑い")
        # Copyright年
        yrs = re.findall(r'(?:©|copyright|&copy;)\s*\D{0,12}((?:19|20)\d{2})', low)
        yrs += re.findall(r'((?:19|20)\d{2})\s*[-–]\s*((?:19|20)\d{2})', html)
        flat = []
        for y in yrs:
            flat += list(y) if isinstance(y, tuple) else [y]
        years = [int(y) for y in flat if y.isdigit()]
        if years:
            latest = max(years)
            if latest <= 2019:
                sig.append(f"Copyright {latest}(更新停滞疑い)")
        return ("OK" if r.status_code < 400 else f"HTTP {r.status_code}", final, sig)
    except requests.exceptions.SSLError:
        return ("SSLエラー", url, sig + ["SSL証明書エラー"])
    except Exception as ex:
        return (f"到達不可({type(ex).__name__})", url, sig + ["サイト到達不可"])

def gmap_link(name, city):
    q = urllib.parse.quote(f"{name} {city.replace('中心部','')}")
    return f"https://www.google.com/maps/search/?api=1&query={q}"

def main():
    os.makedirs(DATA, exist_ok=True)
    rows = []
    for city, bbox in CITIES.items():
        print(f"[Overpass] {city} ...")
        els = overpass(bbox)
        print(f"  取得 {len(els)} 件")
        seen = set()
        for e in els:
            t = e.get("tags", {})
            name = t.get("name","").strip()
            if not name or name in seen: continue
            if is_chain(name): continue
            seen.add(name)
            site = (t.get("website") or t.get("contact:website") or "").strip()
            if site and not site.lower().startswith("http"):
                site = "http://" + site  # スキーム無しURLを正規化
            genre = t.get("cuisine") or t.get("amenity") or ""
            addr = t.get("addr:full") or " ".join(filter(None,[t.get("addr:quarter",""),t.get("addr:neighbourhood",""),t.get("addr:street","")])) or ""
            rows.append({"city":city,"name":name,"genre":genre,"addr":addr,"site":site,"bad":False})
        time.sleep(2)

    # サイト点検（URLあり）を並列で
    targets = [r for r in rows if r["site"].startswith("http")]
    print(f"\n[サイト点検] {len(targets)} 件を点検中 ...")
    def work(r):
        status, final, sig = audit_site(r["site"])
        r["status"]=status; r["final"]=final; r["signals"]="; ".join(sig)
        r["bad"]= bool(sig)
        return r
    with ThreadPoolExecutor(max_workers=12) as ex:
        for fut in as_completed([ex.submit(work, r) for r in targets]):
            fut.result()

    for r in rows:
        if not r["site"]:
            r["status"]="サイト無し(OSM未登録)"; r["final"]=""; r["signals"]="公式サイト未登録（要・Google確認）"; r["bad"]=True
        r["gmap"]=gmap_link(r["name"], r["city"])

    # ランク: 古い/要改善サイト > サイト無し
    def score(r):
        s = r.get("signals","")
        sc = 0
        if "http(非SSL)" in s: sc+=5
        if "モバイル非対応" in s: sc+=4
        if "旧エンコーディング" in s: sc+=4
        if "frameset" in s or "Flash" in s: sc+=5
        if "<font>" in s or "テーブルレイアウト" in s: sc+=3
        if "Copyright" in s: sc+=2
        if "到達不可" in r.get("status","") or "SSL" in r.get("status",""): sc+=4
        if r["status"].startswith("サイト無し"): sc+=1
        return sc
    leads = [r for r in rows if r["bad"]]
    leads.sort(key=score, reverse=True)

    out_csv = os.path.join(DATA, "renewal_leads.csv")
    with open(out_csv,"w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f, fieldnames=["city","name","genre","status","signals","site","final","addr","gmap"])
        w.writeheader()
        for r in leads: w.writerow({k:r.get(k,"") for k in w.fieldnames})

    # サマリ
    print(f"\n=== 集計 ===")
    print(f"総飲食店(チェーン除外後): {len(rows)}")
    oldsite = [r for r in leads if r["site"]]
    nosite  = [r for r in leads if not r["site"]]
    print(f"  古い/要改善サイト: {len(oldsite)} 件")
    print(f"  サイト無し(OSM未登録): {len(nosite)} 件")
    print(f"  → CSV: {out_csv}")
    print(f"\n--- 【最優先】古い/要改善サイト 上位30 ---")
    for i,r in enumerate(oldsite[:30],1):
        print(f"{i:2}. [{r['city'].replace('中心部','')}] {r['name']}｜{r['genre']}｜{r['signals']}｜{r['final'] or r['site']}")

if __name__=="__main__":
    main()
