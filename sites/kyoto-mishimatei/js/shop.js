/* =========================================================
   モックEC: 商品データ + カート（localStorage永続化）
   ※ 決済は一切発生しません。本番は決済代行のトークン方式で実装。
   商品・価格は「お取り寄せを導入する場合の構成例（目安）」です。
   ========================================================= */

const PRODUCTS = [
  {
    id: "sukiyaki-set-m",
    name: "黒毛和牛すき焼きセット（約3人前）",
    desc: "霜降りの黒毛和牛と割下のセット。家庭でハレのすき焼きを。",
    price: 10800,
    grad: "radial-gradient(circle at 42% 32%, #c98a4a, #3e1820 72%)",
    note: "構成例（目安）"
  },
  {
    id: "gyu-tsukudani",
    name: "牛肉佃煮",
    desc: "和牛を甘辛く炊いた佃煮。ごはんのお供や進物に。",
    price: 2200,
    grad: "radial-gradient(circle at 45% 35%, #8a3040, #2e1018 72%)"
  },
  {
    id: "warishita-m",
    name: "三嶋亭仕立て 割下",
    desc: "すき焼きのための割下。和牛の旨みを引き立てます。",
    price: 1200,
    grad: "linear-gradient(135deg, #3e1820, #c98a4a)"
  }
];

/* 送料（地域別の目安）。デモ表示。 */
const SHIPPING = {
  standard: 1000,
  remote: 1400
};

const PAYMENT_METHODS = [
  "店頭受取／各種キャッシュレス",
  "代金引換（通販・クール便代引き）"
];

const CART_KEY = "kyoto_mishimatei_cart_v1";
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
