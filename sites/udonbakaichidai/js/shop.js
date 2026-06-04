/* =========================================================
   モックEC: 商品データ + カート（localStorage永続化）
   ※ 決済は一切発生しません。本番は決済代行のトークン方式で実装。
   商品ラインナップ・送料・支払い方法は公式通販の公開情報を基に再構成。
   ========================================================= */

const PRODUCTS = [
  {
    id: "den-no-suke-4",
    name: "伝の助うどん 4人前（つゆ付）",
    desc: "店の味をそのまま。ゆでタイプ（米粉入り）で、手軽に打ちたての食感を。",
    price: 1080,
    grad: "linear-gradient(135deg,#f0dca5,#d9b15f)"
  },
  {
    id: "kama-butter-set",
    name: "釜バターうどんセット 2人前",
    desc: "名物・釜バターうどんをご自宅で。特製バター・胡椒・出汁醤油付き。",
    price: 1680,
    grad: "radial-gradient(circle at 40% 35%,#f6d97a,#e0a526 65%,#b9851a)"
  },
  {
    id: "kama-butter-3",
    name: "釜バターうどん 3食組",
    desc: "麺300g×1・つゆ・バターオイル・胡椒入り。まず試したい方に。",
    price: 880,
    grad: "radial-gradient(circle at 45% 40%,#f3d27a,#d99f29 70%,#a9760f)"
  },
  {
    id: "hannama-6",
    name: "半生讃岐うどん 6人前（つゆ付）",
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
    name: "贈答用 化粧箱 8人前（のし対応）",
    desc: "ご贈答に。讃岐うどん詰め合わせのギフトボックス。のし・包装承ります。",
    price: 3200,
    grad: "linear-gradient(135deg,#1a3a5c,#2f5e8c)"
  }
];

/* 送料（公式通販の公開情報を基に再構成）
   全国一律 ¥1,000／北海道・東北・沖縄は ¥1,300 */
const SHIPPING = {
  standard: 1000,
  remote: 1300,
  freeOver: null // 送料無料ラインは設けない
};

/* 利用可能な支払い方法（表示用・デモ） */
const PAYMENT_METHODS = [
  "代金引換",
  "銀行振込",
  "郵便振替",
  "クレジットカード",
  "コンビニ決済",
  "ネットバンク決済",
  "電子マネー決済"
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
  subtotal() {
    const c = this.load();
    return Object.entries(c).reduce((sum, [id, q]) => {
      const p = PRODUCTS.find((x) => x.id === id);
      return sum + (p ? p.price * q : 0);
    }, 0);
  },
  shipping() {
    return this.subtotal() > 0 ? SHIPPING.standard : 0;
  },
  total() {
    return this.subtotal() + this.shipping();
  },
  clear() { localStorage.removeItem(CART_KEY); }
};
