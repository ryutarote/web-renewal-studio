/* =========================================================
   モックEC: 商品データ + カート（localStorage永続化）
   ※ 決済は一切発生しません。本番は決済代行のトークン方式で実装。
   商品・価格は公式通販・公開情報を基に再構成（価格は税込・送料別の「目安」）。
   - 参考: 冷凍「味太助牛たん(塩味)」の通販あり（仙台駅お土産売り場ほか）。
     具体的な通販価格は公式に明示が乏しいため、本デモの価格はすべて「目安」です。
   ========================================================= */

const PRODUCTS = [
  {
    id: "tan-shio-2",
    name: "牛たん塩味 真空パック（2人前）",
    desc: "炭火焼の発祥店が受け継ぐ塩味。厚切りの牛たんを真空パックで。ご家庭のフライパン・網で香ばしく（価格は目安）。",
    price: 2600,
    grad: "radial-gradient(circle at 42% 32%, #c9603c, #3a302a 72%)",
    note: "通販価格は公式に明示が乏しく「目安」"
  },
  {
    id: "tan-shio-4",
    name: "牛たん塩味 真空パック（4人前）",
    desc: "ご家族・集まりに。発祥店の塩味をたっぷり4人前で。冷凍でお届け（価格は目安）。",
    price: 4800,
    grad: "radial-gradient(circle at 45% 35%, #b5532f, #332a25 72%)",
    note: "目安価格"
  },
  {
    id: "tail-soup",
    name: "テールスープ",
    desc: "じっくり炊いた牛テールの澄んだ滋味。牛たん焼と並ぶ初代考案の名物を、ご家庭で温めるだけ（価格は目安）。",
    price: 1200,
    grad: "radial-gradient(circle at 45% 35%, #cf7a44, #4a3a30 72%)",
    note: "目安価格"
  },
  {
    id: "gift-box",
    name: "進物用 詰合せ（化粧箱・のし対応）",
    desc: "ご贈答に。牛たん塩味とテールスープの詰合せを化粧箱で。のし・包装を承ります（価格は目安）。",
    price: 6500,
    grad: "linear-gradient(135deg, #3a302a, #c9603c)",
    note: "目安価格"
  }
];

/* 送料（公式は地域別・送料別／代引き想定）。デモでは目安値を表示。 */
const SHIPPING = {
  standard: 1000,
  remote: 1500
};

const PAYMENT_METHODS = [
  "代金引換（クール便代引き）"
];

const CART_KEY = "sendai-ajitasuke_cart_v1";
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
