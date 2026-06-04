/* モックEC: 商品データ + カート（localStorage）。デモ。価格は参考の目安。 */
const PRODUCTS = [
  { id:"jaja-4", name:"じゃじゃ麺 4食（特製肉味噌付）", desc:"もちもち平打ち麺と秘伝の肉味噌のセット。", price:1400, grad:"linear-gradient(135deg,#caa06a,#6b4423)" },
  { id:"jaja-8", name:"じゃじゃ麺 8食（特製肉味噌付）", desc:"ご家族・来客に。たっぷり8食分。", price:2600, grad:"linear-gradient(135deg,#b98a52,#4a2f17)" },
  { id:"miso",   name:"特製肉味噌（単品）", desc:"十数種の材料を炒め寝かせた秘伝の味噌。", price:600, grad:"linear-gradient(135deg,#8a5a2e,#4a2f17)" },
  { id:"gift",   name:"進物用 詰め合わせ（のし対応）", desc:"盛岡名物をご贈答に。", price:3200, grad:"linear-gradient(135deg,#6b4423,#3a240f)" }
];
const SHIPPING={standard:1000,remote:1300};
const PAYMENT_METHODS=["代金引換","クレジットカード","銀行振込"];
const CART_KEY="jajamen_cart_v1";
const yen=(n)=>"¥"+n.toLocaleString("ja-JP");
const Cart={load(){let c;try{c=JSON.parse(localStorage.getItem(CART_KEY))||{};}catch{c={};}let ch=false;for(const id of Object.keys(c)){const q=c[id];if(!PRODUCTS.some(p=>p.id===id)||!(q>0)){delete c[id];ch=true;}}if(ch)this.save(c);return c;},save(c){localStorage.setItem(CART_KEY,JSON.stringify(c));},add(id){const c=this.load();c[id]=(c[id]||0)+1;this.save(c);return c;},setQty(id,q){const c=this.load();if(q<=0)delete c[id];else c[id]=q;this.save(c);return c;},count(){return Object.values(this.load()).reduce((a,b)=>a+b,0);},subtotal(){const c=this.load();return Object.entries(c).reduce((s,[id,q])=>{const p=PRODUCTS.find(x=>x.id===id);return s+(p?p.price*q:0);},0);},shipping(){return this.subtotal()>0?SHIPPING.standard:0;},total(){return this.subtotal()+this.shipping();},clear(){localStorage.removeItem(CART_KEY);}};
