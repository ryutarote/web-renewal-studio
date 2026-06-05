/* =========================================================
   モックEC: 商品データ + カート（localStorage永続化）
   ※ 決済は一切発生しません。本番は決済代行のトークン方式で実装。
   商品・価格は公式通販（izumosoba-haneya.com）の公開情報を基に再構成。
   - 参考: 半生そば（つゆ付・6人前）¥3,900 / 乾そば（つゆ付・6人前）¥2,650
     お試しセット ¥1,850 等を公式が販売。下記は構成例で価格は「目安」。
   - 半生・冷凍生そばは要冷蔵/冷凍便、進物は化粧箱・のし対応。
   ========================================================= */

const PRODUCTS = [
  {
    id: "namahan-4",
    name: "出雲そば 半生（4人前・つゆ付）",
    desc: "石臼挽きの本格出雲そば。半生仕立てだから家庭でも打ち立てに近いコシと香り。特製つゆ付き。",
    price: 2600,
    grad: "radial-gradient(circle at 42% 32%, #8a9a5b, #3d4a2a 72%)",
    note: "公式通販の構成を基にした目安価格（税込・送料別）"
  },
  {
    id: "namahan-2",
    name: "出雲そば 半生（2人前・つゆ付）",
    desc: "まずは試したい方へ。挽きたての風味を閉じ込めた半生そばを2人前で。つゆ付き。",
    price: 1450,
    grad: "radial-gradient(circle at 45% 35%, #9aa766, #44512d 72%)"
  },
  {
    id: "kamaage-nama",
    name: "釜揚げそば用 生そば（3人前）",
    desc: "そば湯ごといただく釜揚げに最適な生そば。とろりと濃厚なそば湯と香りをご家庭で。",
    price: 1300,
    grad: "radial-gradient(circle at 45% 35%, #b0bd7d, #5a6838 72%)"
  },
  {
    id: "gift-box",
    name: "進物用 化粧箱（のし対応）",
    desc: "ご贈答に。出雲そばの詰合せを化粧箱で。のし・包装を承ります。献上の伝統を贈り物に。",
    price: 3900,
    grad: "linear-gradient(135deg, #3d4a2a, #8a9a5b)"
  }
];

/* 送料（公式は地域別・送料別／代引き）。デモでは目安値を表示。 */
const SHIPPING = {
  standard: 900,
  remote: 1300
};

const PAYMENT_METHODS = [
  "代金引換（ゆうパック代引き）"
];

const CART_KEY = "izumo-haneya_cart_v1";
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
