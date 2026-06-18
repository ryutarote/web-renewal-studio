#!/usr/bin/env python3
"""候補30店のリニューアル提案モックをデータ駆動で生成する。冪等。

テンプレ（sites/fukui-yoroppaken）の css/main.js を流用し、:rootトークン・ヒーロー配色・
絵文字・SITE/ROUTES/DESC・空カート文言を差し替え、index.html / shop.js はデータから生成する。
データは scripts/candidate_data.py（CANDIDATES: list[dict]）。

使い方:
  python3 scripts/gen_candidate_sites.py            # 全件
  python3 scripts/gen_candidate_sites.py slug1 slug2 # 指定slugのみ
"""
import sys, re, pathlib, html, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from candidate_data import CANDIDATES

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITES = ROOT / "sites"
TPL = SITES / "fukui-yoroppaken"

def esc(x): return html.escape(str(x), quote=True)

# ---------- CSS ----------
def build_css(s):
    css = (TPL/"css"/"style.css").read_text(encoding="utf-8")
    t = s["css"]["tokens"]
    token_block = f"""  --background: {t['background']};
  --foreground: {t['foreground']};
  --card: {t['card']};
  --card-foreground: {t['card_fg']};
  --muted: {t['muted']};
  --muted-foreground: {t['muted_fg']};
  --primary: {t['primary']};
  --primary-foreground: {t['primary_fg']};
  --secondary: {t['secondary']};
  --secondary-foreground: {t['secondary_fg']};
  --accent: {t['accent']};
  --accent-foreground: {t['accent_fg']};
  --destructive: {t['destructive']};
  --border: {t['border']};
  --input: {t['input']};
  --ring: {t['ring']};"""
    # :root のトークン群（--background 〜 --ring）を置換
    css = re.sub(r'  --background:.*?  --ring:[^\n]*', token_block, css, count=1, flags=re.S)
    # ヘッダーコメント
    css = css.replace("   ヨーロッパ軒 総本店 リニューアル（モック）", f"   {s['name']} リニューアル（モック）", 1)
    # ヒーロー配色
    css = css.replace(
        "    radial-gradient(70% 120% at 50% -10%, hsl(30 80% 40% / .55), transparent 60%),\n    linear-gradient(160deg, hsl(23 50% 30%) 0%, hsl(23 56% 18%) 85%);",
        f"    radial-gradient(70% 120% at 50% -10%, {s['css']['hero_radial']}, transparent 60%),\n    linear-gradient(160deg, {s['css']['hero_lin1']} 0%, {s['css']['hero_lin2']} 85%);", 1)
    # 料理プレースホルダ絵文字
    de = s["css"]["dish_emojis"]  # [katsu, pari, mix]
    css = css.replace('.dish-photo::after { content: "🍱"', f'.dish-photo::after {{ content: "{de[0]}"', 1)
    css = css.replace('.dish-photo--katsu::after { content: "🍱"', f'.dish-photo--katsu::after {{ content: "{de[0]}"', 1)
    css = css.replace('.dish-photo--pari::after { content: "🥩"', f'.dish-photo--pari::after {{ content: "{de[1]}"', 1)
    css = css.replace('.dish-photo--mix::after { content: "🍤"', f'.dish-photo--mix::after {{ content: "{de[2]}"', 1)
    # 商品サムネ絵文字（2箇所）
    pe = s["css"]["product_emoji"]
    css = css.replace('.product-thumb:empty::after, .product-thumb[role]:not(:has(img))::after { content: "🍱"',
                      f'.product-thumb:empty::after, .product-thumb[role]:not(:has(img))::after {{ content: "{pe}"', 1)
    css = css.replace('.product-thumb:empty::after {\n  content: "🍱"', f'.product-thumb:empty::after {{\n  content: "{pe}"', 1)
    return css

# ---------- shop.js ----------
def build_shopjs(s):
    prods = ",\n".join(
        "  {\n" + f'    id: "{p["id"]}",\n    name: "{p["name"]}",\n    desc: "{p["desc"]}",\n    price: {p["price"]},\n    grad: "{p["grad"]}"' +
        (f',\n    note: "{p["note"]}"' if p.get("note") else "") + "\n  }"
        for p in s["products"])
    pay = ",\n  ".join(f'"{x}"' for x in s.get("payment", ["店頭受取／各種キャッシュレス"]))
    sh = s.get("shipping", {"standard":900,"remote":1300})
    return f'''/* =========================================================
   モックEC: 商品データ + カート（localStorage永続化）
   ※ 決済は一切発生しません。本番は決済代行のトークン方式で実装。
   商品・価格は「お取り寄せを導入する場合の構成例（目安）」です。
   ========================================================= */

const PRODUCTS = [
{prods}
];

/* 送料（地域別の目安）。デモ表示。 */
const SHIPPING = {{
  standard: {sh["standard"]},
  remote: {sh["remote"]}
}};

const PAYMENT_METHODS = [
  {pay}
];

const CART_KEY = "{s["cart_key"]}";
const yen = (n) => "¥" + n.toLocaleString("ja-JP");

const Cart = {{
  load() {{
    let c;
    try {{ c = JSON.parse(localStorage.getItem(CART_KEY)) || {{}}; }}
    catch {{ c = {{}}; }}
    let changed = false;
    for (const id of Object.keys(c)) {{
      const q = c[id];
      if (!PRODUCTS.some((p) => p.id === id) || !(q > 0)) {{ delete c[id]; changed = true; }}
    }}
    if (changed) this.save(c);
    return c;
  }},
  save(c) {{ localStorage.setItem(CART_KEY, JSON.stringify(c)); }},
  add(id) {{ const c = this.load(); c[id] = (c[id] || 0) + 1; this.save(c); return c; }},
  setQty(id, qty) {{ const c = this.load(); if (qty <= 0) delete c[id]; else c[id] = qty; this.save(c); return c; }},
  count() {{ return Object.values(this.load()).reduce((a, b) => a + b, 0); }},
  subtotal() {{
    const c = this.load();
    return Object.entries(c).reduce((sum, [id, q]) => {{
      const p = PRODUCTS.find((x) => x.id === id); return sum + (p ? p.price * q : 0);
    }}, 0);
  }},
  shipping() {{ return this.subtotal() > 0 ? SHIPPING.standard : 0; }},
  total() {{ return this.subtotal() + this.shipping(); }},
  clear() {{ localStorage.removeItem(CART_KEY); }}
}};
'''

# ---------- main.js ----------
def build_mainjs(s):
    mj = (TPL/"js"/"main.js").read_text(encoding="utf-8")
    nav = s["nav"]
    desc = s["desc"]
    block = f'''  const SITE = "{s["name"]}";
  const ROUTES = {{
    home:  "ホーム",
    menu:  "{nav["menu"]}",
    story: "{nav["story"]}",
    shop:  "{nav["shop"]}",
    order: "{nav["order"]}"
  }};
  const DESC = {{
    home:  "{desc["home"]}",
    menu:  "{desc["menu"]}",
    story: "{desc["story"]}",
    shop:  "{desc["shop"]}",
    order: "{desc["order"]}"
  }};
'''
    mj = re.sub(r'  const SITE = ".*?\n  const views = ', block + "  const views = ", mj, count=1, flags=re.S)
    mj = re.sub(r'cartItemsEl\.innerHTML = `<div class="cart-empty">.*?</div>`;',
                'cartItemsEl.innerHTML = `<div class="cart-empty"><p>カートは空です。<br>'
                + s["empty_cart"] + '</p><a class="btn btn-primary" href="#/order">'
                + s["nav"]["order"] + 'を見る</a></div>`;', mj, count=1, flags=re.S)
    mj = mj.replace("   ヨーロッパ軒 総本店 リニューアル（モック）", f"   {s['name']} リニューアル（モック）", 1)
    return mj

# ---------- index.html ----------
def stats_html(stats):
    out=[]
    for st in stats:
        sup = f"<span>{st['sup']}</span>" if st.get("sup") else ""
        out.append(f"            <div><dt>{st['dt']}</dt><dd>{st['dd']}{sup}</dd></div>")
    return "\n".join(out)

def quicknav_html(items):
    return "\n".join(
        f'          <a class="quicknav-card" href="{i["href"]}"><span class="qn-ico" aria-hidden="true">{i["ico"]}</span><span class="qn-t">{i["t"]}</span><span class="qn-d">{i["d"]}</span></a>'
        for i in items)

def signature_html(sig):
    cards=[]
    for it in sig["items"]:
        pill = f'<span class="pill">{it["pill"]}</span>' if it.get("pill") else ""
        feat = " dish-card--feature" if it.get("feature") else ""
        cards.append(f'''          <article class="dish-card{feat}">
            <div class="dish-photo dish-photo--{it["cls"]}" role="img" aria-label="{it["aria"]}"></div>
            <div class="dish-body">
              <div class="dish-head"><h3>{it["name"]}</h3>{pill}</div>
              <p>{it["desc"]}</p>
              <p class="dish-price">{it["price"]}<span>{it.get("price_note","税込・目安")}</span></p>
            </div>
          </article>''')
    return "\n".join(cards)

def menu_tables_html(cats):
    out=[]
    for c in cats:
        rows=[]
        for r in c["rows"]:
            cls=' class="menu-row-feature"' if r.get("feature") else ""
            rows.append(f'              <tr{cls}><td>{r["name"]}</td><td>{r["desc"]}</td><td>{r["price"]}</td></tr>')
        out.append(f'''        <h3 class="menu-cat">{c["cat"]}</h3>
        <div class="menu-table-wrap">
          <table class="menu-table">
            <thead><tr><th>品名</th><th>内容</th><th>価格</th></tr></thead>
            <tbody>
{chr(10).join(rows)}
            </tbody>
          </table>
        </div>''')
    return "\n".join(out)

def rules_html(rules):
    return "\n".join(f'          <div class="rule-card"><span class="rule-no">{r["no"]}</span><div><h3>{r["h"]}</h3><p>{r["p"]}</p></div></div>' for r in rules)

def guide_html(steps):
    return "\n".join(f'          <li><span class="guide-no">{i+1}</span><div><h3>{st["h"]}</h3><p>{st["p"]}</p></div></li>' for i,st in enumerate(steps))

def ecinfo_html(infos):
    return "\n".join(f'          <div class="ec-info"><h3>{x["h"]}</h3><p>{x["p"]}</p></div>' for x in infos)

def shopblocks_html(blocks):
    out=[]
    for b in blocks:
        cls=" ec-info--accent" if b.get("accent") else ""
        out.append(f'          <div class="ec-info{cls}"><h3>{b["h"]}</h3><p>{b["p"]}</p></div>')
    return "\n".join(out)

def jsonld(s):
    j=s["jsonld"]
    data={"@context":"https://schema.org","@type":"Restaurant","name":s["name"],
          "servesCuisine":j["cuisine"],"priceRange":j.get("price_range","¥¥"),
          **({"telephone":j["tel_intl"]} if j.get("tel_intl") else {}),
          "address":{"@type":"PostalAddress","streetAddress":j["street"],"addressLocality":j["locality"],
                     "addressRegion":j["region"],"postalCode":j["postal"],"addressCountry":"JP"}}
    if j.get("founding"): data["foundingDate"]=j["founding"]
    if j.get("hours"):
        data["openingHoursSpecification"]=[{"@type":"OpeningHoursSpecification","dayOfWeek":h["days"],"opens":h["opens"],"closes":h["closes"]} for h in j["hours"]]
    return json.dumps(data, ensure_ascii=False, indent=2)

def build_index(s):
    h=s["header"]; hero=s["hero"]; acc=s["access"]; mn=s["menu"]; story=s["story"]; order=s["order"]; nav=s["nav"]
    fav=f"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%23{s['fav_bg']}'/%3E%3Ctext x='32' y='44' font-size='28' text-anchor='middle' fill='%23{s['fav_fg']}' font-family='serif'%3E{s['fav_char']}%3C/text%3E%3C/svg%3E"
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{esc(s["title"])}</title>
<meta name="description" content="{esc(s["desc"]["home"])}" />
<meta name="theme-color" content="{s["theme_color"]}" />
<meta name="robots" content="noindex, nofollow" />
<meta name="format-detection" content="telephone=no" />

<link rel="icon" href="{fav}" />

<meta property="og:type" content="restaurant" />
<meta property="og:site_name" content="{esc(s["name"])}" />
<meta property="og:title" content="{esc(s["title"])}" />
<meta property="og:description" content="{esc(s["og_desc"])}" />
<meta property="og:locale" content="ja_JP" />

<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&family=Shippori+Mincho:wght@600;700;800&display=swap" rel="stylesheet" />

<link rel="stylesheet" href="css/style.css" />

<script type="application/ld+json">
{jsonld(s)}
</script>
</head>
<body>
<a class="skip-link" href="#main">本文へスキップ</a>
<div class="demo-ribbon" aria-hidden="true">提案デモ（モック）</div>
<p id="route-status" class="sr-only" aria-live="polite" role="status"></p>

<header class="site-header" id="top">
  <div class="header-info">
    <div class="container header-info-inner">
      <span class="hi-tel">TEL {(f'<a href="tel:'+h["tel_intl"]+'">'+h["tel_disp"]+'</a>') if h.get("tel_intl") else h["tel_disp"]}</span>
      <span>{h["hours"]}</span>
      <span>{h["closed"]}</span>
      <span>{h["addr"]}</span>
    </div>
  </div>
  <div class="container header-inner">
    <a class="brand" href="#/" aria-label="{esc(s["name"])} ホーム">
      <span class="brand-mark" aria-hidden="true">{s["mark"]}</span>
      <span class="brand-text">
        <span class="brand-sub">{s["brand_sub"]}</span>
        <span class="brand-name">{s["name"]}</span>
      </span>
    </a>
    <nav class="nav" aria-label="グローバルナビゲーション">
      <button class="nav-toggle" aria-expanded="false" aria-controls="nav-menu" aria-label="メニューを開く">
        <span></span><span></span><span></span>
      </button>
      <ul class="nav-menu" id="nav-menu">
        <li><a href="#/" data-route="home">ホーム</a></li>
        <li><a href="#/menu" data-route="menu">{nav["menu"]}</a></li>
        <li><a href="#/story" data-route="story">{nav["story"]}</a></li>
        <li><a href="#/shop" data-route="shop">{nav["shop"]}</a></li>
        <li><a href="#/order" data-route="order" class="nav-cta">{nav["order"]}</a></li>
      </ul>
    </nav>
    <button class="cart-button" id="cart-open" aria-label="カートを開く">
      <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>
      <span class="cart-count" id="cart-count" aria-live="polite" hidden>0</span>
    </button>
  </div>
</header>

<nav class="crumb-bar" id="crumb-bar" aria-label="パンくずリスト" hidden>
  <div class="container">
    <a href="#/">ホーム</a> <span class="crumb-sep" aria-hidden="true">/</span> <span id="crumb-current"></span>
  </div>
</nav>

<main id="main">
  <div class="view is-active" data-route="home">
    <section class="hero {hero["variant"]}">
      <div class="hero-media" role="img" aria-label="{hero["media_aria"]}"></div>
      <div class="hero-inner">
        <div class="hero-panel">
          <span class="badge badge--hero">{hero["badge"]}</span>
          <h1 class="hero-title" data-view-title>{hero["title_html"]}</h1>
          <p class="hero-lead">{hero["lead"]}</p>
          <div class="hero-actions">
            <a class="btn btn-primary" href="{hero["cta1"]["href"]}">{hero["cta1"]["label"]}</a>
            <a class="btn btn-outline" href="{hero["cta2"]["href"]}">{hero["cta2"]["label"]}</a>
          </div>
          <dl class="hero-stats">
{stats_html(hero["stats"])}
          </dl>
        </div>
      </div>
    </section>

    <section class="news-bar" aria-label="お知らせ">
      <div class="container news-bar-inner">
        <span class="news-date">営業案内</span>
        <p>{s["news"]}</p>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="quicknav">
{quicknav_html(s["quicknav"])}
        </div>
      </div>
    </section>

    <section class="section section--alt">
      <div class="container">
        <header class="section-head">
          <span class="badge">SIGNATURE</span>
          <h2 class="section-title">{s["signature"]["title"]}</h2>
          <p class="section-desc">{s["signature"]["desc"]}</p>
        </header>
        <div class="meibutsu-grid">
{signature_html(s["signature"])}
        </div>
        <p class="rank-note">{s["signature"]["rank_note"]}</p>
        <div class="center-cta"><a class="btn btn-primary" href="#/menu">{nav["menu"]}をすべて見る</a></div>
      </div>
    </section>

    <section class="section">
      <div class="container greeting-grid">
        <div class="greeting-photo" role="img" aria-label="{s["greeting"]["aria"]}"></div>
        <div>
          <header class="section-head section-head--left">
            <span class="badge">STORY</span>
            <h2 class="section-title">{s["greeting"]["title"]}</h2>
          </header>
          {"".join(f"<p>{p}</p>" for p in s["greeting"]["paras"])}
          <div class="center-cta center-cta--left"><a class="btn btn-outline btn-outline--dark" href="#/story">{s["greeting"]["cta_label"]}</a></div>
        </div>
      </div>
    </section>

    <section class="section section--alt">
      <div class="container">
        <header class="section-head">
          <span class="badge">ACCESS</span>
          <h2 class="section-title">{acc["title"]}</h2>
          <p class="section-desc">{acc["desc"]}</p>
        </header>
        <div class="shop-grid">
          <div class="shop-info card">
            <dl class="info-list">
              <div><dt>住所</dt><dd>{acc["addr_full"]}</dd></div>
              <div><dt>電話</dt><dd>{(f'<a href="tel:'+acc["tel_intl"]+'">'+acc["tel_disp"]+'</a>') if acc.get("tel_intl") else acc["tel_disp"]}</dd></div>
              <div><dt>営業時間</dt><dd>{acc["hours"]}</dd></div>
              <div><dt>定休日</dt><dd>{acc["closed"]}</dd></div>
              <div><dt>アクセス</dt><dd>{acc["access"]}</dd></div>
            </dl>
            <a class="btn btn-primary" href="https://www.google.com/maps/search/?api=1&query={acc["map_query"]}" target="_blank" rel="noopener">Googleマップで見る</a>
          </div>
          <div class="shop-map">
            <iframe class="googlemap" title="{esc(s["name"])} 地図" loading="lazy" allowfullscreen
              src="https://maps.google.com/maps?q={acc["map_src"]}&t=&z=16&ie=UTF8&iwloc=&output=embed"></iframe>
          </div>
        </div>
      </div>
    </section>
  </div>

  <div class="view" data-route="menu">
    <section class="section">
      <div class="container">
        <header class="section-head">
          <span class="badge">MENU</span>
          <h1 class="section-title" data-view-title>{nav["menu"]}</h1>
          <p class="section-desc">{mn["desc"]}</p>
        </header>
{menu_tables_html(mn["cats"])}
        <p class="menu-note">{mn["note"]}</p>
        <div class="rule-cards">
{rules_html(mn["rules"])}
        </div>
        <div class="center-cta"><a class="btn btn-outline btn-outline--dark" href="#/order">{mn["cta_label"]}</a></div>
      </div>
    </section>
  </div>

  <div class="view" data-route="story">
    <section class="section">
      <div class="container">
        <header class="section-head">
          <span class="badge">OUR STORY</span>
          <h1 class="section-title" data-view-title>{nav["story"]}</h1>
          <p class="section-desc">{story["desc"]}</p>
        </header>
        <ol class="guide-list">
{guide_html(story["steps"])}
        </ol>
        <p class="menu-note">{story["note"]}</p>
      </div>
    </section>
  </div>

  <div class="view" data-route="shop">
    <section class="section">
      <div class="container">
        <header class="section-head">
          <span class="badge">SHOP</span>
          <h1 class="section-title" data-view-title>{nav["shop"]}</h1>
          <p class="section-desc">{s["shop"]["desc"]}</p>
        </header>
        <div class="ec-info-grid">
{shopblocks_html(s["shop"]["blocks"])}
        </div>
        <div class="shop-grid" style="margin-top:2rem">
          <div class="shop-info card">
            <header class="section-head section-head--left">
              <span class="badge">ACCESS</span>
              <h2 class="section-title">地図</h2>
            </header>
            <p>{s["shop"]["access_desc"]}</p>
            <a class="btn btn-primary" href="https://www.google.com/maps/search/?api=1&query={acc["map_query"]}" target="_blank" rel="noopener">Googleマップで見る</a>
          </div>
          <div class="shop-map">
            <iframe class="googlemap" title="{esc(s["name"])} 地図" loading="lazy" allowfullscreen
              src="https://maps.google.com/maps?q={acc["map_src"]}&t=&z=16&ie=UTF8&iwloc=&output=embed"></iframe>
          </div>
        </div>
      </div>
    </section>
  </div>

  <div class="view" data-route="order">
    <section class="section">
      <div class="container">
        <header class="section-head">
          <span class="badge">{order["badge"]}</span>
          <h1 class="section-title" data-view-title>{nav["order"]}</h1>
          <p class="section-desc">
            {order["lead_html"]}<br />
            <strong>アカウント登録は不要です。ゲストのままご利用いただけます。</strong><br />
            <span class="ec-demo-note">※このECはデモ（モック）です。決済は行われません。</span>
          </p>
        </header>
        <div class="product-grid" id="product-grid" aria-live="polite"><!-- JSが商品を描画 --></div>
      </div>
    </section>

    <section class="section section--alt">
      <div class="container">
        <div class="ec-info-grid">
{ecinfo_html(order["infos"])}
        </div>
      </div>
    </section>
  </div>
</main>

<footer class="site-footer">
  <div class="container footer-inner">
    <div class="footer-brand">
      <span class="brand-mark" aria-hidden="true">{s["mark"]}</span>
      <div>
        <p class="footer-name">{s["name"]}</p>
        <p class="footer-addr">{s["footer_addr"]}</p>
      </div>
    </div>
    <nav class="footer-nav" aria-label="フッターナビ">
      <a href="#/menu">{nav["menu"]}</a>
      <a href="#/story">{nav["story"]}</a>
      <a href="#/shop">{nav["shop"]}</a>
      <a href="#/order">{nav["order"]}</a>
    </nav>
    <p class="footer-copy">© <span id="year"></span> {s["name"]}（リニューアル提案モック）</p>
  </div>
</footer>

<div class="cart-overlay" id="cart-overlay" hidden></div>
<aside class="cart-drawer" id="cart-drawer" role="dialog" aria-modal="true" aria-label="ショッピングカート" aria-hidden="true">
  <div class="cart-header">
    <h2>カート</h2>
    <button class="cart-close" id="cart-close" aria-label="カートを閉じる">✕</button>
  </div>
  <div class="cart-items" id="cart-items"></div>
  <div class="cart-footer">
    <div class="cart-line-row"><span>商品小計</span><span id="cart-subtotal">¥0</span></div>
    <div class="cart-line-row"><span>送料</span><span id="cart-shipping">¥0</span></div>
    <div class="cart-total"><span>合計</span><span id="cart-total">¥0</span></div>
    <p class="cart-guest-note">🛈 アカウント登録不要・ゲストのままご購入いただけます</p>
    <button class="btn btn-primary btn-block" id="checkout-open" disabled>レジに進む</button>
    <p class="cart-note">※デモのため決済は発生しません</p>
  </div>
</aside>

<div class="modal" id="checkout-modal" hidden>
  <div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="checkout-title">
    <button class="modal-close" id="checkout-close" aria-label="閉じる">✕</button>
    <h2 id="checkout-title">ご注文手続き（デモ）</h2>
    <fieldset class="acct-choice">
      <legend>ご購入方法</legend>
      <p class="acct-note">🛈 アカウント登録は不要です。ゲストのままご購入いただけます。</p>
      <label class="acct-opt"><input type="radio" name="acct" value="guest" checked /><span><strong>ゲストとして購入</strong>（登録不要・おすすめ）</span></label>
      <label class="acct-opt"><input type="radio" name="acct" value="create" /><span><strong>アカウントを作成して購入</strong>（任意）</span></label>
    </fieldset>
    <form id="checkout-form" novalidate>
      <label>お名前<input type="text" name="name" required autocomplete="name" /></label>
      <label>メールアドレス<input type="email" name="email" required autocomplete="email" /></label>
      <label>お届け先住所<input type="text" name="address" required autocomplete="street-address" /></label>
      <div class="acct-fields" id="acct-fields" hidden>
        <label>パスワード（アカウント作成用）<input type="password" name="password" autocomplete="new-password" minlength="8" placeholder="8文字以上" /></label>
        <p class="hint">作成すると、次回から購入履歴の確認やお届け先の保存ができます（デモ）。</p>
      </div>
      <fieldset class="card-fieldset">
        <legend>お支払い（ダミー）</legend>
        <p class="secure-note">🔒 本番は決済代行のトークン方式（カード非保持／PCI DSS準拠）で実装します。ここでは番号は送信・保存されません。</p>
        <label>カード番号<input type="text" inputmode="numeric" placeholder="4242 4242 4242 4242" autocomplete="off" /></label>
        <div class="card-row">
          <label>有効期限<input type="text" placeholder="MM/YY" /></label>
          <label>CVC<input type="text" placeholder="123" /></label>
        </div>
      </fieldset>
      <div class="checkout-summary">
        <div class="cart-line-row"><span>商品小計</span><span id="co-subtotal">¥0</span></div>
        <div class="cart-line-row"><span>送料</span><span id="co-shipping">¥0</span></div>
        <div class="cart-total"><span>お支払い合計</span><span id="co-total">¥0</span></div>
      </div>
      <button type="submit" class="btn btn-primary btn-block" id="checkout-submit">注文を確定する（デモ）</button>
    </form>
  </div>
</div>

<div class="toast" id="toast" role="status" aria-live="polite" hidden></div>
<button class="to-top" id="to-top" aria-label="ページの先頭へ戻る" hidden>↑</button>

<script src="js/shop.js"></script>
<script src="js/main.js"></script>
</body>
</html>
'''

def generate(s):
    d = SITES / s["slug"]
    (d/"css").mkdir(parents=True, exist_ok=True)
    (d/"js").mkdir(parents=True, exist_ok=True)
    (d/"css"/"style.css").write_text(build_css(s), encoding="utf-8")
    (d/"js"/"shop.js").write_text(build_shopjs(s), encoding="utf-8")
    (d/"js"/"main.js").write_text(build_mainjs(s), encoding="utf-8")
    (d/"index.html").write_text(build_index(s), encoding="utf-8")

def main():
    want=set(sys.argv[1:])
    n=0
    for s in CANDIDATES:
        if want and s["slug"] not in want: continue
        generate(s); n+=1; print("  generated", s["slug"])
    print(f"\n{n} sites generated.")

if __name__=="__main__":
    main()
