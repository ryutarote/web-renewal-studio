#!/usr/bin/env python3
"""見込み客(prospects_*.csv)向けに、軽量・自己完結のリニューアル提案デモを量産する。

デザインは design-system/site.css（Claude Design同期のデザインシステム ver.2）を
インライン展開し、ジャンル別アクセントを各ページで注入する。1ファイル自己完結。

使い方:
  python3 scripts/gen_prospect_sites.py data/prospects_100_batch3.csv leads-b3
"""
import csv, os, re, sys, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_URL = "https://ryutarote.github.io/web-renewal-studio"
COMPANY = "コエテク合同会社"
SENDER_MAIL = "support@koetech.jp"
CAL = "https://timerex.net/s/ryutarote_5007/d6cb0d61"
SITE_CSS = os.path.join(ROOT, "design-system", "site.css")

ROMAJI = {
    "札幌市": "sapporo", "仙台市": "sendai", "横浜市": "yokohama", "名古屋市": "nagoya",
    "京都市": "kyoto", "大阪市": "osaka", "広島市": "hiroshima", "福岡市": "fukuoka",
    "神戸市": "kobe", "川崎市": "kawasaki", "さいたま市": "saitama", "千葉市": "chiba",
    "静岡市": "shizuoka", "岡山市": "okayama", "熊本市": "kumamoto", "金沢市": "kanazawa",
}

# (キーワード, emoji, accent, accent_ink, [サンプルメニュー], tagline, concept)
GENRES = [
    (("sushi", "寿司", "鮨", "すし"), "🍣", "#0e7490", "#0b5563",
     ["旬の握り盛り合わせ", "本日の鮮魚", "海鮮丼"], "旬の鮮度を、握りたてで。",
     "市場から届く旬の魚を、職人がその日いちばんの状態で握ります。"),
    (("ramen", "ラーメン", "noodle", "麺", "つけ麺"), "🍜", "#b91c1c", "#8f1414",
     ["特製らーめん", "つけ麺", "味玉トッピング"], "一杯に、店主のこだわりを。",
     "スープ・麺・具材のすべてに手をかけた、ここだけの一杯をご用意しています。"),
    (("soba", "そば", "蕎麦", "udon", "うどん"), "🥢", "#4d7c0f", "#3a5e0b",
     ["せいろ", "天ざる", "季節の変わりそば"], "香りを、手繰る。",
     "石臼挽きの粉を毎日打ち、喉ごしと香りを大切にお出ししています。"),
    (("cafe", "喫茶", "coffee", "コーヒー"), "☕", "#92400e", "#73310a",
     ["本日のコーヒー", "自家製スイーツ", "ランチプレート"], "街に流れる、ゆっくりした時間。",
     "一杯ずつ丁寧に淹れるコーヒーと、手づくりのお菓子でひと息つける場所です。"),
    (("bar", "pub", "居酒屋", "izakaya", "酒", "lounge"), "🍶", "#6d28d9", "#561fb0",
     ["おすすめの一品", "厳選地酒", "季節のおつまみ"], "一日の終わりに、一杯を。",
     "気の合う人と、旨い酒と肴で過ごす。そんな夜にちょうどいい一軒です。"),
    (("chinese", "中華", "餃子"), "🥟", "#be123c", "#9a0e30",
     ["本格中華コース", "点心の盛り合わせ", "麻婆豆腐"], "火を入れる、旨さを。",
     "強い火力で仕上げる本格中華を、気軽な一品からコースまで取り揃えています。"),
    (("yakitori", "焼き鳥", "焼鳥", "chicken", "串"), "🍢", "#c2410c", "#9a330a",
     ["串の盛り合わせ", "自家製つくね", "地鶏の炭火焼"], "炭火で、香ばしく。",
     "備長炭でじっくり焼き上げる串を、一本ずつ丁寧にお出しします。"),
    (("yakiniku", "焼肉", "ホルモン"), "🥩", "#b91c1c", "#911414",
     ["上カルビ", "盛り合わせ", "希少部位"], "いい肉を、いい火で。",
     "厳選した肉を、最良の状態でお楽しみいただけるよう仕入れています。"),
    (("italian", "pizza", "pasta", "イタリ"), "🍝", "#15803d", "#106030",
     ["本日のパスタ", "窯焼きピッツァ", "前菜の盛り合わせ"], "素材を、素直に。",
     "旬の食材を活かしたイタリアンを、肩肘張らずに楽しめる一軒です。"),
    (("french", "western", "洋食", "bistro", "ビストロ"), "🍽️", "#1d4ed8", "#173da6",
     ["シェフのコース", "季節の魚料理", "本日のデザート"], "ひと皿に、季節を。",
     "季節の移ろいを映したお料理を、コースから一品まで取り揃えています。"),
    (("burger", "fast_food", "バーガー"), "🍔", "#d97706", "#ad5e05",
     ["おすすめバーガー", "フライドポテト", "ドリンクセット"], "できたてを、頬張る。",
     "注文を受けてから仕上げる、できたての美味しさにこだわっています。"),
    (("bakery", "パン", "bread"), "🥐", "#a16207", "#7f4d05",
     ["人気の食事パン", "季節の菓子パン", "焼き菓子の詰め合わせ"], "毎朝、焼きたてを。",
     "毎朝店内で焼き上げるパンを、いちばんおいしい時間にお届けします。"),
    (("seafood", "海鮮", "魚", "fish", "kaisen", "海"), "🐟", "#0369a1", "#04557f",
     ["本日の鮮魚", "海鮮の盛り合わせ", "旬の地魚"], "海の恵みを、そのままに。",
     "その日に揚がった魚を、いちばんおいしい食べ方でご提供します。"),
    (("japanese", "和食", "regional", "teishoku", "定食", "郷土", "割烹", "kappo"), "🍱", "#4338ca", "#352aa3",
     ["旬のおまかせ", "季節の一品", "本日の定食"], "四季を、一皿に。",
     "地の食材を活かした和の料理を、ていねいにお出しします。"),
]
FALLBACK = ("🍴", "#0f766e", "#0b5a53",
            ["おすすめ料理", "本日の一品", "おまかせコース"], "素材を活かした、一皿を。",
            "地元で愛される味を、ていねいにお出ししています。")


def esc(x):
    return html.escape(str(x or ""), quote=True)


def site_css():
    return open(SITE_CSS, encoding="utf-8").read()


def genre_info(genre):
    g = (genre or "").lower()
    for keys, emoji, a, a2, menu, tag, concept in GENRES:
        if any(k.lower() in g for k in keys):
            return emoji, a, a2, menu, tag, concept
    return FALLBACK


def jp_genre_label(genre):
    m = {
        "sushi": "寿司", "ramen": "ラーメン", "noodle": "麺料理", "soba": "そば",
        "udon": "うどん", "cafe": "カフェ", "coffee": "喫茶", "bar": "バー",
        "pub": "酒場", "chinese": "中華料理", "japanese": "和食", "regional": "郷土料理",
        "seafood": "海鮮", "italian": "イタリアン", "french": "フレンチ",
        "western": "洋食", "chicken": "鶏料理", "yakitori": "焼き鳥",
        "yakiniku": "焼肉", "fast_food": "ファストフード", "burger": "バーガー",
        "restaurant": "レストラン", "bakery": "ベーカリー", "bistro": "ビストロ",
    }
    parts = re.split(r"[;,/・]", genre or "")
    out = [m.get(p.strip().lower(), p.strip()) for p in parts if p.strip()]
    return "・".join(dict.fromkeys(out)) or "飲食店"


def accent_style(accent, accent_ink):
    return (f":root{{--accent:{accent};--accent-ink:{accent_ink};"
            f"--accent-wash:color-mix(in srgb,{accent} 9%,transparent)}}")


def page_html(p, css):
    name = p["shop_name"]
    area = p["area"]
    glabel = jp_genre_label(p.get("genre", ""))
    emoji, accent, accent_ink, menu, tagline, concept = genre_info(p.get("genre", ""))
    phone = p.get("phone", "").strip()
    tel = (f'<a class="tel" href="tel:{esc(phone)}">{esc(phone)}</a>'
           if phone else '<span style="color:var(--muted)">提案後にご案内</span>')
    menu_items = "\n".join(
        f'''      <div class="ds-menu-item">
        <span class="mi-emoji">{emoji}</span>
        <span><span class="mi-name">{esc(item)}{'<span class="ds-badge">人気</span>' if i == 0 else ''}</span><span class="mi-sub">サンプル表示</span></span>
        <span class="mi-dot"></span>
        <span class="mi-price">¥—</span>
      </div>''' for i, item in enumerate(menu))
    highlights = [
        (emoji, f"こだわりの{glabel}", "素材と手仕事を大切に、ていねいに仕上げます。"),
        ("🪑", "落ち着いた店内で", f"{area}で、ゆっくりとお過ごしいただけます。"),
        ("📅", "かんたんご予約", "お電話・オンラインからスムーズにご予約いただけます。"),
    ]
    hl_cards = "\n".join(
        f'''      <div class="ds-hl"><div class="ic">{ic}</div><h3>{esc(t)}</h3><p>{esc(d)}</p></div>'''
        for ic, t, d in highlights)
    bar_left = (f'<a class="ds-btn ds-btn--line" style="background:var(--surface)" href="tel:{esc(phone)}">☎ お電話</a>'
                if phone else f'<a class="ds-btn ds-btn--line" style="background:var(--surface)" href="mailto:{SENDER_MAIL}">メール</a>')
    aux_tel = f'　/　<a href="tel:{esc(phone)}">☎ {esc(phone)}</a>' if phone else ''

    return f'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{esc(name)}｜リニューアル提案デモ（{COMPANY}）</title>
<meta name="description" content="{esc(name)}（{esc(area)}・{esc(glabel)}）のWebサイト リニューアル提案デモ。{COMPANY}が公開情報をもとに試作したサンプルです。">
<meta property="og:title" content="{esc(name)}｜リニューアル提案デモ">
<meta property="og:description" content="スマホ対応・高速表示・予約導線を備えた、現代的な構成案（サンプル）。">
<style>
{css}
{accent_style(accent, accent_ink)}
</style>
</head>
<body>
<div class="ds-demo-bar">これは <b>{COMPANY}</b> による<b>リニューアル提案デモ</b>です。実在の {esc(name)} 様の公式サイトではありません（料金は発生しません）。</div>

<header class="ds-header"><div class="wrap">
  <div class="ds-brand"><span class="mk">{emoji}</span>{esc(name)}</div>
  <div class="ds-nav-wrap">
    <nav class="ds-nav"><a href="#reasons">選ばれる理由</a><a href="#menu">お品書き</a><a href="#access">アクセス</a></nav>
    <a class="ds-btn ds-btn--fill" href="#contact">ご予約</a>
  </div>
</div></header>

<section class="ds-hero"><div class="wrap">
  <div class="mark">{emoji}</div>
  <span class="eyebrow">{esc(area)} ／ {esc(glabel)}</span>
  <h1>{esc(name)}</h1>
  <p class="lead">{esc(tagline)}<br>{esc(concept)}</p>
  <div class="actions">
    <a class="ds-btn ds-btn--fill" href="#contact">ご予約・お問い合わせ</a>
    <a class="ds-btn ds-btn--line" href="#menu">お品書きを見る</a>
  </div>
</div></section>

<div class="ds-proof"><div class="wrap">
  <span class="stars">★★★★★</span>
  <span class="quote">「また来たくなる、{esc(area)}の一軒。」</span>
  <span class="src">— お客様の声（実装イメージ。実サイトではGoogle口コミ等を掲載）</span>
</div></div>

<section class="ds-section" id="reasons"><div class="wrap">
  <div class="ds-head"><span class="ds-index">01</span><span class="ds-label">Why us</span></div>
  <h2 class="ds-h2" style="margin-bottom:.7em">選ばれる理由</h2>
  <div class="ds-highlights">
{hl_cards}
  </div>
</div></section>

<section class="ds-section ds-section--alt" id="concept"><div class="wrap">
  <div class="ds-head"><span class="ds-index">02</span><span class="ds-label">Concept</span></div>
  <h2 class="ds-h2" style="margin-bottom:.5em">こだわり</h2>
  <p class="ds-lead-text">{esc(concept)}<br><span style="color:var(--muted);font-size:14px">※本デモの紹介文はジャンルに合わせた構成サンプルです。実制作では貴店の歴史・看板メニュー・写真を反映します。</span></p>
</div></section>

<section class="ds-section" id="menu"><div class="wrap">
  <div class="ds-head"><span class="ds-index">03</span><span class="ds-label">Menu</span></div>
  <h2 class="ds-h2" style="margin-bottom:.6em">お品書き</h2>
  <div class="ds-menu">
{menu_items}
  </div>
  <p class="ds-note">※メニュー名・価格は提案用のサンプル表示です。実データ（実メニュー・写真・価格）を反映して正式版を制作します。</p>
</div></section>

<section class="ds-section ds-section--alt" id="access"><div class="wrap">
  <div class="ds-head"><span class="ds-index">04</span><span class="ds-label">Access</span></div>
  <h2 class="ds-h2" style="margin-bottom:.7em">アクセス・ご利用案内</h2>
  <div class="ds-access">
    <div class="ds-info">
      <div class="row"><span class="k">エリア</span><span>{esc(area)}</span></div>
      <div class="row"><span class="k">ジャンル</span><span>{esc(glabel)}</span></div>
      <div class="row"><span class="k">電話</span>{tel}</div>
      <div class="row"><span class="k">営業時間</span><span style="color:var(--muted)">提案後に実データを反映</span></div>
    </div>
    <div class="ds-map">📍 地図はこの位置に表示されます</div>
  </div>
</div></section>

<section class="ds-section" id="contact"><div class="wrap">
  <div class="ds-cta">
    <span class="ds-label">Renewal Proposal</span>
    <h2>このデザインで、正式サイトを無料でご提案します</h2>
    <p>スマホ対応・表示速度・予約/通販導線・常時SSLを備えた構成案です。実データを反映したお見積り・正式提案をご案内します。</p>
    <div class="actions">
      <a class="ds-btn ds-btn--fill" href="{CAL}">お打ち合わせを予約する</a>
      <a class="ds-btn ds-btn--ghost" href="mailto:{SENDER_MAIL}">メールで問い合わせ</a>
    </div>
    <div class="ds-reserve-aux">ご予約・お問い合わせはお気軽に{aux_tel}</div>
  </div>
</div></section>

<footer class="ds-footer"><div class="wrap">
  <div class="disc">※本ページは {COMPANY} が公開情報をもとに独自に制作した<b>リニューアル提案サンプル</b>です。掲載情報は参考値で、{esc(name)} 様の公式サイトではありません。料金は一切発生しません。</div>
  <div>{COMPANY}　Mail: {SENDER_MAIL}　／　制作実績: <a href="{BASE_URL}/">{BASE_URL}/</a></div>
</div></footer>

<div class="ds-actionbar">
  {bar_left}
  <a class="ds-btn ds-btn--fill" href="#contact">ご予約・お問い合わせ</a>
</div>
</body>
</html>
'''


def gallery_title(outdir):
    labels = {
        "leads-b3": "第3弾",
        "leads-email": "メール取得済み候補",
    }
    return labels.get(outdir, outdir)


def gallery_html(items, outdir, css):
    title = gallery_title(outdir)
    cards = "\n".join(
        f'''    <a href="{esc(it['slug'])}/">
      <div class="em">{genre_info(it.get('genre',''))[0]}</div>
      <div class="nm">{esc(it['shop_name'])}</div>
      <div class="sb">{esc(it['area'])} ／ {esc(jp_genre_label(it.get('genre','')))}</div>
    </a>''' for it in items)
    return f'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>リニューアル提案デモ集（{esc(title)} {len(items)}件）｜{COMPANY}</title>
<style>
{css}
</style>
</head>
<body>
<section class="ds-hero"><div class="wrap">
  <span class="eyebrow">{COMPANY}｜Renewal Proposal</span>
  <h1>提案デモ集　{esc(title)}</h1>
  <p class="lead">各店の旧サイト改善を体現した、スマホ対応・常時SSL・高速表示の構成サンプル（全{len(items)}件）。</p>
</div></section>
<section class="ds-section"><div class="wrap">
  <div class="ds-gal">
{cards}
  </div>
  <p class="ds-note" style="margin-top:30px">※すべて {COMPANY} が公開情報をもとに制作した提案サンプルで、各店の公式サイトではありません。</p>
</div></section>
</body>
</html>
'''


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "data", "prospects_100_batch3.csv")
    outdir = sys.argv[2] if len(sys.argv) > 2 else "leads-b3"
    rows = list(csv.DictReader(open(src, encoding="utf-8-sig")))
    css = site_css()
    site_root = os.path.join(ROOT, "sites", outdir)
    os.makedirs(site_root, exist_ok=True)

    used = set()
    for r in rows:
        romaji = ROMAJI.get(r["area"], "shop")
        slug = f"{romaji}-{int(r['rank']):03d}"
        while slug in used:
            slug += "x"
        used.add(slug)
        r["slug"] = slug
        r["demo_url"] = f"{BASE_URL}/{outdir}/{slug}/"
        d = os.path.join(site_root, slug)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
            f.write(page_html(r, css))

    with open(os.path.join(site_root, "index.html"), "w", encoding="utf-8") as f:
        f.write(gallery_html(rows, outdir, css))

    fields = list(rows[0].keys())
    for c in ("slug", "demo_url"):
        if c not in fields:
            fields.append(c)
    with open(src, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    print(f"生成: {len(rows)} デモ -> sites/{outdir}/<slug>/index.html")
    print(f"ギャラリー: sites/{outdir}/index.html  ({BASE_URL}/{outdir}/)")


if __name__ == "__main__":
    main()
