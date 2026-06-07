/* =========================================================
   モックEC: 商品データ + カート（localStorage永続化）
   ※ 決済は一切発生しません。本番は決済代行のトークン方式で実装。
   商品・価格は「お取り寄せを導入する場合の構成例（目安）」です。
   ========================================================= */

const PRODUCTS = [
  {
    id: "retort-curry",
    name: "名物カレー（レトルト）",
    desc: "混ぜて食べる名物カレーをご家庭で。生卵を落としてどうぞ。",
    price: 650,
    grad: "radial-gradient(circle at 42% 32%, #e0b04a, #4a2f1a 72%)",
    note: "構成例（目安）"
  },
  {
    id: "curry-3set",
    name: "名物カレー 3食詰合せ",
    desc: "レトルト名物カレーの詰合せ。常備やギフトに。",
    price: 1800,
    grad: "radial-gradient(circle at 45% 35%, #c88a3a, #3a2414 72%)"
  },
  {
    id: "haishi",
    name: "ハイシソース（レトルト）",
    desc: "コク深いハイシをごはんに。手軽に洋食気分。",
    price: 700,
    grad: "linear-gradient(135deg, #4a2f1a, #e0b04a)"
  }
];

/* 送料（地域別の目安）。デモ表示。 */
const SHIPPING = {
  standard: 900,
  remote: 1300
};

const PAYMENT_METHODS = [
  "店頭受取／各種キャッシュレス",
  "代金引換（通販・クール便代引き）"
];

const CART_KEY = "osaka_jiyuken_cart_v1";
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
