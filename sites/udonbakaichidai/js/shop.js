/* =========================================================
   モックEC: 商品データ + カート（localStorage永続化）
   ※ 決済は一切発生しません。本番は決済代行のトークン方式で実装。
   ========================================================= */

const PRODUCTS = [
  {
    id: "den-no-suke-4",
    name: "伝の助うどん 4人前（つゆ付）",
    desc: "店の味をそのまま。ゆでタイプで手軽に本格讃岐うどん。",
    price: 1080,
    grad: "linear-gradient(135deg,#f0dca5,#d9b15f)"
  },
  {
    id: "kama-butter-set",
    name: "釜バターうどんセット 2人前",
    desc: "名物・釜バターうどんをご自宅で。特製出汁醤油・バター付き。",
    price: 1680,
    grad: "radial-gradient(circle at 40% 35%,#f6d97a,#e0a526 65%,#b9851a)"
  },
  {
    id: "hannama-6",
    name: "半生讃岐うどん 6人前",
    desc: "コシと小麦の香りが長持ちする半生タイプ。常温保存OK。",
    price: 1500,
    grad: "linear-gradient(135deg,#e7d6ac,#c7a45c)"
  },
  {
    id: "kijoyu-set",
    name: "生醤油うどんセット 3人前",
    desc: "麺の旨みを楽しむ生醤油。すだち果汁を添えて。",
    price: 1400,
    grad: "linear-gradient(135deg,#dccba0,#b89a5f)"
  },
  {
    id: "gift-8",
    name: "贈答用 化粧箱 8人前",
    desc: "のし対応。讃岐うどん詰め合わせのギフトボックス。",
    price: 3200,
    grad: "linear-gradient(135deg,#1a3a5c,#2f5e8c)"
  },
  {
    id: "taiken-kit",
    name: "手打ち体験キット",
    desc: "ご家庭で打ちたて体験。小麦粉・レシピ・麺棒ガイド付き。",
    price: 2200,
    grad: "linear-gradient(135deg,#d9b8a0,#b3373a)"
  }
];

const CART_KEY = "udon_cart_v1";
const yen = (n) => "¥" + n.toLocaleString("ja-JP");

const Cart = {
  load() {
    try { return JSON.parse(localStorage.getItem(CART_KEY)) || {}; }
    catch { return {}; }
  },
  save(c) { localStorage.setItem(CART_KEY, JSON.stringify(c)); },
  add(id) {
    const c = this.load();
    c[id] = (c[id] || 0) + 1;
    this.save(c);
    return c;
  },
  setQty(id, qty) {
    const c = this.load();
    if (qty <= 0) delete c[id]; else c[id] = qty;
    this.save(c);
    return c;
  },
  count() {
    return Object.values(this.load()).reduce((a, b) => a + b, 0);
  },
  total() {
    const c = this.load();
    return Object.entries(c).reduce((sum, [id, q]) => {
      const p = PRODUCTS.find((x) => x.id === id);
      return sum + (p ? p.price * q : 0);
    }, 0);
  },
  clear() { localStorage.removeItem(CART_KEY); }
};
