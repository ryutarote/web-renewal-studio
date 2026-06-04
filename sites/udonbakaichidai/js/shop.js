/* =========================================================
   モックEC: 商品データ + カート（localStorage永続化）
   ※ 決済は一切発生しません。本番は決済代行のトークン方式で実装。
   商品ラインナップ・価格・画像・送料は公式通販(category/1, category/5)の公開情報。
   画像は http 配信のため images.weserv.nl 経由で https 化して表示。
   ========================================================= */

const IMG = (path) => "https://images.weserv.nl/?url=www.udonbakaichidai.co.jp/images/material/" + path;

const PRODUCTS = [
  {
    id: "omiyage-udon",
    name: "手打十段うどんバカ一代の『おみやげうどん』",
    desc: "店の味をご自宅で。手打十段の讃岐うどんおみやげ用。",
    price: 1500,
    img: IMG("udon01.jpg")
  },
  {
    id: "dennosuke-4",
    name: "『伝の助うどん』4人前（つゆ付）ゆでタイプ ★米粉入り",
    desc: "ゆでタイプで手軽に本格讃岐うどん。つゆ付き・米粉入り。",
    price: 1500,
    img: IMG("dennosuke01.jpg")
  },
  {
    id: "dennosuke-2",
    name: "『伝の助うどん』2人前（つゆ付）ゆでタイプ ★米粉入り",
    desc: "まずはお試しに。ゆでタイプ・つゆ付き・米粉入りの2人前。",
    price: 800,
    img: IMG("dennosuke06.jpg")
  },
  {
    id: "dashi-shoyu",
    name: "釜バターうどん用『だし醤油』",
    desc: "名物・釜バターうどんの味を決める特製だし醤油。",
    price: 400,
    img: IMG("P1010012.jpg")
  }
];

/* 送料（公式通販の公開情報）
   全国一律 ¥1,000／北海道・東北・沖縄は ¥1,300（すべて税込） */
const SHIPPING = {
  standard: 1000,
  remote: 1300
};

/* 利用可能な支払い方法（公式の表記） */
const PAYMENT_METHODS = [
  "代金引換",
  "銀行振込",
  "郵便振替",
  "クレジットカード決済",
  "オンラインコンビニ決済",
  "ネットバンク決済",
  "電子マネー決済"
];

const CART_KEY = "udon_cart_v2";
const yen = (n) => "¥" + n.toLocaleString("ja-JP");

const Cart = {
  load() {
    let c;
    try { c = JSON.parse(localStorage.getItem(CART_KEY)) || {}; }
    catch { c = {}; }
    // 旧バージョン等で存在しない商品IDが残っていたら除去（空カートで件数が出る不具合の防止）
    let changed = false;
    for (const id of Object.keys(c)) {
      const q = c[id];
      if (!PRODUCTS.some((p) => p.id === id) || !(q > 0)) { delete c[id]; changed = true; }
    }
    if (changed) this.save(c);
    return c;
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
