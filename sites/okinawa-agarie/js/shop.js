/* =========================================================
   モックEC: 商品データ + カート（localStorage永続化）
   ※ 決済は一切発生しません。本番は決済代行のトークン方式で実装。
   商品・価格は公式通販（agariesoba.com）の公開情報を基に再構成。
   - 確定: 東江そば 4人前セット（自家製生麺・出汁付）¥5,420（送料無料）
   - 確定: 東江そば(2人前)＆冷やしそば(2人前) ¥5,260（送料無料）
   - ソーキ／三枚肉セット・進物は構成例（価格は「目安」）。
   ========================================================= */

const PRODUCTS = [
  {
    id: "agarie-set-4",
    name: "東江そば 4人前セット（自家製生麺・出汁付）",
    desc: "麺職人が打つもちもちの自家製生麺と、昆布・鰹節の一番だしを4人前で。ご家庭で店の味を。",
    price: 5420,
    grad: "radial-gradient(circle at 42% 32%, #3a9aa3, #1d5d63 72%)",
    note: "公式通販の実セット（送料無料）"
  },
  {
    id: "soki-set-2",
    name: "ソーキそばセット（2食・出汁付）",
    desc: "やわらかく煮込んだ本ソーキ付き。看板のソーキそばをご家庭で味わえる2食セット。",
    price: 3200,
    grad: "radial-gradient(circle at 45% 35%, #4aa8a0, #235a52 72%)"
  },
  {
    id: "sanmainiku-set-2",
    name: "三枚肉そばセット（2食・出汁付）",
    desc: "甘辛く炊いた豚バラ三枚肉付き。定番の三枚肉そばを生麺・一番だしで。2食セット。",
    price: 3000,
    grad: "radial-gradient(circle at 45% 35%, #d6a86a, #946231 72%)"
  },
  {
    id: "gift-box",
    name: "進物用 詰合せ（化粧箱・のし対応）",
    desc: "ご贈答に。自家製生麺と出汁・具材の詰合せを化粧箱で。のし・包装を承ります。",
    price: 6000,
    grad: "linear-gradient(135deg, #1d5d63, #3a9aa3)"
  }
];

/* 送料（公式はセット商品が送料無料）。デモでは離島等の目安値を表示。 */
const SHIPPING = {
  standard: 0,
  remote: 800
};

const PAYMENT_METHODS = [
  "クレジットカード",
  "代金引換"
];

const CART_KEY = "okinawa-agarie_cart_v1";
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
