/* =========================================================
   モックEC: 商品データ + カート（localStorage永続化）
   ※ 決済は一切発生しません。本番は決済代行のトークン方式で実装。
   ※ 喜多方ラーメンは河京等の地元製麺所経由でも流通。本ECは
     「新規構築型リニューアル提案」のデモであり、価格は目安です。
   - 参考: 醤油ラーメン 生麺セットは地元通販で 4食 ¥1,000〜1,200 前後（目安）。
   - 単品・進物・詰合せは構成例（価格は「目安」）。
   ========================================================= */

const PRODUCTS = [
  {
    id: "ramen-shoyu-2",
    name: "喜多方ラーメン 生麺2食（醤油）",
    desc: "多加水熟成の平打ちちぢれ麺と、豚骨・煮干しのあっさり醤油スープ。まずは“元祖の味”をご家庭で2食から。",
    price: 760,
    grad: "radial-gradient(circle at 42% 32%, #c08a4a, #4f3417 72%)",
    note: "構成例（税込・送料別／目安）"
  },
  {
    id: "ramen-shoyu-4",
    name: "喜多方ラーメン 生麺4食（醤油）",
    desc: "看板の醤油ラーメンをたっぷり4食。家族で、贈り物の手前の“ためし買い”にも。スープ・調味料付き。",
    price: 1380,
    grad: "radial-gradient(circle at 45% 35%, #b97e3f, #463012 72%)"
  },
  {
    id: "chashu",
    name: "焼豚（チャーシュー）ブロック",
    desc: "醤油スープに合わせて炊いた自家製風の焼豚。薄切りでトッピングに、おつまみにも。約200g。",
    price: 980,
    grad: "radial-gradient(circle at 45% 35%, #a85d3a, #3e2412 72%)"
  },
  {
    id: "gift-box",
    name: "進物用 詰合せ（化粧箱・のし対応）",
    desc: "ご贈答に。醤油ラーメン生麺と焼豚の詰合せを化粧箱で。のし・包装を承ります。",
    price: 3200,
    grad: "linear-gradient(135deg, #4f3417, #c08a4a)"
  }
];

/* 送料（地域別・送料別／代引き）。デモでは目安値を表示。 */
const SHIPPING = {
  standard: 900,
  remote: 1300
};

const PAYMENT_METHODS = [
  "代金引換（ゆうパック代引き）"
];

const CART_KEY = "kitakata-genraiken_cart_v1";
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
