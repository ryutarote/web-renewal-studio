/* =========================================================
   モックEC: 商品データ + カート（localStorage永続化）
   ※ 決済は一切発生しません。本番は決済代行のトークン方式で実装。
   商品・価格は公式通販の公開情報を基に再構成。
   - 参考: 公式通販「元祖もつ鍋」セット（牛もつ300g・女将特製スープ120ml・
     ちゃんぽん2玉・にんにく・赤唐辛子を含む）。【小】2〜3人前 ¥3,155 ほか。
   - 価格・内容は公開情報を基にした「目安」。最新は公式サイトをご確認ください。
   ========================================================= */

const PRODUCTS = [
  {
    id: "motsunabe-set-s",
    name: "元祖もつ鍋セット【小】（2〜3人前）",
    desc: "牛もつ300g・女将特製スープ・ちゃんぽん2玉・にんにく・赤唐辛子。ご家庭で“元祖”の味を再現する基本セット。",
    price: 3155,
    grad: "radial-gradient(circle at 42% 32%, #3f8a52, #1f4a2c 72%)",
    note: "公式通販の参考セット（税込・送料別）"
  },
  {
    id: "motsunabe-set-m",
    name: "元祖もつ鍋セット【中】（3〜4人前）",
    desc: "牛もつ300g×2・スープ×2・ちゃんぽん2玉×2。家族や少人数のお集まりにちょうどよい中容量。",
    price: 6380,
    grad: "radial-gradient(circle at 45% 35%, #4a9a5e, #245634 72%)"
  },
  {
    id: "motsu-add",
    name: "追加 生もつ（300g）",
    desc: "大将厳選の新鮮な生もつ。もっと食べたい方へ、もつだけを追加で。ぷりぷりの食感をたっぷりと。",
    price: 880,
    grad: "radial-gradient(circle at 45% 35%, #c0492f, #7a2a1c 72%)"
  },
  {
    id: "champon-shime",
    name: "ちゃんぽん玉・〆セット（2玉）",
    desc: "もつの旨味が溶け出したスープに。博多もつ鍋の王道の〆、ちゃんぽん玉のセット。",
    price: 600,
    grad: "linear-gradient(135deg, #1f4a2c, #4a9a5e)"
  }
];

/* 送料（公式は地域別・クール便／送料別）。デモでは目安値を表示。 */
const SHIPPING = {
  standard: 1000,
  remote: 1500
};

const PAYMENT_METHODS = [
  "クレジットカード",
  "代金引換"
];

const CART_KEY = "hakata-rakutenchi_cart_v1";
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
