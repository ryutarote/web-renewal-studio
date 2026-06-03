# 古いWebサイトを使う中小・個人店リスト収集

Google Map上で**評価50件以上**、かつ**2015年以前に作られたWebサイト**を使っている、
全国の**個人経営・中小企業**の店舗を収集するためのパイプライン。
サイトリニューアル営業のリード獲得を想定。

## 前提と制約（重要）

| 必要なデータ | 取得手段 | 状況 |
|---|---|---|
| 店舗 + Webサイト（全国） | OpenStreetMap / Overpass API | ✅ 無料・自動 |
| サイトが2015年以前に作られたか | Wayback Machine CDX API | ✅ 無料・自動（最古スナップショット年で判定） |
| 個人/中小の判定 | 大手チェーン名ブラックリスト除外 | ✅ 無料・自動（簡易） |
| **Google Mapの評価50件以上** | Google Places API（有料）/ 手動 | ⚠️ **無料の自動取得手段なし** |

「**無料手段だけで**」という方針のため、評価数だけは自動で埋められません。
本パイプラインは「評価数以外の条件を満たす候補」を全国から自動収集し、
評価数は最後に**手動 or 任意の有料API**で埋める2段構成です。

### 判定ロジックの注意

- 「2015年以前に作られたサイト」は **Wayback Machineの最古スナップショットが2015年以前** で代用しています。
  サイト初公開時期の良い近似ですが、ドメイン移転・リニューアル後にアーカイブされた場合はズレます。
  あくまで「古いサイトの可能性が高い候補」を絞る一次スクリーニングです。
- OpenStreetMapに登録され、かつ `website`/`contact:website` タグを持つ店舗のみが対象です。
  Google Mapにあってもサイトを登録していない店舗は拾えません（網羅性の限界）。

## セットアップ

```bash
pip install -r scripts/requirements.txt
```

## 実行

### 1. 候補収集（全国・無料）

```bash
# 全国47都道府県
python3 scripts/collect_candidates.py

# 動作確認（1〜2県・各県の調査数を制限）
python3 scripts/collect_candidates.py --prefectures 京都府 鳥取県 --limit-per-pref 50

# サイト年代判定をスキップして収集だけ（高速）
python3 scripts/collect_candidates.py --no-wayback
```

出力（`data/` 配下）:
- `candidates_all_<timestamp>.csv` … 収集した全候補
- `candidates_pre2015_<timestamp>.csv` … うちサイトが2015年以前の候補

### 2. 評価数の付与

```bash
# 手動モード（既定・無料）: gmap_check_url 列のリンクを開いて評価数を目視入力
python3 scripts/verify_reviews.py data/candidates_pre2015_<timestamp>.csv

# 任意: Google Places API（有料・APIキーが必要）
export GOOGLE_MAPS_API_KEY=xxxx
python3 scripts/verify_reviews.py data/candidates_pre2015_<timestamp>.csv --mode places-api --min-reviews 50
```

`manual` モードは各行に `gmap_check_url`（Google Map検索リンク）を付与し、
`google_reviews` 列を `TODO` にします。リンクを開いて評価数を入力 → 50以上だけ残せば完成です。

## ⚠️ 実行環境について（Claude Code on the web）

このリポジトリをClaude Code on the webのセッションで動かす場合、
**ネットワークポリシーによって外部アクセスが遮断される**ことがあります。
本パイプラインはOverpass / Wayback Machineへの外部HTTPアクセスが必須です。

- 開発時の検証では、当環境のegressが全面的にブロック（全ホスト403）されていました。
- そのため**スクリプトはローカルPC、または外部アクセスを許可したネットワークポリシーの環境**で実行してください。
- ネットワークポリシーの設定は <https://code.claude.com/docs/en/claude-code-on-the-web> を参照。

## 出力カラム

| カラム | 内容 |
|---|---|
| prefecture | 都道府県 |
| name | 店舗名 |
| category | 業種（OSMタグ由来） |
| website / domain | サイトURL / ドメイン |
| address | 住所（OSMタグから組み立て） |
| lat / lon | 緯度経度 |
| phone | 電話番号 |
| site_oldest_year | Wayback最古スナップショット年 |
| site_pre_cutoff | 2015年以前か（yes/no/unknown） |
| google_reviews | 評価数（後段で付与） |

## 今後の拡張余地

- 評価数の無料取得は不可。どうしても自動化するならGoogle Places API（有料・$200/月の無料枠あり）の導入を検討。
- チェーン判定はブラックリスト方式の簡易版。OSMの `brand`/`operator` タグや店舗数カウントで精度向上可能。
- サイトの「古さ」判定に、HTML解析（jQuery旧版・Flash・viewport無し・©年表記など）の補助シグナルを追加可能。
