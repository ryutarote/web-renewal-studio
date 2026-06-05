/* =========================================================
   モックEC: 商品データ + カート（localStorage永続化）
   ※ 決済は一切発生しません。本番は決済代行のトークン方式で実装。
   商品・価格は明神水産オンラインショップの公開情報を基に再構成（価格は目安）。
   - 参考: 明神水産オンラインショップはヤマト運輸クール便で全国発送（冷凍・送料込みの商品あり）。
     支払いはクレジットカード／コンビニ／代金引換ほかに対応。
   - 価格は公式の価格帯（セット ¥3,996〜）を参考にした「目安」です。
   ========================================================= */

const PRODUCTS = [
  {
    id: "shio-tataki-set",
    name: "藁焼き鰹 塩たたきセット",
    desc: "“塩たたき”発祥の味をご家庭で。一本釣りの鰹を藁の炎で香ばしく焼き上げ、薬味と塩でいただく自慢の逸品。",
    price: 4980,
    grad: "radial-gradient(circle at 42% 32%, hsl(20 80% 55%), hsl(8 70% 30%) 72%)",
    note: "公式の人気カテゴリ。価格は目安（税込・送料込み相当）"
  },
  {
    id: "tare-tataki-2",
    name: "藁焼き鰹たたき（タレ付）2節",
    desc: "土佐沖の一本釣り鰹を藁焼きに。特製ポン酢ダレと薬味付きで、解凍してすぐお召し上がりいただけます。",
    price: 3996,
    grad: "radial-gradient(circle at 45% 35%, hsl(16 78% 52%), hsl(6 65% 28%) 72%)"
  },
  {
    id: "tabekurabe",
    name: "食べ比べセット（塩・タレ）",
    desc: "発祥の“塩たたき”と定番の“タレたたき”を一度に。藁焼きの香りと土佐の海の旨みを存分にどうぞ。",
    price: 5980,
    grad: "radial-gradient(circle at 45% 35%, hsl(24 80% 58%), hsl(10 65% 30%) 72%)"
  },
  {
    id: "gift-box",
    name: "進物用 詰合せ（化粧箱・のし対応）",
    desc: "お中元・お歳暮・ご贈答に。藁焼き鰹たたきの詰合せを化粧箱で。のし・包装を承ります。",
    price: 8640,
    grad: "linear-gradient(135deg, hsl(8 70% 30%), hsl(20 80% 55%))"
  }
];

/* 送料（公式は冷凍・送料込みの商品あり／クール便）。デモでは目安値を表示。 */
const SHIPPING = {
  standard: 0,
  remote: 600
};

const PAYMENT_METHODS = [
  "クレジットカード",
  "代金引換",
  "コンビニ決済",
  "銀行振込・郵便振込"
];

const CART_KEY = "kochi-myojinmaru_cart_v1";
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
