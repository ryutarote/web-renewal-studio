/* =========================================================
   モックEC: 商品データ + カート（localStorage永続化）
   ※ 決済は一切発生しません。本番は決済代行のトークン方式で実装。
   商品・価格は「お取り寄せを導入する場合の構成例（目安）」です。
   ========================================================= */

const PRODUCTS = [
  {
    id: "kabayaki",
    name: "うなぎ蒲焼（真空・1尾）",
    desc: "秘伝のたれで焼いた蒲焼。温めてうな丼・うな重に。",
    price: 3800,
    grad: "radial-gradient(circle at 42% 32%, #d8a83a, #2a1d12 72%)",
    note: "構成例（目安）"
  },
  {
    id: "kizami",
    name: "きざみうなぎ",
    desc: "きざんだ蒲焼。ひつまぶしや混ぜごはんに。",
    price: 2200,
    grad: "radial-gradient(circle at 45% 35%, #b58a2f, #241810 72%)"
  },
  {
    id: "tare",
    name: "うなぎのたれ",
    desc: "秘伝のたれ。焼き魚や卵かけごはんにも。",
    price: 700,
    grad: "linear-gradient(135deg, #2a1d12, #d8a83a)"
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

const CART_KEY = "tokyo_nodaiwa_cart_v1";
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
