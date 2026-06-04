/* モックEC: 商品データ + カート（localStorage）。デモ。価格は参考の目安。 */
const PRODUCTS = [
  { id:"soba-2", name:"冷凍お好み焼き そば肉玉（2枚・ソース付）", desc:"元祖の味をご家庭で。麺はそば入り、温めるだけ。", price:2000, grad:"linear-gradient(135deg,#e8a05a,#c75b1e)" },
  { id:"udon-2", name:"冷凍お好み焼き うどん肉玉（2枚・ソース付）", desc:"もっちり食感のうどん入り。お子様にも人気。", price:2000, grad:"linear-gradient(135deg,#e6b06a,#b3471f)" },
  { id:"sauce",  name:"元祖お好みソース＆青のりセット", desc:"あの濃厚ソースをおうちでも。", price:800, grad:"linear-gradient(135deg,#8a4a23,#5a2f16)" },
  { id:"set-4",  name:"元祖お好みセット（4枚・ソース付）", desc:"そば肉玉×2・うどん肉玉×2の詰め合わせ。", price:3800, grad:"linear-gradient(135deg,#d2622a,#8f2d1c)" }
];
const SHIPPING={standard:1000,remote:1300};
const PAYMENT_METHODS=["代金引換","クレジットカード","銀行振込"];
const CART_KEY="mitchan_cart_v1";
const yen=(n)=>"¥"+n.toLocaleString("ja-JP");
const Cart={load(){let c;try{c=JSON.parse(localStorage.getItem(CART_KEY))||{};}catch{c={};}let ch=false;for(const id of Object.keys(c)){const q=c[id];if(!PRODUCTS.some(p=>p.id===id)||!(q>0)){delete c[id];ch=true;}}if(ch)this.save(c);return c;},save(c){localStorage.setItem(CART_KEY,JSON.stringify(c));},add(id){const c=this.load();c[id]=(c[id]||0)+1;this.save(c);return c;},setQty(id,q){const c=this.load();if(q<=0)delete c[id];else c[id]=q;this.save(c);return c;},count(){return Object.values(this.load()).reduce((a,b)=>a+b,0);},subtotal(){const c=this.load();return Object.entries(c).reduce((s,[id,q])=>{const p=PRODUCTS.find(x=>x.id===id);return s+(p?p.price*q:0);},0);},shipping(){return this.subtotal()>0?SHIPPING.standard:0;},total(){return this.subtotal()+this.shipping();},clear(){localStorage.removeItem(CART_KEY);}};
