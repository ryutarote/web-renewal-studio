/* =========================================================
   モックEC: 商品データ + カート（localStorage永続化）
   ※ 決済は一切発生しません。本番は決済代行のトークン方式で実装。
   商品・価格は「お取り寄せを導入する場合の構成例（目安）」です。
   ========================================================= */

const PRODUCTS = [
  {
    id: "saga-chanpon",
    name: "ちゃんぽん（通販・2食）",
    desc: "もちもち麺と豚骨スープのセット。野菜をたっぷり加えてご家庭で。",
    price: 1500,
    grad: "radial-gradient(circle at 42% 32%, #e0a83a, #3a2216 72%)",
    note: "構成例（目安）"
  },
  {
    id: "chanpon-soup",
    name: "ちゃんぽんスープ",
    desc: "豚骨ベースのまろやかスープ。野菜炒めにも。",
    price: 700,
    grad: "radial-gradient(circle at 45% 35%, #c4882f, #2a1810 72%)"
  },
  {
    id: "chanpon-set",
    name: "ちゃんぽんセット（4食）",
    desc: "たっぷりのちゃんぽんセット。お集まりやお取り寄せに。",
    price: 2800,
    grad: "linear-gradient(135deg, #3a2216, #e0a83a)"
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

const CART_KEY = "takeo_idechanpon_cart_v1";
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
