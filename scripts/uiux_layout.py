#!/usr/bin/env python3
"""#4 ヒーローのレイアウト多様化 / #2 バナー導線のコンテンツ化。冪等。

#4: 全サイト同型(中央寄せ)を解消。ヒーローに3バリエーション（中央=既定 / minimal=左寄せ
    テキスト先行 / split=PCで左テキスト＋右カラーパネル）を用意し、店ごとに割当て。
    実写真ヒーロー(udon/morioka/nagasaki)は既定のまま維持。
#2: ナビと重複する導線バナー(banners--text: 4サイト)を「タイトル＋説明」のコンテンツ
    カードへ。絵文字を撤去し情報価値を付与。
"""
import sys, re, pathlib

SITES = pathlib.Path(__file__).resolve().parent.parent / "sites"
CSS_MARK = "ヒーロー・レイアウトのバリエーション / バナーのコンテンツ化"

HERO_VARIANT = {
    # minimal
    "fukui-yoroppaken":"hero--minimal","izumo-haneya":"hero--minimal",
    "kochi-myojinmaru":"hero--minimal","okinawa-agarie":"hero--minimal",
    "sapporo-ajinosanpei":"hero--minimal","nagoya-houraiken":"hero--minimal",
    # split
    "hakata-rakutenchi":"hero--split","hiroshima-mitchan":"hero--split",
    "kitakata-genraiken":"hero--split","osaka-daruma":"hero--split",
    "sendai-ajitasuke":"hero--split","utsunomiya-minmin":"hero--split",
    # default(photo heroes): udonbakaichidai, morioka-jajamen, nagasaki-shikairou
}

BANNERS = {
  "utsunomiya-minmin":[("#/menu","お品書き","名物の三種と価格"),("#/gyoza","餃子のこだわり","白菜たっぷり・あっさり"),
                       ("#/shop","店舗・アクセス","宇都宮市内の各店"),("#/order","お取り寄せ","冷凍生餃子をご家庭で")],
  "hiroshima-mitchan":[("#/menu","お品書き","名物と鉄板メニュー"),("#/story","みっちゃんの歴史","広島お好み焼の元祖"),
                       ("#/shop","店舗・アクセス","八丁堀本店のご案内"),("#/order","お取り寄せ","冷凍お好み焼をご家庭で")],
  "morioka-jajamen":[("#/menu","お品書き","じゃじゃ麺と一品"),("#/story","じゃじゃ麺とは","食べ方とちーたんたん"),
                     ("#/shop","店舗・アクセス","本店・分店のご案内"),("#/order","お取り寄せ","ご家庭でじゃじゃ麺を")],
  "nagasaki-shikairou":[("#/menu","お品書き","ちゃんぽん・皿うどん"),("#/story","ちゃんぽん物語","発祥の地・四海樓"),
                        ("#/shop","店舗・アクセス","松が枝町のご案内"),("#/order","お取り寄せ","ご家庭で味わう")],
}

CSS_BLOCK = """

/* =========================================================
   {mark}
   ========================================================= */
/* #4 minimal: ヒーロー帯を省きテキスト先行・左寄せ */
.hero--minimal .hero-media {{ display: none; }}
.hero--minimal .hero-inner {{ justify-content: flex-start; padding-block: clamp(2.6rem, 7vw, 5rem); }}
.hero--minimal .hero-panel {{ text-align: left; margin-inline: 0; max-width: 46rem; }}
.hero--minimal .hero-lead {{ margin-inline: 0; }}
.hero--minimal .hero-actions {{ justify-content: flex-start; }}
.hero--minimal .hero-title {{ font-size: clamp(2.1rem, 5.2vw, 3.8rem); }}

/* #4 split: PCで左テキスト＋右カラーパネル */
@media (min-width: 860px) {{
  .hero.hero--split {{ display: grid; grid-template-columns: 1.05fr .95fr; align-items: stretch; }}
  .hero.hero--split .hero-inner {{ order: 1; align-items: center; }}
  .hero.hero--split .hero-panel {{ text-align: left; margin-inline: 0; }}
  .hero.hero--split .hero-lead {{ margin-inline: 0; }}
  .hero.hero--split .hero-actions {{ justify-content: flex-start; }}
  .hero.hero--split .hero-media {{ order: 2; min-height: 100%; height: auto;
     border-bottom: 0; border-left: 4px solid hsl(var(--accent)); }}
  .hero.hero--split .hero-media:empty {{ min-height: 100%; }}
}}

/* #2 バナー導線をコンテンツ化（タイトル＋説明・絵文字なし） */
.banners--text .banner-card {{ align-items: flex-start; text-align: left;
   justify-content: center; gap: .28rem; padding: 1.1rem 1.15rem; }}
.banner-card .banner-title {{ font-weight: 700; font-size: 1.02rem; line-height: 1.3; }}
.banner-card .banner-sub {{ font-weight: 400; font-size: .78rem; line-height: 1.4;
   color: hsl(var(--muted-foreground)); }}
""".format(mark=CSS_MARK)

errors=[]

def banner_html(slug):
    rows = "".join(
        f'\n          <a class="banner-card" href="{h}">'
        f'<span class="banner-title">{t}</span>'
        f'<span class="banner-sub">{s}</span></a>'
        for (h,t,s) in BANNERS[slug])
    return f'<div class="banners banners--text">{rows}\n        </div>'

def process(d: pathlib.Path):
    slug = d.name
    # CSS append
    css = d/"css"/"style.css"
    cs = css.read_text(encoding="utf-8")
    if CSS_MARK not in cs:
        css.write_text(cs + CSS_BLOCK, encoding="utf-8")
    # HTML: hero variant + banner
    html = d/"index.html"
    s = html.read_text(encoding="utf-8"); o = s
    if slug in HERO_VARIANT:
        a = '<section class="hero">'
        repl = f'<section class="hero {HERO_VARIANT[slug]}">'
        if a in s: s = s.replace(a, repl, 1)
        elif HERO_VARIANT[slug] not in s: errors.append(f"{slug}: hero anchor 不在")
    if slug in BANNERS and 'banner-title' not in s:
        s2 = re.sub(r'<div class="banners banners--text">.*?</div>', banner_html(slug), s, count=1, flags=re.S)
        if s2 == s: errors.append(f"{slug}: banner block 不在")
        s = s2
    if s != o: html.write_text(s, encoding="utf-8")
    return True

def main():
    dirs = sorted([d for d in SITES.iterdir() if d.is_dir() and (d/"index.html").exists()])
    for d in dirs:
        process(d)
        v = HERO_VARIANT.get(d.name, "default")
        b = "banner✓" if d.name in BANNERS else "-"
        print(f"  {d.name:22} hero={v:14} {b}")
    if errors:
        print("\n*** エラー ***");
        for e in errors: print("  -", e)
        sys.exit(1)
    print("\nOK")

if __name__ == "__main__":
    main()
