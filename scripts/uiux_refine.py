#!/usr/bin/env python3
"""UI/UX レビュー反映：全15サイトへ一括適用（冪等）。

適用内容:
  HTML: robots を noindex,nofollow / canonical(公式向き)を除去 / 提案デモのリボン追加
  CSS : 末尾に「UI/UX改修」上書きブロックを追記（絵文字撤去・プレースホルダ抑制・
        遷移短縮・タップ領域・現在地ナビの可視化・ghostボタンのコントラスト・デモ表示）
  JS  : モバイルナビの inert 化（A11y）/ カート追加時の自動展開を廃止（トーストのみ）
"""
import sys, pathlib, re

SITES = pathlib.Path(__file__).resolve().parent.parent / "sites"
MARK = "UI/UX 改修（レビュー反映・全サイト共通追記）"

CSS_BLOCK = """

/* =========================================================
   {mark}
   ========================================================= */
/* P0: ヒーローの絵文字を撤去し、クリーンなカラーバンドに */
.hero-media::after {{ content: "" !important; }}
.hero-media:empty {{ min-height: clamp(110px, 16vw, 170px); }}

/* P0: 空の料理/商品タイルは「写真準備中」の控えめなプレースホルダに
   （実写真タイル= --photo / <img>入りは :empty に該当しないため影響なし） */
.dish-photo:empty::after,
.product-thumb:empty::after {{
  opacity: .32 !important;
  filter: grayscale(.45) drop-shadow(0 2px 4px rgba(0,0,0,.12)) !important;
  font-size: clamp(1.9rem, 4vw, 2.5rem) !important;
}}
.dish-photo:empty, .product-thumb:empty {{ position: relative; }}
.dish-photo:empty::before,
.product-thumb:empty::before {{
  content: "写真は準備中です";
  position: absolute; left: 0; right: 0; bottom: .55rem;
  text-align: center; font-size: .66rem; letter-spacing: .06em;
  color: rgba(40,32,24,.5); pointer-events: none;
}}

/* P1: 画面遷移を短縮（回遊のテンポ優先） */
.view.is-active {{ animation-duration: .16s; }}

/* P1: タップ/クリックターゲット拡大（WCAG 2.5.5） */
.qty button {{ min-width: 40px; height: 40px; }}
.cart-remove {{ min-height: 40px; padding-inline: .5rem; }}

/* P1: 現在地ナビを色のみに依存させない（下線＋太字） */
.nav-menu a.active,
.nav-menu a[aria-current="page"] {{
  text-decoration: underline; text-underline-offset: 6px;
  text-decoration-thickness: 2px; font-weight: 700;
}}

/* P1: ヒーロー第2ボタン（ghost）の可読性確保 */
.btn-ghost {{ background: rgba(0,0,0,.5); }}
.btn-ghost:hover {{ background: rgba(0,0,0,.62); }}

/* P2: 提案デモであることを常時明示（誤認・誤クロール防止） */
.demo-ribbon {{
  position: fixed; left: 10px; bottom: 12px; z-index: 140;
  background: rgba(20,18,16,.82); color: #fff;
  font-size: .7rem; font-weight: 700; letter-spacing: .05em;
  padding: .3rem .65rem; border-radius: 999px;
  pointer-events: none; backdrop-filter: blur(4px);
}}
@media (max-width: 560px) {{ .demo-ribbon {{ font-size: .6rem; left: 8px; bottom: 8px; }} }}
@media (prefers-reduced-motion: reduce) {{ .view.is-active {{ animation-duration: .001s; }} }}
""".format(mark=MARK)

errors = []

def edit_html(p: pathlib.Path):
    s = p.read_text(encoding="utf-8")
    o = s
    # H1: robots
    s = s.replace('<meta name="robots" content="index, follow" />',
                  '<meta name="robots" content="noindex, nofollow" />')
    # H2: canonical(公式URL向き)を1行除去
    s = re.sub(r'\n[ \t]*<link rel="canonical"[^>]*>\s*(?=\n)', '\n', s, count=1)
    # H3: 提案デモのリボン（冪等）
    if 'class="demo-ribbon"' not in s:
        anchor = '<a class="skip-link" href="#main">本文へスキップ</a>'
        if anchor not in s:
            errors.append(f"{p}: skip-link anchor 不在");
        else:
            s = s.replace(anchor, anchor +
                '\n<div class="demo-ribbon" aria-hidden="true">提案デモ（モック）</div>')
    if 'content="noindex' not in s:
        errors.append(f"{p}: robots 置換失敗")
    if s != o:
        p.write_text(s, encoding="utf-8")
    return s != o

def edit_css(p: pathlib.Path):
    s = p.read_text(encoding="utf-8")
    if MARK in s:
        return False
    p.write_text(s + CSS_BLOCK, encoding="utf-8")
    return True

def edit_js(p: pathlib.Path):
    s = p.read_text(encoding="utf-8")
    o = s
    # J1a: NAV_MQ 定義（navMenu 定義直後・冪等）
    if "NAV_MQ" not in s:
        a = 'const navMenu = $("#nav-menu");'
        if a in s:
            s = s.replace(a, a +
                '\n  const NAV_MQ = window.matchMedia("(max-width: 1024px)");'
                '\n  NAV_MQ.addEventListener("change", (e) => { navMenu.inert = e.matches && !navMenu.classList.contains("open"); });',
                1)
        else:
            errors.append(f"{p}: navMenu 定義 不在")
    # J1b: closeNav で inert（モバイル幅のみ）
    if "navMenu.inert = NAV_MQ.matches;" not in s:
        a = '    navMenu.classList.remove("open");'
        if a in s:
            s = s.replace(a, a + '\n    navMenu.inert = NAV_MQ.matches;', 1)
        else:
            errors.append(f"{p}: closeNav anchor 不在")
    # J1c: トグル open 時に inert 解除
    if "navMenu.inert = !open;" not in s:
        a = '    navToggle.setAttribute("aria-expanded", String(open));'
        if a in s:
            s = s.replace(a, a + '\n    navMenu.inert = !open;', 1)
        else:
            errors.append(f"{p}: nav-toggle anchor 不在")
    # J2: カート追加で自動展開しない（トーストのみ・文言改善）
    a = '    toast("カートに追加しました");\n    openCart();'
    if a in s:
        s = s.replace(a,
            '    toast("カートに追加しました（右上のカートからご確認いただけます）");', 1)
    elif 'カートに追加しました（右上の' not in s:
        errors.append(f"{p}: cart-add anchor 不在")
    if s != o:
        p.write_text(s, encoding="utf-8")
    return s != o

def main():
    dirs = sorted([d for d in SITES.iterdir() if d.is_dir() and (d/"index.html").exists()])
    print(f"対象サイト: {len(dirs)}")
    for d in dirs:
        h = edit_html(d/"index.html")
        c = edit_css(d/"css"/"style.css")
        j = edit_js(d/"js"/"main.js")
        print(f"  {d.name:22} html={int(h)} css={int(c)} js={int(j)}")
    if errors:
        print("\n*** エラー ***")
        for e in errors: print("  -", e)
        sys.exit(1)
    print("\nOK: 全サイト適用完了")

if __name__ == "__main__":
    main()
