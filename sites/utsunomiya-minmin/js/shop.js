/* =========================================================
   モックEC: 商品データ + カート（localStorage永続化）
   ※ 決済は一切発生しません。本番は決済代行のトークン方式で実装。
   商品・価格・送料は公式通販の公開情報を基に再構成（冷凍生餃子）。
   ========================================================= */

const PRODUCTS = [
  {
    id: "frozen-30",
    name: "冷凍生餃子 5人前（30個・タレ付）",
    desc: "野菜たっぷり、あっさり味。ご家庭で焼きたての一皿を。1個約20g。",
    price: 1350,
    grad: "radial-gradient(circle at 45% 35%, #f4d8b0, #d98b3a 70%)"
  },
  {
    id: "frozen-60",
    name: "冷凍生餃子 10人前（60個・タレ付）",
    desc: "家族や来客に。焼・水・揚、お好みの調理でどうぞ。",
    price: 2700,
    grad: "radial-gradient(circle at 45% 35%, #f0cda0, #c97b2e 72%)"
  },
  {
    id: "frozen-90",
    name: "冷凍生餃子 15人前（90個・タレ付）",
    desc: "まとめ買いに。冷凍ストックでいつでも宇都宮の味。",
    price: 4050,
    grad: "radial-gradient(circle at 45% 35%, #ecc795, #bf6f27 72%)"
  },
  {
    id: "gift-box",
    name: "進物用 化粧箱（のし対応）",
    desc: "ご贈答に。冷凍生餃子の詰め合わせ。のし・包装承ります。",
    price: 3000,
    grad: "linear-gradient(135deg, #9c1f1f, #c0392b)"
  }
];

/* 送料（公式通販の公開情報を基に再構成）
   全国一律 ¥1,000（沖縄を除く）。2人前〜のご注文。 */
const SHIPPING = {
  standard: 1000,
  remote: 1300
};

const PAYMENT_METHODS = [
  "代金引換",
  "郵便振替"
];

const CART_KEY = "minmin_cart_v1";
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
