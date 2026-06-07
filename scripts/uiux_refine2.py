#!/usr/bin/env python3
"""UI/UX 見送り項目の着手（第2弾）：全15サイト・冪等。

#3 地図iframeのプライバシー/パフォーマンス対応:
   ホーム・店舗の Google Maps iframe を「クリックで読み込むファサード」に変換（JSのみ）。
   → ページ表示時に第三者iframeを自動ロードしない（重複ロード解消・Cookie/通信を抑制）。
#6 チェックアウトのインラインエラー表示:
   ネイティブ reportValidity 依存を廃し、デザインに馴染むインラインエラー＋aria属性に。
いずれも index.html は編集せず、js/main.js と css/style.css への追記/最小編集で実装。
"""
import sys, pathlib

SITES = pathlib.Path(__file__).resolve().parent.parent / "sites"
CSS_MARK = "見送り項目 着手（地図ファサード / インラインエラー）"
JS_MARK = "__uiux2_appended"

CSS_BLOCK = """

/* =========================================================
   {mark}
   ========================================================= */
/* #3 地図ファサード（クリックでGoogleマップを読み込む） */
.map-facade {{
  width: 100%; height: 100%; min-height: 280px; border: 0; cursor: pointer;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: .45rem; font-family: inherit; color: #33475c;
  background:
    radial-gradient(120% 80% at 50% 0%, rgba(255,255,255,.6), transparent 60%),
    repeating-linear-gradient(45deg, #e9eef2 0 22px, #e3e9ee 22px 44px);
  transition: filter .15s ease;
}}
.map-facade:hover {{ filter: brightness(.97); }}
.map-facade svg {{ width: 40px; height: 40px; }}
.map-facade-label {{ font-weight: 700; font-size: 1rem; }}
.map-facade-sub {{ font-size: .74rem; opacity: .72; }}

/* #6 チェックアウト：インラインエラー */
.field-error {{
  display: block; color: #c0392b; font-size: .8rem; font-weight: 600;
  margin-top: .3rem; font-family: inherit;
}}
.field-error::before {{ content: "⚠ "; }}
#checkout-form input[aria-invalid="true"] {{
  border-color: #c0392b !important;
  box-shadow: 0 0 0 1px #c0392b !important;
}}
""".format(mark=CSS_MARK)

JS_BLOCK = r"""

/* ===== UI/UX 第2弾（見送り項目）: 地図ファサード / インラインエラー ===== */
/* __uiux2_appended */
(function () {
  "use strict";
  // ---- #3 Google Maps を「クリックで読み込む」ファサード化 ----
  var PIN = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
    + '<path fill="currentColor" d="M12 2a7 7 0 0 0-7 7c0 5 7 13 7 13s7-8 7-13a7 7 0 0 0-7-7Zm0 9.5A2.5 2.5 0 1 1 12 6a2.5 2.5 0 0 1 0 5.5Z"/></svg>';
  function facade(map) {
    var iframe = map.querySelector("iframe.googlemap");
    if (!iframe) return;
    var src = iframe.getAttribute("src");
    var title = iframe.getAttribute("title") || "地図";
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "map-facade";
    btn.setAttribute("aria-label", title + "を表示（Googleマップを読み込みます）");
    btn.innerHTML = PIN
      + '<span class="map-facade-label">地図を表示</span>'
      + '<span class="map-facade-sub">タップでGoogleマップを読み込みます</span>';
    iframe.remove();
    map.appendChild(btn);
    btn.addEventListener("click", function () {
      var f = document.createElement("iframe");
      f.className = "googlemap";
      f.title = title;
      f.loading = "lazy";
      f.setAttribute("allowfullscreen", "");
      f.setAttribute("referrerpolicy", "no-referrer-when-downgrade");
      f.src = src;
      btn.replaceWith(f);
    });
  }
  Array.prototype.forEach.call(document.querySelectorAll(".shop-map"), facade);

  // ---- #6 チェックアウト：インラインエラー ----
  var form = document.getElementById("checkout-form");
  if (form) {
    function errId(inp) { return "err-" + (inp.name || "f"); }
    function clearErr(inp) {
      inp.removeAttribute("aria-invalid");
      var e = document.getElementById(errId(inp));
      if (e) e.remove();
      inp.removeAttribute("aria-describedby");
    }
    function setErr(inp, msg) {
      inp.setAttribute("aria-invalid", "true");
      var id = errId(inp);
      var e = document.getElementById(id);
      if (!e) {
        e = document.createElement("span");
        e.className = "field-error";
        e.id = id;
        e.setAttribute("role", "alert");
        (inp.parentNode || inp).appendChild(e);
      }
      e.textContent = msg;
      inp.setAttribute("aria-describedby", id);
    }
    window.__checkoutValidate = function (f) {
      f = f || form;
      var inputs = Array.prototype.slice.call(
        f.querySelectorAll("input[required], input[name=password]"));
      var ok = true, firstBad = null;
      inputs.forEach(function (inp) {
        clearErr(inp);
        if (inp.name === "password" && !inp.required) return; // ゲスト時は対象外
        var v = (inp.value || "").trim(), msg = "";
        if (!v) msg = "入力してください。";
        else if (inp.type === "email" && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v))
          msg = "メールアドレスの形式をご確認ください。";
        else if (inp.name === "password" && v.length < 8)
          msg = "8文字以上で入力してください。";
        if (msg) { setErr(inp, msg); ok = false; if (!firstBad) firstBad = inp; }
      });
      if (firstBad) firstBad.focus();
      return ok;
    };
    // 入力時にエラーを解除
    form.addEventListener("input", function (e) {
      var t = e.target;
      if (t && t.matches("input")) clearErr(t);
    });
  }
})();
"""

errors = []

def edit_js(p: pathlib.Path):
    s = p.read_text(encoding="utf-8")
    o = s
    a = "    if (!form.checkValidity()) { form.reportValidity(); return; }"
    repl = ('    if (typeof window.__checkoutValidate === "function") '
            '{ if (!window.__checkoutValidate(form)) return; } '
            'else if (!form.checkValidity()) { form.reportValidity(); return; }')
    if a in s:
        s = s.replace(a, repl, 1)
    elif "__checkoutValidate" not in s:
        errors.append(f"{p}: validate行 不在")
    if JS_MARK not in s:
        s = s + JS_BLOCK
    if s != o:
        p.write_text(s, encoding="utf-8")
    return s != o

def edit_css(p: pathlib.Path):
    s = p.read_text(encoding="utf-8")
    if CSS_MARK in s:
        return False
    p.write_text(s + CSS_BLOCK, encoding="utf-8")
    return True

def main():
    dirs = sorted([d for d in SITES.iterdir() if d.is_dir() and (d/"index.html").exists()])
    print(f"対象サイト: {len(dirs)}")
    for d in dirs:
        c = edit_css(d/"css"/"style.css")
        j = edit_js(d/"js"/"main.js")
        print(f"  {d.name:22} css={int(c)} js={int(j)}")
    if errors:
        print("\n*** エラー ***")
        for e in errors: print("  -", e)
        sys.exit(1)
    print("\nOK: 全サイト適用完了")

if __name__ == "__main__":
    main()
