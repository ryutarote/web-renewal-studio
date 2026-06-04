/* =========================================================
   うどんバカ一代 リニューアル（モック）
   - ハッシュルーティングのSPA（クリックでビュー切替・リロードなし）
   - 商品描画 / カートDrawer / チェックアウト(モック)
   - ドロワー/モーダルはフォーカストラップ＋背面スクロール固定
   - 購入までアカウント登録は不要（ゲスト購入が既定。作成は任意）
   ========================================================= */
(function () {
  "use strict";

  const $ = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));
  const FOCUSABLE = 'a[href],button:not([disabled]),input:not([disabled]),select,textarea,[tabindex]:not([tabindex="-1"])';

  /* ---- 年号 ---- */
  $("#year").textContent = new Date().getFullYear();

  /* =========================================================
     SPA ルーター
     ========================================================= */
  const SITE = "手打十段 うどんバカ一代";
  const ROUTES = {
    home:    "ホーム",
    menu:    "お品書き",
    shop:    "店舗紹介・アクセス",
    craft:   "うどんができるまで",
    rule:    "バカイチのルール",
    recruit: "求人情報",
    ec:      "お土産うどん お取り寄せ"
  };
  const DESC = {
    home:    "香川県高松市の手打ち讃岐うどん「うどんバカ一代」。名物・釜バターうどん発祥の店。早朝6時から打ちたて・茹でたて。お土産うどんの通販も。",
    menu:    "うどんバカ一代のお品書き。釜バターうどん¥560〜、かけ・ぶっかけ・釜玉・肉うどん等を小・中・大の価格でご案内。サイドメニューも。",
    shop:    "うどんバカ一代の店舗紹介・アクセス。高松市多賀町、6:00〜18:00、年中無休（元旦のみ休み）、駐車場45台、瓦町駅徒歩7分。",
    craft:   "うどんバカ一代のうどんができるまで。専用の粉を使い、練り・熟成・手打ち・茹で・締めの工程で打ちたてを提供します。",
    rule:    "うどんバカ一代のセルフの流れ「バカイチのルール」。注文から会計、返却までのステップをご案内します。",
    recruit: "うどんバカ一代の求人情報。空調完備、平日時給1,200円〜・土日祝1,350円〜、ラスト手当、食事付き。アルバイト・社員募集。",
    ec:      "うどんバカ一代のお土産うどん通販。おみやげうどん・伝の助うどん・だし醤油。アカウント登録不要のゲスト購入OK（デモ）。"
  };
  const views = $$(".view");
  const navLinks = $$('.nav-menu a[data-route]');

  function routeFromHash() {
    const h = (location.hash || "").replace(/^#\/?/, "");
    return ROUTES[h] ? h : "home";
  }

  function showView(route) {
    views.forEach((v) => {
      const on = v.dataset.route === route;
      v.classList.toggle("is-active", on);
      v.hidden = !on;
    });
    navLinks.forEach((a) => {
      const on = a.dataset.route === route;
      a.classList.toggle("active", on);
      if (on) a.setAttribute("aria-current", "page");
      else a.removeAttribute("aria-current");
    });
    document.title = (route === "home" ? "" : ROUTES[route] + "｜") + SITE + "（リニューアル提案）";
    const status = $("#route-status");
    if (status) status.textContent = ROUTES[route] + " のページを表示しました";

    // メタディスクリプション（SEO/シェア）
    const metaDesc = $('meta[name="description"]');
    if (metaDesc && DESC[route]) metaDesc.setAttribute("content", DESC[route]);

    // パンくず
    const crumb = $("#crumb-bar");
    if (crumb) {
      if (route === "home") { crumb.hidden = true; }
      else { crumb.hidden = false; $("#crumb-current").textContent = ROUTES[route]; }
    }

    // 開いているUIを閉じる
    closeCart();
    closeModal();
    closeNav();

    // 先頭へ＋見出しへフォーカス（アクセシビリティ）
    window.scrollTo({ top: 0, behavior: "auto" });
    const active = views.find((v) => v.dataset.route === route);
    const title = active && active.querySelector("[data-view-title]");
    if (title) {
      title.setAttribute("tabindex", "-1");
      title.focus({ preventScroll: true });
    }
  }

  window.addEventListener("hashchange", () => showView(routeFromHash()));

  /* ---- モバイルナビ ---- */
  const navToggle = $(".nav-toggle");
  const navMenu = $("#nav-menu");
  function closeNav() {
    navMenu.classList.remove("open");
    navToggle.setAttribute("aria-expanded", "false");
    navToggle.setAttribute("aria-label", "メニューを開く");
  }
  navToggle.addEventListener("click", () => {
    const open = navMenu.classList.toggle("open");
    navToggle.setAttribute("aria-expanded", String(open));
    navToggle.setAttribute("aria-label", open ? "メニューを閉じる" : "メニューを開く");
    if (open) { const first = navMenu.querySelector("a"); if (first) first.focus(); }
  });
  // ルーター遷移時に閉じるので、リンククリック個別処理は不要

  /* =========================================================
     商品描画（EC）
     ========================================================= */
  const grid = $("#product-grid");
  grid.innerHTML = PRODUCTS.map((p) => `
    <article class="product-card">
      <div class="product-thumb"${p.img ? "" : ` style="background:${p.grad || "#e7ddcb"}"`} role="img" aria-label="${p.name}の商品画像">
        ${p.img ? `<img src="${p.img}" alt="${p.name}" loading="lazy" />` : ""}
      </div>
      <div class="product-body">
        <h3 class="product-name">${p.name}</h3>
        <p class="product-desc">${p.desc}</p>
        <div class="product-foot">
          <span class="product-price">${yen(p.price)}<span>税込</span></span>
          <button class="add-cart" data-id="${p.id}" aria-label="${p.name}をカートに追加">カートに入れる</button>
        </div>
      </div>
    </article>
  `).join("");

  /* =========================================================
     フォーカストラップ＋背面スクロール固定（共通）
     ========================================================= */
  let lastFocused = null;
  let releaseTrap = null;

  function lockScroll() { document.body.classList.add("no-scroll"); }
  function unlockScroll() {
    if (!$(".cart-drawer.open") && $("#checkout-modal").hidden) {
      document.body.classList.remove("no-scroll");
    }
  }
  function trapFocus(container) {
    function onKey(e) {
      if (e.key !== "Tab") return;
      const f = $$(FOCUSABLE, container).filter((el) => el.offsetParent !== null);
      if (!f.length) return;
      const first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
    container.addEventListener("keydown", onKey);
    return () => container.removeEventListener("keydown", onKey);
  }

  /* =========================================================
     カートDrawer
     ========================================================= */
  const drawer = $("#cart-drawer");
  const overlay = $("#cart-overlay");
  const cartCountEl = $("#cart-count");
  const cartItemsEl = $("#cart-items");
  const cartSubtotalEl = $("#cart-subtotal");
  const cartShippingEl = $("#cart-shipping");
  const cartTotalEl = $("#cart-total");
  const checkoutBtn = $("#checkout-open");

  function openCart() {
    renderCart();
    lastFocused = document.activeElement;
    drawer.classList.add("open");
    drawer.setAttribute("aria-hidden", "false");
    overlay.hidden = false;
    lockScroll();
    releaseTrap = trapFocus(drawer);
    $("#cart-close").focus();
  }
  function closeCart() {
    if (!drawer.classList.contains("open")) return;
    drawer.classList.remove("open");
    drawer.setAttribute("aria-hidden", "true");
    overlay.hidden = true;
    if (releaseTrap) { releaseTrap(); releaseTrap = null; }
    unlockScroll();
    if (lastFocused && document.contains(lastFocused)) lastFocused.focus();
  }

  function refreshCount() {
    const n = Cart.count();
    cartCountEl.textContent = n;
    checkoutBtn.disabled = n === 0;
  }

  function renderCart() {
    const c = Cart.load();
    const ids = Object.keys(c);
    if (ids.length === 0) {
      cartItemsEl.innerHTML = `<div class="cart-empty"><p>カートは空です。<br>お土産うどんはいかがですか？</p><a class="btn btn-primary" href="#/ec">お土産うどんを見る</a></div>`;
    } else {
      cartItemsEl.innerHTML = ids.map((id) => {
        const p = PRODUCTS.find((x) => x.id === id);
        if (!p) return "";
        const q = c[id];
        const thumbStyle = p.img
          ? `background-image:url('${p.img}');background-size:cover;background-position:center;`
          : `background:${p.grad || "#e7ddcb"};`;
        return `
          <div class="cart-line" data-id="${id}">
            <span class="thumb" style="${thumbStyle}"></span>
            <div>
              <div class="nm">${p.name}</div>
              <div class="pr">${yen(p.price)} × ${q} = ${yen(p.price * q)}</div>
              <div class="qty">
                <button class="q-dec" aria-label="数量を減らす">−</button>
                <span aria-live="polite">${q}</span>
                <button class="q-inc" aria-label="数量を増やす">＋</button>
                <button class="cart-remove" aria-label="削除">削除</button>
              </div>
            </div>
          </div>`;
      }).join("");
    }
    const sub = Cart.subtotal();
    const ship = Cart.shipping();
    cartSubtotalEl.textContent = yen(sub);
    cartShippingEl.textContent = ship > 0 ? yen(ship) : "—";
    cartTotalEl.textContent = yen(Cart.total());
    refreshCount();
  }

  grid.addEventListener("click", (e) => {
    const btn = e.target.closest(".add-cart");
    if (!btn) return;
    Cart.add(btn.dataset.id);
    refreshCount();
    toast("カートに追加しました");
    openCart();
  });

  cartItemsEl.addEventListener("click", (e) => {
    const line = e.target.closest(".cart-line");
    if (!line) return;
    const id = line.dataset.id;
    const cur = Cart.load()[id] || 0;
    if (e.target.classList.contains("q-inc")) Cart.setQty(id, cur + 1);
    else if (e.target.classList.contains("q-dec")) Cart.setQty(id, cur - 1);
    else if (e.target.classList.contains("cart-remove")) Cart.setQty(id, 0);
    else return;
    renderCart();
  });

  $("#cart-open").addEventListener("click", openCart);
  $("#cart-close").addEventListener("click", closeCart);
  overlay.addEventListener("click", closeCart);

  /* =========================================================
     チェックアウト(モック)
     ========================================================= */
  const modal = $("#checkout-modal");
  const form = $("#checkout-form");
  const acctFields = $("#acct-fields");
  const passwordInput = acctFields ? $("input[name=password]", acctFields) : null;
  const submitBtn = $("#checkout-submit");
  let modalReleaseTrap = null;
  let modalLastFocused = null;

  function syncCheckoutSummary() {
    $("#co-subtotal").textContent = yen(Cart.subtotal());
    const ship = Cart.shipping();
    $("#co-shipping").textContent = ship > 0 ? yen(ship) : "—";
    $("#co-total").textContent = yen(Cart.total());
  }

  function openModal() {
    syncCheckoutSummary();
    modalLastFocused = document.activeElement;
    // カートは閉じるが背面ロックは維持
    drawer.classList.remove("open");
    drawer.setAttribute("aria-hidden", "true");
    overlay.hidden = true;
    if (releaseTrap) { releaseTrap(); releaseTrap = null; }
    modal.hidden = false;
    lockScroll();
    modalReleaseTrap = trapFocus(modal);
    $("#checkout-close").focus();
  }
  function closeModal() {
    if (modal.hidden) return;
    modal.hidden = true;
    if (modalReleaseTrap) { modalReleaseTrap(); modalReleaseTrap = null; }
    unlockScroll();
    if (modalLastFocused && document.contains(modalLastFocused)) modalLastFocused.focus();
  }

  checkoutBtn.addEventListener("click", openModal);
  $("#checkout-close").addEventListener("click", closeModal);
  modal.addEventListener("click", (e) => { if (e.target === modal) closeModal(); });

  function applyAcctMode() {
    const mode = (form.querySelector("input[name=acct]:checked") || {}).value || "guest";
    const create = mode === "create";
    if (acctFields) acctFields.hidden = !create;
    if (passwordInput) passwordInput.required = create;
    if (submitBtn) submitBtn.textContent = create
      ? "アカウントを作成して注文（デモ）"
      : "ゲストとして注文を確定（デモ）";
  }
  $$("input[name=acct]", form).forEach((r) => r.addEventListener("change", applyAcctMode));
  applyAcctMode();

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    if (!form.checkValidity()) { form.reportValidity(); return; }
    const mode = (form.querySelector("input[name=acct]:checked") || {}).value || "guest";
    const total = Cart.total();
    Cart.clear();
    renderCart();
    closeModal();
    form.reset();
    applyAcctMode();
    const who = mode === "create" ? "アカウントを作成しました｜" : "ゲスト購入｜";
    toast(`${who}ご注文ありがとうございます（デモ）｜合計 ${yen(total)}`, 4500);
  });

  /* ---- Esc で各種クローズ ---- */
  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    if (!modal.hidden) closeModal();
    else if (drawer.classList.contains("open")) closeCart();
    else if (navMenu.classList.contains("open")) closeNav();
  });

  /* ---- トースト ---- */
  let toastTimer;
  function toast(msg, ms = 2200) {
    const el = $("#toast");
    el.textContent = msg;
    el.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { el.hidden = true; }, ms);
  }

  /* =========================================================
     YouTube ファサード（クリックで初めて読み込む＝初期表示を軽量化）
     ========================================================= */
  document.addEventListener("click", (e) => {
    const fac = e.target.closest(".video-facade");
    if (!fac) return;
    const id = fac.dataset.yt;
    if (!id) return;
    const iframe = document.createElement("iframe");
    iframe.src = "https://www.youtube-nocookie.com/embed/" + id + "?autoplay=1&rel=0";
    iframe.title = fac.getAttribute("aria-label") || "動画";
    iframe.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture";
    iframe.allowFullscreen = true;
    iframe.loading = "lazy";
    const wrap = document.createElement("div");
    wrap.className = "video";
    wrap.appendChild(iframe);
    fac.replaceWith(wrap);
    const f = iframe; setTimeout(() => f.focus && f.focus(), 0);
  });

  /* =========================================================
     画像フォールバック（外部CDN/プロキシ障害時も崩れにくく）
     ========================================================= */
  window.addEventListener("error", (e) => {
    const t = e.target;
    if (t && t.tagName === "IMG" && !t.dataset.fallback) {
      t.dataset.fallback = "1";
      t.classList.add("img-failed");
    }
  }, true);

  /* =========================================================
     ページ先頭へ戻るボタン
     ========================================================= */
  const toTop = $("#to-top");
  if (toTop) {
    let ticking = false;
    const onScroll = () => {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(() => {
        toTop.hidden = window.scrollY < 600;
        ticking = false;
      });
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    toTop.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: "smooth" });
      const t = document.querySelector(".view.is-active [data-view-title]");
      if (t) { t.setAttribute("tabindex", "-1"); t.focus({ preventScroll: true }); }
    });
  }

  /* ---- 初期化 ---- */
  refreshCount();
  showView(routeFromHash());
})();
