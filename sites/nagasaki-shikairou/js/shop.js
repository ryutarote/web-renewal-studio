/* モックEC: 商品データ + カート（localStorage）。デモ（リニューアル提案）。
   四海樓は公式の自社通販を持たず、現状はAmazon等の外部・店頭1F売店での販売。
   下記は「もし自社ECを設けたら」という提案デモ。価格は参考の目安。
   料理写真はちゃんぽん/皿うどんの公式画像を images.weserv.nl 経由でhttps配信。 */
const IMG = (u) => "https://images.weserv.nl/?url=" + encodeURIComponent(u) + "&w=640&h=480&fit=cover&output=webp";
const PRODUCTS = [
  { id:"champon-2", name:"長崎ちゃんぽん 2食（スープ付）", desc:"発祥の味をご家庭で。具だくさんの一杯。", price:1200, img:IMG("shikairou.com/wp-content/uploads/2025/02/ime_c01-scaled.jpg"), grad:"linear-gradient(135deg,#cfe6f0,#2b6e8f)" },
  { id:"sara-2",    name:"皿うどん 2食（あんかけ付）", desc:"パリッと細麺に、とろみあんをたっぷり。", price:1200, img:IMG("shikairou.com/wp-content/uploads/2025/02/ime_s01-scaled.jpg"), grad:"linear-gradient(135deg,#e8d49a,#b9851a)" },
  { id:"set-4",     name:"ちゃんぽん・皿うどん 食べ比べ 4食", desc:"長崎の二大名物をひと箱で。", price:2300, grad:"linear-gradient(135deg,#2b6e8f,#123c52)" },
  { id:"gift",      name:"進物用 化粧箱（のし対応）", desc:"ご贈答に。詰め合わせギフト。", price:3500, grad:"linear-gradient(135deg,#1f5673,#0e2a3a)" }
];
const SHIPPING={standard:1000,remote:1300};
const PAYMENT_METHODS=["クレジットカード","代金引換","銀行振込"];
const CART_KEY="shikairou_cart_v2";
const yen=(n)=>"¥"+n.toLocaleString("ja-JP");
const Cart={load(){let c;try{c=JSON.parse(localStorage.getItem(CART_KEY))||{};}catch{c={};}let ch=false;for(const id of Object.keys(c)){const q=c[id];if(!PRODUCTS.some(p=>p.id===id)||!(q>0)){delete c[id];ch=true;}}if(ch)this.save(c);return c;},save(c){localStorage.setItem(CART_KEY,JSON.stringify(c));},add(id){const c=this.load();c[id]=(c[id]||0)+1;this.save(c);return c;},setQty(id,q){const c=this.load();if(q<=0)delete c[id];else c[id]=q;this.save(c);return c;},count(){return Object.values(this.load()).reduce((a,b)=>a+b,0);},subtotal(){const c=this.load();return Object.entries(c).reduce((s,[id,q])=>{const p=PRODUCTS.find(x=>x.id===id);return s+(p?p.price*q:0);},0);},shipping(){return this.subtotal()>0?SHIPPING.standard:0;},total(){return this.subtotal()+this.shipping();},clear(){localStorage.removeItem(CART_KEY);}};
