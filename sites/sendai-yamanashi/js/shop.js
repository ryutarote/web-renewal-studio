/* =========================================================
   モックEC: 商品データ + カート（localStorage永続化）
   ※ 決済は一切発生しません。本番は決済代行のトークン方式で実装。
   商品・価格は構成例（「目安」）。実際の通販条件は店舗にご確認ください。
   ========================================================= */

const PRODUCTS = [
  {
    id: "tan-set",
    name: "厚切り牛たん 詰合せ（塩・味噌漬け＋テールスープ）",
    desc: "名物の厚切りたん（塩・味噌漬け）に、コトコト炊いたテールスープを添えた基本セット。ご家庭で炭火の余韻を。",
    price: 4800,
    grad: "radial-gradient(circle at 42% 32%, #c4642f, #3a241c 72%)",
    note: "構成例（目安・税込／送料別）"
  },
  {
    id: "tan-shio",
    name: "厚切り牛たん 塩味 300g",
    desc: "粗めの塩で下味をつけた厚切りたん。さっと炙って、レモンや七味でシンプルに。",
    price: 2300,
    grad: "radial-gradient(circle at 45% 35%, #b65a2c, #2f1f18 72%)"
  },
  {
    id: "tan-miso",
    name: "厚切り牛たん 味噌漬け 300g",
    desc: "仙台味噌の風味をまとわせた味噌漬け。麦めしが進む、コク深い一枚。",
    price: 2400,
    grad: "radial-gradient(circle at 45% 35%, #a9692f, #34241a 72%)"
  },
  {
    id: "tail-soup",
    name: "テールスープ 2食",
    desc: "牛テールをじっくり炊き出した澄んだスープ。たん焼きの相棒に。湯せん・レンジで手軽に。",
    price: 1000,
    grad: "linear-gradient(135deg, #6b4423, #c4843f)"
  }
];

/* 送料（地域別の目安）。デモ表示。 */
const SHIPPING = {
  standard: 900,
  remote: 1300
};

const PAYMENT_METHODS = [
  "代金引換（クール便代引き）"
];

const CART_KEY = "sendai_yamanashi_cart_v1";
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
