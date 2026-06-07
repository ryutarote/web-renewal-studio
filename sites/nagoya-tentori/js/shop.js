/* =========================================================
   モックEC: 商品データ + カート（localStorage永続化）
   ※ 決済は一切発生しません。本番は決済代行のトークン方式で実装。
   テイクアウト/通販の商品・価格は公開メニューを基にした構成（弁当は実価格、
   冷凍商品は「目安」）。実際の取り扱いは店舗にご確認ください。
   ========================================================= */

const PRODUCTS = [
  {
    id: "karaage-bento",
    name: "特製からあげ弁当",
    desc: "揚げたてのからあげをたっぷりのせた一番人気の弁当。ごはんとの相性も抜群。",
    price: 480,
    grad: "radial-gradient(circle at 42% 32%, #f0b53d, #6b4423 72%)",
    note: "店頭テイクアウトの定番"
  },
  {
    id: "shiromi-bento",
    name: "白身魚とからあげ弁当（タルタル付き）",
    desc: "サクサクの白身フライとからあげの欲ばり弁当。自家製タルタルを添えて。",
    price: 550,
    grad: "radial-gradient(circle at 45% 35%, #e6a93a, #5e3d1e 72%)"
  },
  {
    id: "aji-bento",
    name: "アジフライとからあげ弁当",
    desc: "肉厚のアジフライとからあげを一度に。食べごたえのある組み合わせ。",
    price: 550,
    grad: "radial-gradient(circle at 45% 35%, #d99a36, #4f3318 72%)"
  },
  {
    id: "frozen-karaage",
    name: "冷凍からあげ 500g（ご家庭用）",
    desc: "お店の味をご家庭で。温めるだけで揚げたての食感。お弁当やおつまみに（通販デモ）。",
    price: 1200,
    grad: "linear-gradient(135deg, #6b4423, #f0b53d)",
    note: "通販構成例（目安）"
  }
];

/* 送料（通販の地域別目安）。デモ表示。店頭テイクアウトは送料なし。 */
const SHIPPING = {
  standard: 800,
  remote: 1200
};

const PAYMENT_METHODS = [
  "店頭受取（現金・キャッシュレス）",
  "代金引換（通販・クール便代引き）"
];

const CART_KEY = "nagoya_tentori_cart_v1";
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
