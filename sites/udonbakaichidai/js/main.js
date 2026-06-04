/* =========================================================
   UI: ナビ開閉 / 商品描画 / カートDrawer / チェックアウト(モック)
   購入までアカウント登録は不要（ゲスト購入が既定。作成は任意）。
   ========================================================= */
(function () {
  "use strict";

  const $ = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));

  /* ---- 年号 ---- */
  $("#year").textContent = new Date().getFullYear();

  /* ---- モバイルナビ ---- */
  const navToggle = $(".nav-toggle");
  const navMenu = $("#nav-menu");
  navToggle.addEventListener("click", () => {
    const open = navMenu.classList.toggle("open");
    navToggle.setAttribute("aria-expanded", String(open));
    navToggle.setAttribute("aria-label", open ? "メニューを閉じる" : "メニューを開く");
  });
  navMenu.addEventListener("click", (e) => {
    if (e.target.tagName === "A") {
      navMenu.classList.remove("open");
      navToggle.setAttribute("aria-expanded", "false");
    }
  });

  /* ---- 商品描画 ---- */
  const grid = $("#product-grid");
  grid.innerHTML = PRODUCTS.map((p) => `
    <article class="product-card">
      <div class="product-thumb" style="background:${p.grad}" role="img" aria-label="${p.name}の商品画像"></div>
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

  /* ---- カートDrawer ---- */
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
    drawer.classList.add("open");
    drawer.setAttribute("aria-hidden", "false");
    overlay.hidden = false;
  }
  function closeCart() {
    drawer.classList.remove("open");
    drawer.setAttribute("aria-hidden", "true");
    overlay.hidden = true;
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
      cartItemsEl.innerHTML = `<p class="cart-empty">カートは空です。<br>お土産うどんはいかがですか？</p>`;
    } else {
      cartItemsEl.innerHTML = ids.map((id) => {
        const p = PRODUCTS.find((x) => x.id === id);
        if (!p) return "";
        const q = c[id];
        return `
          <div class="cart-line" data-id="${id}">
            <span class="thumb" style="background:${p.grad}"></span>
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

  /* 商品追加 */
  grid.addEventListener("click", (e) => {
    const btn = e.target.closest(".add-cart");
    if (!btn) return;
    Cart.add(btn.dataset.id);
    refreshCount();
    toast("カートに追加しました");
    openCart();
  });

  /* カート内操作 */
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

  /* ---- チェックアウト(モック) ---- */
  const modal = $("#checkout-modal");
  const form = $("#checkout-form");
  const acctFields = $("#acct-fields");
  const passwordInput = acctFields ? $("input[name=password]", acctFields) : null;
  const submitBtn = $("#checkout-submit");

  function syncCheckoutSummary() {
    $("#co-subtotal").textContent = yen(Cart.subtotal());
    const ship = Cart.shipping();
    $("#co-shipping").textContent = ship > 0 ? yen(ship) : "—";
    $("#co-total").textContent = yen(Cart.total());
  }

  function openModal() {
    syncCheckoutSummary();
    modal.hidden = false;
    closeCart();
  }
  const closeModal = () => { modal.hidden = true; };

  checkoutBtn.addEventListener("click", openModal);
  $("#checkout-close").addEventListener("click", closeModal);
  modal.addEventListener("click", (e) => { if (e.target === modal) closeModal(); });

  /* 購入方法の切替: ゲスト(登録不要・既定) / アカウント作成(任意) */
  function applyAcctMode() {
    const mode = (form.querySelector("input[name=acct]:checked") || {}).value || "guest";
    const create = mode === "create";
    if (acctFields) acctFields.hidden = !create;
    if (passwordInput) passwordInput.required = create; // 作成時のみパスワード必須
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

  /* 初期化 */
  refreshCount();
})();
