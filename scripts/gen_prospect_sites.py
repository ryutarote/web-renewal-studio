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
    (("cafe", "喫茶", "coffee", "coffee_shop", "コーヒー", "internet_cafe"), "☕", "#92400e", "#73310a",
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
    (("yakiniku", "barbecue", "grill", "焼肉", "ホルモン"), "🥩", "#b91c1c", "#911414",
     ["上カルビ", "盛り合わせ", "希少部位"], "いい肉を、いい火で。",
     "厳選した肉を、最良の状態でお楽しみいただけるよう仕入れています。"),
    (("italian", "pizza", "pasta", "イタリ"), "🍝", "#15803d", "#106030",
     ["本日のパスタ", "窯焼きピッツァ", "前菜の盛り合わせ"], "素材を、素直に。",
     "旬の食材を活かしたイタリアンを、肩肘張らずに楽しめる一軒です。"),
    (("french", "western", "洋食", "bistro", "ビストロ"), "🍽️", "#1d4ed8", "#173da6",
     ["シェフのコース", "季節の魚料理", "本日のデザート"], "ひと皿に、季節を。",
     "季節の移ろいを映したお料理を、コースから一品まで取り揃えています。"),
    (("burger", "fast_food", "american", "バーガー"), "🍔", "#d97706", "#ad5e05",
     ["おすすめバーガー", "フライドポテト", "ドリンクセット"], "できたてを、頬張る。",
     "注文を受けてから仕上げる、できたての美味しさにこだわっています。"),
    (("bakery", "パン", "bread"), "🥐", "#a16207", "#7f4d05",
     ["人気の食事パン", "季節の菓子パン", "焼き菓子の詰め合わせ"], "毎朝、焼きたてを。",
     "毎朝店内で焼き上げるパンを、いちばんおいしい時間にお届けします。"),
    (("seafood", "海鮮", "魚", "fish", "kaisen", "海"), "🐟", "#0369a1", "#04557f",
     ["本日の鮮魚", "海鮮の盛り合わせ", "旬の地魚"], "海の恵みを、そのままに。",
     "その日に揚がった魚を、いちばんおいしい食べ方でご提供します。"),
    (("japanese", "hotpot", "chazuke", "和食", "regional", "teishoku", "定食", "郷土", "割烹", "kappo"), "🍱", "#4338ca", "#352aa3",
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
        "coffee_shop": "喫茶店", "barbecue": "焼肉・グリル", "grill": "グリル",
        "chazuke": "茶漬け", "hotpot": "鍋料理", "american": "アメリカ料理",
        "internet_cafe": "インターネットカフェ", "sandwich": "サンドイッチ",
        "curry": "カレー", "fish_and_chips": "フィッシュ&チップス",
        "pizza": "ピッツァ",
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


def photo_for_genre(genre):
    g = (genre or "").lower()
    photos = [
        (("coffee", "cafe", "喫茶", "internet_cafe"), "https://images.unsplash.com/photo-1509042239860-f550ce710b93?auto=format&fit=crop&w=1800&q=82"),
        (("sushi", "seafood", "fish", "海鮮", "魚"), "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?auto=format&fit=crop&w=1800&q=82"),
        (("barbecue", "yakiniku", "grill", "burger", "american", "fast_food"), "https://images.unsplash.com/photo-1550547660-d9450f859349?auto=format&fit=crop&w=1800&q=82"),
        (("chinese", "餃子"), "https://images.unsplash.com/photo-1525755662778-989d0524087e?auto=format&fit=crop&w=1800&q=82"),
        (("italian", "pizza", "pasta"), "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=1800&q=82"),
        (("french", "bistro", "western", "洋食"), "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?auto=format&fit=crop&w=1800&q=82"),
        (("bar", "pub", "izakaya", "酒"), "https://images.unsplash.com/photo-1514933651103-005eec06c04b?auto=format&fit=crop&w=1800&q=82"),
        (("hotpot", "japanese", "regional", "chazuke", "udon", "soba"), "https://images.unsplash.com/photo-1534939561126-855b8675edd7?auto=format&fit=crop&w=1800&q=82"),
    ]
    for keys, url in photos:
        if any(k in g for k in keys):
            return url
    return "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=1800&q=82"


def landing_css(accent, accent_ink, photo):
    return f'''
:root {{
  --ink: #171717;
  --muted: #66615b;
  --line: #e8e1d8;
  --paper: #fbfaf7;
  --panel: #ffffff;
  --accent: {accent};
  --accent-ink: {accent_ink};
  --accent-soft: color-mix(in srgb, {accent} 12%, #ffffff);
  --shadow: 0 24px 70px rgba(23, 23, 23, .12);
}}
* {{ box-sizing: border-box; }}
html {{ scroll-behavior: smooth; }}
body {{
  margin: 0;
  color: var(--ink);
  background: var(--paper);
  font-family: "Inter", "Hiragino Sans", "Hiragino Kaku Gothic ProN", "Noto Sans JP", Meiryo, sans-serif;
  line-height: 1.75;
}}
a {{ color: inherit; text-decoration: none; }}
.wrap {{ width: min(1120px, calc(100% - 40px)); margin: 0 auto; }}
.proposal-strip {{
  background: #111;
  color: rgba(255,255,255,.82);
  font-size: 12px;
  letter-spacing: .02em;
  padding: 8px 0;
}}
.proposal-strip b {{ color: #fff; font-weight: 700; }}
.site-header {{
  position: sticky;
  top: 0;
  z-index: 10;
  background: rgba(251, 250, 247, .86);
  border-bottom: 1px solid rgba(232, 225, 216, .78);
  backdrop-filter: blur(14px);
}}
.site-header .wrap {{
  min-height: 68px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}}
.brand {{
  display: flex;
  align-items: baseline;
  gap: 10px;
  min-width: 0;
  font-weight: 800;
  letter-spacing: .03em;
}}
.brand span {{
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}}
.brand small {{
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: .08em;
  text-transform: uppercase;
}}
.nav {{
  display: flex;
  align-items: center;
  gap: 20px;
  color: #4a4743;
  font-size: 13px;
  font-weight: 700;
}}
.nav a {{ min-height: 36px; display: inline-flex; align-items: center; }}
.btn {{
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border-radius: 6px;
  border: 1px solid transparent;
  padding: 10px 18px;
  font-size: 14px;
  font-weight: 800;
  line-height: 1.2;
  white-space: nowrap;
}}
.btn-primary {{ background: var(--accent); color: #fff; box-shadow: 0 14px 34px color-mix(in srgb, var(--accent) 28%, transparent); }}
.btn-secondary {{ background: rgba(255,255,255,.14); color: #fff; border-color: rgba(255,255,255,.36); }}
.btn-outline {{ background: #fff; color: var(--accent-ink); border-color: color-mix(in srgb, var(--accent) 28%, #d9d0c5); }}
.hero {{
  position: relative;
  min-height: min(720px, calc(100svh - 40px));
  display: grid;
  align-items: end;
  padding: clamp(110px, 16vh, 170px) 0 56px;
  color: #fff;
  isolation: isolate;
  background:
    linear-gradient(90deg, rgba(0,0,0,.70) 0%, rgba(0,0,0,.48) 45%, rgba(0,0,0,.18) 100%),
    linear-gradient(0deg, rgba(0,0,0,.48) 0%, transparent 38%),
    url("{photo}") center / cover no-repeat;
}}
.hero::after {{
  content: "";
  position: absolute;
  inset: auto 0 0;
  height: 130px;
  background: linear-gradient(0deg, var(--paper), transparent);
  z-index: -1;
}}
.hero-content {{ max-width: 760px; }}
.eyebrow {{
  display: inline-flex;
  align-items: center;
  gap: 10px;
  color: rgba(255,255,255,.86);
  font-size: 13px;
  font-weight: 800;
  letter-spacing: .12em;
  text-transform: uppercase;
}}
.eyebrow::before {{
  content: "";
  width: 36px;
  height: 2px;
  background: var(--accent);
}}
h1 {{
  margin: 18px 0 18px;
  max-width: 12em;
  font-family: Georgia, "Times New Roman", "Hiragino Mincho ProN", serif;
  font-size: clamp(44px, 8vw, 84px);
  line-height: .98;
  letter-spacing: 0;
  text-wrap: balance;
  overflow-wrap: anywhere;
}}
.hero-lead {{
  max-width: 650px;
  margin: 0;
  color: rgba(255,255,255,.88);
  font-size: clamp(16px, 2.1vw, 21px);
  font-weight: 600;
}}
.hero-actions {{ display: flex; flex-wrap: wrap; gap: 12px; margin-top: 30px; }}
.hero-meta {{
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1px;
  margin-top: 44px;
  max-width: 780px;
  border-radius: 8px;
  overflow: hidden;
  background: rgba(255,255,255,.18);
  border: 1px solid rgba(255,255,255,.18);
  backdrop-filter: blur(12px);
}}
.hero-meta div {{ padding: 16px 18px; background: rgba(0,0,0,.18); min-width: 0; }}
.hero-meta b {{ display: block; color: #fff; font-size: 13px; }}
.hero-meta span {{ color: rgba(255,255,255,.78); font-size: 12px; }}
.section {{ padding: clamp(64px, 8vw, 104px) 0; }}
.section + .section {{ border-top: 1px solid var(--line); }}
.section.alt {{ background: #fff; }}
.section-head {{
  display: flex;
  justify-content: space-between;
  align-items: end;
  gap: 24px;
  margin-bottom: 28px;
}}
.section-kicker {{
  color: var(--accent-ink);
  font-size: 12px;
  font-weight: 900;
  letter-spacing: .16em;
  text-transform: uppercase;
}}
h2 {{
  margin: 8px 0 0;
  font-size: clamp(28px, 4vw, 48px);
  line-height: 1.12;
  letter-spacing: 0;
  text-wrap: balance;
  overflow-wrap: anywhere;
}}
.section-copy {{ max-width: 560px; color: var(--muted); margin: 0; font-size: 15px; }}
.feature-grid {{
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}}
.feature {{
  min-height: 220px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 26px;
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 8px;
  box-shadow: 0 14px 42px rgba(23,23,23,.05);
}}
.feature strong {{ font-size: 24px; line-height: 1.25; letter-spacing: 0; }}
.feature p {{ color: var(--muted); margin: 18px 0 0; font-size: 14px; }}
.number {{ color: var(--accent); font-size: 13px; font-weight: 900; letter-spacing: .16em; }}
.story {{
  display: grid;
  grid-template-columns: minmax(0, .9fr) minmax(0, 1.1fr);
  gap: clamp(30px, 6vw, 72px);
  align-items: center;
}}
.story-visual {{
  min-height: 430px;
  border-radius: 8px;
  background:
    linear-gradient(180deg, rgba(0,0,0,.05), rgba(0,0,0,.22)),
    url("{photo}") center / cover no-repeat;
  box-shadow: var(--shadow);
}}
.story-text p {{ color: var(--muted); font-size: 17px; margin: 0 0 18px; }}
.menu-grid {{
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}}
.menu-item {{
  min-height: 162px;
  padding: 22px;
  border-radius: 8px;
  border: 1px solid var(--line);
  background: #fff;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}}
.menu-item b {{ font-size: 18px; line-height: 1.35; }}
.menu-item span {{ color: var(--muted); font-size: 13px; }}
.reserve {{
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 24px;
  align-items: stretch;
}}
.reserve-panel {{
  padding: clamp(28px, 5vw, 56px);
  border-radius: 8px;
  background: var(--ink);
  color: #fff;
}}
.reserve-panel p {{ color: rgba(255,255,255,.72); max-width: 660px; }}
.reserve-actions {{ display: flex; flex-wrap: wrap; gap: 12px; margin-top: 28px; }}
.info-card {{
  padding: 26px;
  border-radius: 8px;
  background: var(--accent-soft);
  border: 1px solid color-mix(in srgb, var(--accent) 24%, var(--line));
}}
.info-row {{
  display: grid;
  grid-template-columns: 86px minmax(0, 1fr);
  gap: 12px;
  padding: 13px 0;
  border-bottom: 1px solid color-mix(in srgb, var(--accent) 18%, #ddd);
  font-size: 14px;
}}
.info-row:last-child {{ border-bottom: 0; }}
.info-row b {{ color: var(--accent-ink); }}
.note {{ color: var(--muted); font-size: 12px; margin-top: 18px; }}
.footer {{
  padding: 30px 0 92px;
  color: var(--muted);
  border-top: 1px solid var(--line);
  font-size: 12px;
}}
.footer .wrap {{ display: grid; gap: 8px; }}
.actionbar {{
  position: fixed;
  z-index: 20;
  left: 50%;
  bottom: 16px;
  transform: translateX(-50%);
  width: min(720px, calc(100% - 28px));
  display: none;
  gap: 8px;
  padding: 8px;
  border-radius: 8px;
  background: rgba(255,255,255,.92);
  border: 1px solid var(--line);
  box-shadow: 0 18px 50px rgba(23,23,23,.16);
  backdrop-filter: blur(12px);
}}
.actionbar .btn {{ flex: 1; }}
@media (max-width: 820px) {{
  body {{ overflow-x: hidden; }}
  .wrap {{ width: min(100% - 28px, 1120px); }}
  .proposal-strip {{ font-size: 11px; line-height: 1.55; overflow-wrap: anywhere; word-break: break-all; }}
  .proposal-strip .wrap {{ width: min(100% - 24px, 1120px); white-space: normal; }}
  .site-header .wrap {{ min-height: 58px; gap: 10px; }}
  .brand {{ flex: 1; font-size: 15px; }}
  .nav {{ display: none; }}
  .nav a:not(.btn) {{ display: none; }}
  .nav .btn {{ min-height: 38px; padding: 8px 11px; font-size: 13px; }}
  .brand small {{ display: none; }}
  .hero {{ min-height: 690px; padding: 96px 0 42px; background-position: center; }}
  .hero-content {{ min-width: 0; max-width: 100%; }}
  h1 {{ max-width: 100%; font-size: clamp(38px, 12vw, 54px); line-height: 1.05; word-break: break-all; }}
  h2 {{ word-break: break-all; }}
  .hero-lead {{ font-size: 15px; line-height: 1.75; overflow-wrap: anywhere; word-break: break-all; }}
  .hero-meta {{ grid-template-columns: 1fr; margin-top: 32px; }}
  .section-head {{ display: block; }}
  .section-copy {{ margin-top: 14px; }}
  .feature-grid, .menu-grid, .story, .reserve {{ grid-template-columns: 1fr; }}
  .story-visual {{ min-height: 300px; order: -1; }}
  .reserve {{ gap: 14px; }}
  .actionbar {{ display: none; }}
  .hide-mobile {{ display: none; }}
}}
'''


def landing_page_html(p):
    name = p["shop_name"]
    area = p["area"]
    glabel = jp_genre_label(p.get("genre", ""))
    _emoji, accent, accent_ink, menu, tagline, concept = genre_info(p.get("genre", ""))
    photo = photo_for_genre(p.get("genre", ""))
    phone = p.get("phone", "").strip()
    tel_link = f'<a href="tel:{esc(phone)}">{esc(phone)}</a>' if phone else '<span>正式制作時に反映</span>'
    action_tel = (f'<a class="btn btn-outline" href="tel:{esc(phone)}">電話する</a>' if phone
                  else f'<a class="btn btn-outline" href="mailto:{SENDER_MAIL}">メールする</a>')
    features = [
        ("01", f"{glabel}らしさを一目で伝える", "初見でも料理・雰囲気・価格帯が伝わる構成で、検索後の離脱を抑えます。"),
        ("02", "予約と来店導線を近くする", "電話・Web予約・地図への移動を、スマホ画面でも迷わず押せる位置に配置します。"),
        ("03", "最新情報を更新しやすくする", "メニュー、営業時間、臨時休業などを運用しやすい形で整理します。"),
    ]
    feature_cards = "\n".join(
        f'''      <article class="feature">
        <div class="number">{n}</div>
        <div><strong>{esc(t)}</strong><p>{esc(d)}</p></div>
      </article>''' for n, t, d in features)
    menu_cards = "\n".join(
        f'''      <article class="menu-item">
        <b>{esc(item)}</b>
        <span>実制作では写真・価格・説明文を貴店データに差し替えます</span>
      </article>''' for item in menu)
    aux_tel = f' / {esc(phone)}' if phone else ""

    return f'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{esc(name)}｜Webリニューアル提案LP（{COMPANY}）</title>
<meta name="description" content="{esc(name)}（{esc(area)}・{esc(glabel)}）向けのプロフェッショナルなWebリニューアル提案LP。">
<meta property="og:title" content="{esc(name)}｜Webリニューアル提案LP">
<meta property="og:description" content="スマホ来店導線、店舗の世界観、更新しやすさを重視したランディングページ提案。">
<style>
{landing_css(accent, accent_ink, photo)}
</style>
</head>
<body>
<div class="proposal-strip"><div class="wrap">これは <b>{COMPANY}</b> によるWebリニューアル提案LPです。公式サイトではありません。</div></div>

<header class="site-header">
  <div class="wrap">
    <a class="brand" href="#"><span>{esc(name)}</span><small>{esc(area)} / {esc(glabel)}</small></a>
    <nav class="nav">
      <a href="#story">Concept</a>
      <a href="#menu">Menu</a>
      <a href="#visit">Visit</a>
      <a class="btn btn-outline" href="#contact">相談する</a>
    </nav>
  </div>
</header>

<main>
  <section class="hero">
    <div class="wrap">
      <div class="hero-content">
        <span class="eyebrow">{esc(area)} / {esc(glabel)}</span>
        <h1>{esc(name)}</h1>
        <p class="hero-lead">{esc(tagline)} {esc(concept)}</p>
        <div class="hero-actions">
          <a class="btn btn-primary" href="#contact">リニューアル相談</a>
          <a class="btn btn-secondary" href="#menu">メニューを見る</a>
        </div>
        <div class="hero-meta" aria-label="店舗情報">
          <div><b>Area</b><span>{esc(area)}</span></div>
          <div><b>Style</b><span>{esc(glabel)}</span></div>
          <div><b>Phone</b><span>{esc(phone) if phone else "制作時に反映"}</span></div>
        </div>
      </div>
    </div>
  </section>

  <section class="section alt">
    <div class="wrap">
      <div class="section-head">
        <div>
          <div class="section-kicker">Landing Page Design</div>
          <h2>来店前の期待感を、予約行動につなげる構成。</h2>
        </div>
        <p class="section-copy">スマホで見た瞬間に「どんな店か」「何を食べられるか」「どう予約するか」が伝わるよう、ファーストビューからCTAまでを整理した提案です。</p>
      </div>
      <div class="feature-grid">
{feature_cards}
      </div>
    </div>
  </section>

  <section class="section" id="story">
    <div class="wrap story">
      <div class="story-text">
        <div class="section-kicker">Concept</div>
        <h2>{esc(tagline)}</h2>
        <p>{esc(concept)}</p>
        <p>正式制作では、店内写真、看板メニュー、店主の想い、Googleビジネスプロフィールの情報を反映し、検索から来店までの流れを自然につくります。</p>
      </div>
      <div class="story-visual" aria-label="店舗イメージ"></div>
    </div>
  </section>

  <section class="section alt" id="menu">
    <div class="wrap">
      <div class="section-head">
        <div>
          <div class="section-kicker">Menu Highlights</div>
          <h2>看板メニューを、迷わず選べる見せ方に。</h2>
        </div>
        <p class="section-copy">料理写真と説明文を組み合わせ、初めてのお客様にもおすすめが伝わるメニュー導線を用意します。</p>
      </div>
      <div class="menu-grid">
{menu_cards}
      </div>
      <p class="note">掲載メニューは提案用サンプルです。正式版では実メニュー・価格・写真に差し替えます。</p>
    </div>
  </section>

  <section class="section" id="visit">
    <div class="wrap reserve">
      <div class="reserve-panel">
        <div class="section-kicker">Visit</div>
        <h2>予約、問い合わせ、地図をひとつの流れに。</h2>
        <p>スマートフォンでの閲覧を前提に、来店直前のユーザーが必要とする情報を下部CTAと店舗情報に集約します。</p>
        <div class="reserve-actions">
          <a class="btn btn-primary" href="{CAL}">打ち合わせ予約</a>
          {action_tel}
        </div>
      </div>
      <aside class="info-card" aria-label="店舗情報">
        <div class="info-row"><b>店舗</b><span>{esc(name)}</span></div>
        <div class="info-row"><b>エリア</b><span>{esc(area)}</span></div>
        <div class="info-row"><b>ジャンル</b><span>{esc(glabel)}</span></div>
        <div class="info-row"><b>電話</b>{tel_link}</div>
        <div class="info-row"><b>更新課題</b><span>{esc(p.get("renewal_reason", "Web導線の改善"))}</span></div>
      </aside>
    </div>
  </section>

  <section class="section alt" id="contact">
    <div class="wrap">
      <div class="section-head">
        <div>
          <div class="section-kicker">Renewal Proposal</div>
          <h2>この方向性で、正式な改善案を作成します。</h2>
        </div>
        <p class="section-copy">写真・営業時間・実メニューを反映したうえで、公開までの作業範囲と費用感をご案内します。</p>
      </div>
      <div class="reserve-actions">
        <a class="btn btn-primary" href="{CAL}">無料相談を予約する</a>
        <a class="btn btn-outline" href="mailto:{SENDER_MAIL}">メールで相談する</a>
      </div>
      <p class="note">{COMPANY} / {SENDER_MAIL}{aux_tel}</p>
    </div>
  </section>
</main>

<footer class="footer">
  <div class="wrap">
    <div>本ページは {COMPANY} が公開情報をもとに制作した提案サンプルです。{esc(name)} 様の公式サイトではありません。</div>
    <div>制作元: {COMPANY} / <a href="{BASE_URL}/">{BASE_URL}/</a></div>
  </div>
</footer>

<div class="actionbar" aria-label="固定アクション">
  {action_tel}
  <a class="btn btn-primary" href="#contact">相談する</a>
</div>
</body>
</html>
'''


def landing_gallery_html(items):
    cards = "\n".join(
        f'''      <a class="gallery-card" href="{esc(it['slug'])}/">
        <span>{esc(it['area'])}</span>
        <strong>{esc(it['shop_name'])}</strong>
        <small>{esc(jp_genre_label(it.get('genre','')))}</small>
      </a>''' for it in items)
    return f'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>プロフェッショナルLP提案デモ集（メール取得済み候補 {len(items)}件）｜{COMPANY}</title>
<style>
:root {{
  --ink: #171717;
  --muted: #66615b;
  --line: #e8e1d8;
  --paper: #fbfaf7;
  --accent: #0f766e;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  color: var(--ink);
  background: var(--paper);
  font-family: "Inter", "Hiragino Sans", "Hiragino Kaku Gothic ProN", "Noto Sans JP", Meiryo, sans-serif;
}}
a {{ color: inherit; text-decoration: none; }}
.wrap {{ width: min(1120px, calc(100% - 40px)); margin: 0 auto; }}
.hero {{
  min-height: 430px;
  display: grid;
  align-items: end;
  padding: 88px 0 58px;
  color: #fff;
  background:
    linear-gradient(90deg, rgba(0,0,0,.72), rgba(0,0,0,.25)),
    url("https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=1800&q=82") center / cover no-repeat;
}}
.kicker {{ color: rgba(255,255,255,.78); font-size: 13px; font-weight: 900; letter-spacing: .14em; text-transform: uppercase; }}
h1 {{ max-width: 820px; margin: 14px 0 0; font-size: clamp(40px, 7vw, 78px); line-height: 1.02; letter-spacing: 0; }}
.lead {{ max-width: 680px; color: rgba(255,255,255,.82); font-size: 17px; line-height: 1.8; }}
.section {{ padding: 58px 0 76px; }}
.gallery {{
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}}
.gallery-card {{
  min-height: 158px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 22px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 14px 38px rgba(23,23,23,.05);
}}
.gallery-card span {{ color: var(--accent); font-size: 12px; font-weight: 900; letter-spacing: .12em; text-transform: uppercase; }}
.gallery-card strong {{ font-size: 22px; line-height: 1.25; letter-spacing: 0; }}
.gallery-card small {{ color: var(--muted); font-size: 13px; }}
.note {{ color: var(--muted); font-size: 12px; margin-top: 28px; line-height: 1.8; }}
@media (max-width: 820px) {{
  .gallery {{ grid-template-columns: 1fr; }}
  .hero {{ min-height: 520px; }}
}}
</style>
</head>
<body>
<section class="hero">
  <div class="wrap">
    <div class="kicker">{COMPANY} / Renewal Proposal</div>
    <h1>プロフェッショナルLP提案デモ集</h1>
    <p class="lead">メール取得済み候補 {len(items)}件を、来店導線と店舗の世界観が伝わるランディングページ形式に再設計しました。</p>
  </div>
</section>
<section class="section">
  <div class="wrap">
    <div class="gallery">
{cards}
    </div>
    <p class="note">すべて {COMPANY} が公開情報をもとに制作した提案サンプルで、各店の公式サイトではありません。</p>
  </div>
</section>
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
            if outdir == "leads-email":
                f.write(landing_page_html(r))
            else:
                f.write(page_html(r, css))

    with open(os.path.join(site_root, "index.html"), "w", encoding="utf-8") as f:
        if outdir == "leads-email":
            f.write(landing_gallery_html(rows))
        else:
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
