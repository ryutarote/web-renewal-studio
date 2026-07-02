# web-renewal-studio Design System ver.2 「Editorial Washoku」

飲食店リニューアル提案デモ向けの共通デザインシステム。Claude Design（claude.ai/design）で管理。

## 思想
- **明朝の見出し × クリーンなサンセリフ本文** — 料理と店の世界観を引き立てるエディトリアル。
- **余白とヘアライン**で上質さを出し、装飾は最小限。
- **ジャンル別アクセント**を1色だけ注入（寿司=藍緑 / ラーメン=朱 / 和食=藍 / カフェ=琥珀 / 居酒屋=紫 …）。各ページは `--accent` `--accent-ink` を上書きするだけで世界観が変わる。
- スマホ対応・常時SSL・外部依存なしの軽量1ファイル構成（相手の旧サイト改善を体現）。

## 構成
- `site.css` … トークン（color/type/space/radius/shadow）＋全コンポーネントのスタイル。
- `components/*.html` … 各コンポーネントのプレビュー（`@dsCard` 付き）。
  - Foundations: Color & Type
  - Components: Hero / Buttons / Menu list / Access / CTA band / Gallery card

## 使い方
`scripts/gen_prospect_sites.py` が `site.css` をインライン展開し、ジャンル別アクセントを注入して
各見込み客のデモ（`sites/leads-b3/<slug>/`）を生成する。
