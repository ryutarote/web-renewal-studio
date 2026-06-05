/* =========================================================
   モックEC: 商品データ + カート（localStorage永続化）
   ※ 決済は一切発生しません。本番は決済代行のトークン方式で実装。
   商品・価格は公式通販の公開情報を基に再構成。
   - 確定: 特製カツ丼ソース＆極細パン粉 詰合せ（ソース4本・パン粉4袋）¥2,600（税込・送料別）
     賞味期限 ソース約6ヶ月／パン粉約10ヶ月。ゆうパック代引き発送。
   - それ以外の単品・進物は構成例（価格は「目安」）。
   ========================================================= */

const PRODUCTS = [
  {
    id: "sauce-panko-set",
    name: "特製カツ丼ソース＆極細パン粉 詰合せ",
    desc: "ソース4本＋極細パン粉4袋。ご家庭で“元祖”の味を再現する基本セット。豚肉をご用意いただくだけ。",
    price: 2600,
    grad: "radial-gradient(circle at 42% 32%, #b9763f, #6b3f1f 72%)",
    note: "公式通販の実セット（税込・送料別）"
  },
  {
    id: "sauce-2",
    name: "特製カツ丼ソース 2本",
    desc: "大正以来受け継ぐ特製ウスターソース。揚げたてのカツをくぐらせる、あの一杯のために。",
    price: 1300,
    grad: "radial-gradient(circle at 45% 35%, #a8632f, #5e3518 72%)"
  },
  {
    id: "panko-2",
    name: "極細カツ丼パン粉 2袋",
    desc: "薄づきの衣を生む、きめ細かな専用パン粉。ソースがよく絡み、軽い口当たりに。",
    price: 900,
    grad: "radial-gradient(circle at 45% 35%, #d6a86a, #946231 72%)"
  },
  {
    id: "gift-box",
    name: "進物用 詰合せ（化粧箱・のし対応）",
    desc: "ご贈答に。ソース＆パン粉の詰合せを化粧箱で。のし・包装を承ります。",
    price: 3400,
    grad: "linear-gradient(135deg, #6b3f1f, #b9763f)"
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

const CART_KEY = "yoroppaken_cart_v1";
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
