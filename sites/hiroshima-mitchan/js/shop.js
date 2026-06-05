/* モックEC: 商品データ + カート（localStorage）。デモ。
   価格・商品は公式オンラインショップ（okonomi.jp）の実データに基づく参考値（税込）。
   画像は公式商品画像を images.weserv.nl 経由でhttps配信。 */
const IMG = (u) => "https://images.weserv.nl/?url=" + encodeURIComponent(u) + "&w=640&h=480&fit=cover&output=webp";
const PRODUCTS = [
  { id:"soba",     name:"広島流お好み焼 そば入（410g）", desc:"元祖の味をご家庭で。プロトン凍結で焼きたての風味をそのまま。", price:1188, img:IMG("makeshop-multi-images.akamaized.net/mitchan/itemimages/000000000001_bwufDHD.jpg"), grad:"linear-gradient(135deg,#e8a05a,#c75b1e)" },
  { id:"ikaten",   name:"広島流お好み焼 イカ天入（420g）", desc:"パリッとしたイカ天の食感がアクセント。", price:1296, img:IMG("makeshop-multi-images.akamaized.net/mitchan/itemimages/000000000002_hjuQvYm.jpg"), grad:"linear-gradient(135deg,#e6b06a,#b3471f)" },
  { id:"special",  name:"広島流お好み焼 スペシャル（430g）", desc:"いか＋えび入りの贅沢な一枚。", price:1404, img:IMG("makeshop-multi-images.akamaized.net/mitchan/itemimages/000000000003_7o88H43.jpg"), grad:"linear-gradient(135deg,#d2622a,#8f2d1c)" },
  { id:"mochi",    name:"広島流お好み焼 もち入（450g）", desc:"もちもち食感がうれしい、ボリューム満点。", price:1350, img:IMG("makeshop-multi-images.akamaized.net/mitchan/itemimages/000000000081_OSBJjje.jpg"), grad:"linear-gradient(135deg,#e6b06a,#a8431d)" },
  { id:"kaki",     name:"広島流お好み焼 カキ入（500g）", desc:"広島名物・牡蠣をたっぷり。季節を感じる一枚。", price:1728, img:IMG("makeshop-multi-images.akamaized.net/mitchan/itemimages/000000000004_2GiARFW.jpg"), grad:"linear-gradient(135deg,#c9772f,#7a2c14)" },
  { id:"sauce",    name:"みっちゃん総本店 お好みソース（300g）", desc:"あの濃厚ソースをおうちでも。", price:432, img:IMG("makeshop-multi-images.akamaized.net/mitchan/itemimages/000000000105_Dj19eTl.jpg"), grad:"linear-gradient(135deg,#8a4a23,#5a2f16)" }
];
/* 送料は公式同様に地域別（クール宅急便・税込）。デモは中国地方基準を既定とする。 */
const SHIPPING={standard:1000,remote:2000};
const PAYMENT_METHODS=["クレジットカード","代金引換","銀行振込","コンビニ払い"];
const CART_KEY="mitchan_cart_v2";
const yen=(n)=>"¥"+n.toLocaleString("ja-JP");
const Cart={load(){let c;try{c=JSON.parse(localStorage.getItem(CART_KEY))||{};}catch{c={};}let ch=false;for(const id of Object.keys(c)){const q=c[id];if(!PRODUCTS.some(p=>p.id===id)||!(q>0)){delete c[id];ch=true;}}if(ch)this.save(c);return c;},save(c){localStorage.setItem(CART_KEY,JSON.stringify(c));},add(id){const c=this.load();c[id]=(c[id]||0)+1;this.save(c);return c;},setQty(id,q){const c=this.load();if(q<=0)delete c[id];else c[id]=q;this.save(c);return c;},count(){return Object.values(this.load()).reduce((a,b)=>a+b,0);},subtotal(){const c=this.load();return Object.entries(c).reduce((s,[id,q])=>{const p=PRODUCTS.find(x=>x.id===id);return s+(p?p.price*q:0);},0);},shipping(){return this.subtotal()>0?SHIPPING.standard:0;},total(){return this.subtotal()+this.shipping();},clear(){localStorage.removeItem(CART_KEY);}};
