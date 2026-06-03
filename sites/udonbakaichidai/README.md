# うどんバカ一代 リニューアルサイト（提案モック）

診断レポート（`docs/site-audit-top5.md`）で指摘した課題を解消する、リニューアル版のフロントエンド実装。
**依存ライブラリ・ビルド不要の静的サイト**。`index.html` をブラウザで開くだけで動作する。

## 動かし方

```bash
# 方法1: ファイルを直接開く
open sites/udonbakaichidai/index.html        # mac
# xdg-open / ブラウザにドラッグでも可

# 方法2: 簡易サーバ（推奨。相対パス・OGP確認向き）
cd sites/udonbakaichidai && python3 -m http.server 8000
# → http://localhost:8000
```

## 診断課題 → 本実装での対応

| 旧サイトの課題（診断） | 本リニューアルでの対応 |
|---|---|
| 🔴 非HTTPS（`http://`）でEC決済 | HTTPS前提の構成。決済はトークン方式（カード非保持/PCI DSS準拠）を想定したモックUIで明示 |
| 🔴 PC/スマホ別URL（`/sp/`） | **レスポンシブ1URL**。CSSブレークポイントで全デバイス対応、モバイルはドロワーナビ |
| 構造化データ欠如 | `Restaurant` + `AggregateRating` の JSON-LD を実装（MEO/リッチリザルト対策） |
| メタ/OGP未整備 | `title`/`description`/canonical/OGP/Twitter Card を整備 |
| 旧型ECの体験 | モダンなカート（追加/数量/削除/合計、localStorage永続化）＋チェックアウトUI |
| アクセシビリティ | セマンティックHTML、`aria-*`、スキップリンク、フォーカス可視化、`prefers-reduced-motion` |

## 構成

```
sites/udonbakaichidai/
├── index.html      # 1ページ完結（ヒーロー/名物/こだわり/メニュー/声/店舗/EC）
├── css/style.css   # モバイルファースト、配色: 藍×山吹×生成り×朱
├── js/shop.js      # モックEC: 商品データ + カート(localStorage)
└── js/main.js      # ナビ/商品描画/カートDrawer/チェックアウト
```

## モックECについて（重要）

- カート・チェックアウトは **localStorage上のデモ**。**決済は一切発生しない**。
- カード入力欄はダミーで、番号は送信・保存されない。
- 本番化の際は Stripe / Square / GMO 等の**決済代行のトークン方式**でカード非保持化し、
  注文・在庫はバックエンド（Shopify等のSaaS推奨）に置く。

## 本番化で差し替える項目

- 料理・商品の**写真**（現状はCSSグラデーションのプレースホルダ）
- **価格・メニュー・商品**を実データに
- 構造化データの **`ratingValue`/`reviewCount`** を実Googleレビュー値に
- 店舗の**緯度経度・住所**の確定とGoogleマップ埋め込み
- OGP画像（`assets/ogp.jpg`）の用意
- 常時SSL（Let's Encrypt等）と旧URLからの **301リダイレクト**設計
