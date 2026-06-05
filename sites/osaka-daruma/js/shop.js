/* =========================================================
   モックEC: 商品データ + カート（localStorage永続化）
   ※ 決済は一切発生しません。本番は決済代行のトークン方式で実装。
   商品・価格は公式通販（BASE）の公開情報を基に再構成。
   - 確定: 「だるまのどて焼きレトルト10個セット」が公式通販で販売（送料無料）。
     「カレーレトルト10個セット」（串かつソースカレー＋牛すじ味噌煮込みカレー）も販売。
   - 価格・容量は時期により変動するため、本デモでは「目安」値を表示。
     単品ソース・進物詰合せは構成例（価格は「目安」）。
   ========================================================= */

const PRODUCTS = [
  {
    id: "dote-retort-10",
    name: "名物どて牛すじ煮込み レトルト 10個セット",
    desc: "新世界の名物どて焼きをご家庭で。やわらかく煮込んだ牛すじを甘辛味噌だれで。温めるだけのレトルト10個入り。",
    price: 6480,
    grad: "radial-gradient(circle at 42% 32%, #c2622f, #7a2f1c 72%)",
    note: "公式通販（BASE）で販売／送料無料（目安）"
  },
  {
    id: "curry-retort-10",
    name: "だるまカレー レトルト 10個セット",
    desc: "串かつソースカレー5個＋牛すじ味噌煮込みカレー5個の詰合せ。だるまの味を手軽に楽しめる人気セット。",
    price: 6480,
    grad: "radial-gradient(circle at 45% 35%, #c98a2f, #8a4f1c 72%)"
  },
  {
    id: "sauce-2",
    name: "だるま秘伝ソース 2本",
    desc: "サクッと揚げた串かつにくぐらせる、創業以来の秘伝ソース。甘みと旨みのバランスが大阪の味。",
    price: 1480,
    grad: "radial-gradient(circle at 45% 35%, #b53a2f, #6e1f17 72%)"
  },
  {
    id: "gift-box",
    name: "進物用 詰合せ（化粧箱・のし対応）",
    desc: "ご贈答に。どて焼き・カレー・秘伝ソースの詰合せを化粧箱で。のし・包装を承ります。",
    price: 7800,
    grad: "linear-gradient(135deg, #7a2f1c, #c2622f)"
  }
];

/* 送料（公式はセットにより送料無料あり／地域別）。デモでは目安値を表示。 */
const SHIPPING = {
  standard: 800,
  remote: 1200
};

const PAYMENT_METHODS = [
  "クレジットカード",
  "代金引換"
];

const CART_KEY = "osaka-daruma_cart_v1";
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
