/* =========================================================
   モックEC: 商品データ + カート（localStorage永続化）
   ※ 決済は一切発生しません。本番は決済代行のトークン方式で実装。
   ※ 本ECは「リニューアル提案デモ」です。実際の「味の三平」監修
     味噌ラーメンセットは、サッポロ西山ラーメン等が通販で取り扱って
     います（自社通販ではありません）。価格はすべて「目安」です。
   ========================================================= */

const PRODUCTS = [
  {
    id: "miso-4set-special",
    name: "味噌ラーメン 4食セット（specialつき）",
    desc: "発祥の味噌ラーメンを4食。中太ちぢれの専用麺と味噌だれに、特製トッピングを添えた基本セット。",
    price: 2400,
    grad: "radial-gradient(circle at 42% 32%, #c98a3f, #6b4a26 72%)",
    note: "監修セット（価格は目安・税込）"
  },
  {
    id: "miso-2",
    name: "味噌ラーメン 2食",
    desc: "まずは試したい方へ。炒め野菜と味噌のコクを、ご家庭で手軽に再現できる2食入り。",
    price: 1300,
    grad: "radial-gradient(circle at 45% 35%, #b97a33, #5e3f1f 72%)"
  },
  {
    id: "shoyu-shio-2",
    name: "醤油・塩 食べ比べ 2食",
    desc: "キレのある正油と、すっきりとした塩。味噌の前から愛された二つの味を一度に楽しめます。",
    price: 1300,
    grad: "radial-gradient(circle at 45% 35%, #d6a86a, #8a6231 72%)"
  },
  {
    id: "gift-box",
    name: "進物用 詰合せ（化粧箱・のし対応）",
    desc: "ご贈答に。味噌を中心に味の三平監修の味わいを詰め合わせた化粧箱。のし・包装を承ります。",
    price: 3600,
    grad: "linear-gradient(135deg, #6b4a26, #c98a3f)"
  }
];

/* 送料（地域別・送料別）。デモでは目安値を表示。 */
const SHIPPING = {
  standard: 900,
  remote: 1300
};

const PAYMENT_METHODS = [
  "クレジットカード",
  "代金引換"
];

const CART_KEY = "sapporo-ajinosanpei_cart_v1";
const yen = (n) => "¥" + n.toLocaleString("ja-JP");

const Cart = {
  load() {
    let c;
    try { c = JSON.parse(localStorage.getItem(CART_KEY)) || {}; }
    catch { c = {}; }
    let changed = false;
    for (const id of Object.keys(c)) {
      const q = c[id];
      if (!PRODUCTS.some((p) => p.id === id) || !(q > 0)) { delete c[id]; changed = true; }
    }
    if (changed) this.save(c);
    return c;
  },
  save(c) { localStorage.setItem(CART_KEY, JSON.stringify(c)); },
  add(id) { const c = this.load(); c[id] = (c[id] || 0) + 1; this.save(c); return c; },
  setQty(id, qty) { const c = this.load(); if (qty <= 0) delete c[id]; else c[id] = qty; this.save(c); return c; },
  count() { return Object.values(this.load()).reduce((a, b) => a + b, 0); },
  subtotal() {
    const c = this.load();
    return Object.entries(c).reduce((sum, [id, q]) => {
      const p = PRODUCTS.find((x) => x.id === id); return sum + (p ? p.price * q : 0);
    }, 0);
  },
  shipping() { return this.subtotal() > 0 ? SHIPPING.standard : 0; },
  total() { return this.subtotal() + this.shipping(); },
  clear() { localStorage.removeItem(CART_KEY); }
};
