/* =========================================================
   モックEC: 商品データ + カート（localStorage永続化）
   ※ 決済は一切発生しません。本番は決済代行のトークン方式で実装。
   商品・価格は公式オンラインショップの公開情報を基に再構成。
   - 公式オンラインショップ（houraikenonlineshop.com）で冷凍ひつまぶし・うなぎ蒲焼等を販売。
   - 価格はすべて「目安」（公開情報を基にした参考値）。最新は公式でご確認ください。
   - 「ひつまぶし」はあつた蓬莱軒の登録商標です。
   ========================================================= */

const PRODUCTS = [
  {
    id: "hitsumabushi-1",
    name: "冷凍ひつまぶし（1人前）",
    desc: "発祥の地の味をご家庭で。きざんだ鰻の蒲焼とご飯のセット。①そのまま②薬味③出汁④お好みで、の四つの食べ方をお楽しみください。",
    price: 4200,
    grad: "radial-gradient(circle at 42% 32%, #c47a3a, #5a2f22 72%)",
    note: "価格は目安（公開情報を基にした参考値）"
  },
  {
    id: "unagi-kabayaki",
    name: "うなぎ蒲焼（長焼 1尾）",
    desc: "備長炭で香ばしく焼き上げた蒲焼を、創業以来のたれとともに。うな丼・うな重にも。温めるだけでお召し上がりいただけます。",
    price: 3800,
    grad: "radial-gradient(circle at 45% 35%, #b0682f, #4e2a1d 72%)"
  },
  {
    id: "hitsumabushi-set-2",
    name: "ひつまぶしセット（2人前・出汁/薬味付）",
    desc: "ひつまぶし2人前に、特製出汁とねぎ・わさび・きざみ海苔の薬味付き。四つの食べ方を一式でそろえた、ご家族向けセット。",
    price: 8800,
    grad: "radial-gradient(circle at 45% 35%, #d09a55, #7a4a28 72%)"
  },
  {
    id: "gift-box",
    name: "進物用 化粧箱（のし対応）",
    desc: "ご贈答に。ひつまぶし・うなぎ蒲焼の詰合せを化粧箱で。のし・包装を承ります。大切な方への贈り物に。",
    price: 11000,
    grad: "linear-gradient(135deg, #5a2f22, #c47a3a)"
  }
];

/* 送料（地域別・送料別／クール便）。デモでは目安値を表示。 */
const SHIPPING = {
  standard: 1100,
  remote: 1600
};

const PAYMENT_METHODS = [
  "クレジットカード決済（オンライン）",
  "代金引換（クール宅急便代引き）"
];

const CART_KEY = "nagoya-houraiken_cart_v1";
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
