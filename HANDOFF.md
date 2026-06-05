# プロジェクト引き継ぎ（HANDOFF）— リニューアル提案サイト群

> このファイルは「新しいセッション（ネットワーク許可済み環境）」へ作業文脈を完全に引き継ぐためのものです。
> 新セッションでこのリポジトリ（`ryutarote/moneytize-claude-code` / ブランチ `main`）を開き、本ファイルを最初に読んでから着手してください。

---

## 0. 最優先タスク（新セッションでやること）

1. 各店の**公式サイトに直接アクセスして実データを取得**し、対象サイトの「目安」表記を**実データへ置換**する。
   - これまではサンドボックスの外部遮断（`host_not_allowed`）と公式サイトのボット拒否（`403`）で**直接取得できず**、WebSearch（食べログ/ぐるなび等）と、ユーザーが貼った公式HTML（みんみん・うどん）で補ってきた。
   - 新環境ではネットワーク許可済みのはずなので、まず到達確認 → 取得 → 反映する。
2. 取得した実データで **メニュー全価格・営業時間・定休日・電話・通販条件** を更新。
3. 可能なら**公式の料理写真**を取り込み、現在のプレースホルダ（絵文字タイル）を実写真へ差し替え（下記「画像方針」参照）。
4. 各サイトを**ローカル実機（Playwright/Chromium）で検証** → commit → push → GitHub Pages デプロイ成功を確認。

### 着手前チェック（ネットワーク到達確認）
```bash
for u in https://www.okonomi.co.jp/ https://shikairou.com/ https://www.pairon.iwate.jp/ \
         https://www.minmin.co.jp/ http://www.udonbakaichidai.co.jp/ https://images.weserv.nl/ ; do
  echo "$u -> $(curl -s -o /dev/null -w '%{http_code}' -m 12 "$u")"
done
```
- `200/30x` が返れば直接取得OK。`403 host_not_allowed` のままなら、その環境にもまだ許可が反映されていない（=新環境を作り直す／許可ホストを確認）。
- 公式が **WebFetch を 403 で拒否**する場合があるため、まずは `curl` で生HTMLを取得 → 解析する手が確実。

### 許可したい外部ホスト（取得・表示に必要）
- 公式: `www.okonomi.co.jp`, `shikairou.com`, `www.pairon.iwate.jp`, `www.minmin.co.jp`, `www.udonbakaichidai.co.jp`
- 画像プロキシ（http画像をhttps化して表示）: `images.weserv.nl`
- フォント: `fonts.googleapis.com`, `fonts.gstatic.com`
- （動画を使う場合）`i.ytimg.com`, `www.youtube-nocookie.com`

---

## 1. プロジェクト概要

実在の有名飲食店の**リニューアル提案デモ（モック）**を、共通のSPA基盤で複数制作している。
- リポジトリ: `ryutarote/moneytize-claude-code` / 作業ブランチ: **`main`**（既定ブランチも `main`）
- 公開: **GitHub Pages**（`sites/` をルートにサブディレクトリ配信）
- 公開トップ（5サイト一覧）: https://ryutarote.github.io/moneytize-claude-code/

### サイト一覧
| slug（`sites/<slug>/`） | 店舗 | ジャンル/地域 | 公開URL | 公式サイト | 配色(primary) | モチーフ |
|---|---|---|---|---|---|---|
| `udonbakaichidai` | 手打十段 うどんバカ一代 | 讃岐うどん/香川 | …/udonbakaichidai/ | http://www.udonbakaichidai.co.jp/ | 藍 #1a3a5c | 🍜（実写真あり） |
| `utsunomiya-minmin` | 宇都宮みんみん | 餃子/栃木 | …/utsunomiya-minmin/ | https://www.minmin.co.jp/ | 朱赤 #9c1f1f | 🥟 |
| `hiroshima-mitchan` | みっちゃん総本店 八丁堀本店 | お好み焼/広島 | …/hiroshima-mitchan/ | 橙赤 #b3471f | https://www.okonomi.co.jp/ | 🍳 |
| `nagasaki-shikairou` | 中華料理 四海樓 | ちゃんぽん/長崎 | …/nagasaki-shikairou/ | https://shikairou.com/ | 紺 #1f5673 | 🍜 |
| `morioka-jajamen` | 白龍（パイロン）本店 | じゃじゃ麺/盛岡 | …/morioka-jajamen/ | https://www.pairon.iwate.jp/ | 味噌茶 #6b4423 | 🍜 |

---

## 2. SPA基盤の構造（全サイト共通）

各サイトは `sites/<slug>/` に独立した静的SPA。構成は同一：
```
sites/<slug>/
  index.html      … 1ファイルSPA（複数の .view を内包、ハッシュルーティング）
  css/style.css   … デザイントークン(:root変数) + 全コンポーネント
  js/shop.js      … 商品データ(PRODUCTS) + カート(Cart, localStorage)
  js/main.js      … ルーター + 商品描画 + カート/モーダル + A11y
```

### ルーティング（`js/main.js`）
- `const SITE`（サイト名）, `const ROUTES`（`{routeKey: 表示名}`）, `const DESC`（route別meta description）を**サイトごとに定義**。
- `location.hash`（例 `#/menu`）で `data-route` に一致する `.view` を表示。遷移ごとに: タイトル更新・`<meta name=description>`更新・パンくず更新・**先頭スクロール**・**見出し(`[data-view-title]`)へフォーカス**・`#route-status`(aria-live)読み上げ・各UIクローズ。
- 各 `.view` の主見出しは **`<h1 class="section-title" data-view-title>`**（=ページ単位で h1 は1つ）。

### カート/EC（`js/shop.js` + `main.js`）
- `PRODUCTS = [{id,name,desc,price,grad}]`（画像未使用。`grad`は背景、サムネは CSS で店モチーフ絵文字を表示）。
- `SHIPPING = {standard, remote}`、`CART_KEY`（**サイト毎にユニーク**）。`Cart.load()` は**存在しない商品IDを自動除去**（バージョン跨ぎの不整合防止）。
- カートバッジは空時 `hidden`（`.cart-count[hidden]{display:none}` 必須）。ドロワー/チェックアウトは**フォーカストラップ＋`body.no-scroll`**。ゲスト購入既定、アカウント作成は任意。

### デザイントークン（`css/style.css` の `:root`）
- 主要変数: `--indigo`(=primary), `--indigo-dark`, `--gold`, `--cream`, `--paper`, `--vermilion`, `--ink`, `--muted`, `--line`, `--radius`, `--shadow`。
  - ※歴史的経緯で primary 変数名が `--indigo` のまま（各サイトで色値だけ差し替え）。命名は気にせず色だけ変える。
- ヒーローは**画像を重ねず**、`.hero-media`（装飾バンド＋店モチーフ絵文字）→ 下に `.hero-inner`（テキスト）の**積層**。
- 主なコンポーネントclass: `.view`, `.hero`, `.news-bar`, `.banners--text/.banner-card`, `.meibutsu-grid/.dish-card/.dish-photo`, `.greeting-grid`, `.menu-cols/.menu-list`, `.menu-table`(価格/栄養表), `.guide-list`, `.rule-cards`, `.shop-grid/.shop-map`, `.ec-info-grid/.ec-info`, `.info-list/.info-list--wide`, `.product-grid/.product-card`, カート(`.cart-drawer`), モーダル(`.modal`), `.crumb-bar`, `.to-top`。

### 新サイトの作り方（テンプレ流用）
1. `cp -r sites/utsunomiya-minmin sites/<new-slug>`（minminが最新・最良テンプレ）
2. `css/style.css` の `:root` の `--indigo/--indigo-dark/--shadow` と、`.hero-media` 内のハードコード色、絵文字（`.hero-media::after` / `.dish-photo::after` / `.product-thumb:empty::after`）を差し替え。
3. `js/main.js` の `SITE/ROUTES/DESC`、`js/shop.js` の `PRODUCTS/CART_KEY` を差し替え。
4. `index.html` を内容差し替え（**構造は不変**：header/nav・crumb・各view・footer・cart drawer・checkout modal・to-top）。
5. ルート一覧 `sites/index.html` にカード追加。

---

## 3. 各サイトの「確定済み」と「要・実データ確認（現状は目安表記）」

> ✅=公開情報で確認済み（反映済み） / ⚠=未確認のため「目安」表記。公式から取得して置換すること。

### みっちゃん総本店 八丁堀本店（`hiroshima-mitchan` / https://www.okonomi.co.jp/）
- ✅ 昭和25年(1950)創業・広島お好み焼の元祖（そば入り/お好みソース/ヘラ文化）
- ✅ 住所 広島市中区八丁堀6-7 チュリス八丁堀1F
- ✅ 営業 平日 11:30–14:30 / 17:30–21:00、土日祝 11:00–14:30 / 17:00–21:00
- ✅ 定休 火曜（祝日の場合は翌水曜）
- ✅ お好み焼き ¥930〜、夜の鉄板（コウネ/牡蠣焼き/ホルモン）
- ⚠ 電話番号、全メニュー価格（そば肉玉/うどん肉玉/スペシャル/トッピング）、通販（冷凍お好み焼き）の有無・商品・送料

### 四海樓（`nagasaki-shikairou` / https://shikairou.com/）
- ✅ 明治32年(1899)創業・創業者 陳平順（福建省福州出身）・ちゃんぽん/皿うどん発祥
- ✅ 松が枝町（大浦天主堂電停すぐ）、2F ちゃんぽんミュージアム（無料）、5F 展望レストラン（長崎港一望・全面ガラス張り）
- ⚠ 正確な番地（暫定「松が枝町4-5」）、電話（暫定 095-822-1296）、営業時間/定休、メニュー全価格（ちゃんぽん/皿うどん/コース）、公式通販の有無

### 白龍（パイロン）本店（`morioka-jajamen` / https://www.pairon.iwate.jp/）
- ✅ 昭和28年(1953)創業・創業者 高階貫勝・盛岡じゃじゃ麺発祥（満州の炸醤麺を盛岡風に）
- ✅ 住所 盛岡市内丸5-15
- ✅ 営業 月〜土 9:00–21:00（L.O.20:40）／日 11:30–16:00、定休 無し（盆/年始休）
- ✅ じゃじゃ麺(中) ¥550、ちーたんたん ¥50、ろうすう麺/冷やしつけ麺/水餃子/焼餃子、食べ方（混ぜる→味調整→締めのちーたんたん）
- ⚠ 電話番号、じゃじゃ麺 小/大の価格、サイド/ドリンク価格、通販条件

### 参考（精緻化済みの2サイト = やり方の手本）
- `utsunomiya-minmin`：ユーザーが貼った公式HTML（gyoza/about）で精緻化済み。**栄養成分表・アレルギー・ダブルスイライス¥1,360・焼/水/揚 各¥380** など実データ反映済み。
- `udonbakaichidai`：公式HTMLで精緻化済み。**実写真を images.weserv.nl 経由で表示**（http画像のhttps化）。お品書き全価格・求人詳細・店舗情報・地図など反映済み。

---

## 4. 画像方針（重要）

- 外部画像は **http配信が多くhttps（GitHub Pages）で混在コンテンツ遮断**になる → **`images.weserv.nl` プロキシ**でhttps化して表示（udonで実績あり）。
  - 例: `https://images.weserv.nl/?url=www.example.co.jp/path/img.jpg`
- **誤った写真の流用は厳禁**（ユーザー指摘あり）。各料理に正しく対応する公式画像のみ使用。確証がなければ**現状の絵文字タイルのまま**にする。
- 本番運用では「画像を自リポジトリへ取り込み・自前配信」が理想（プロキシ依存・直リンク回避）。
- 文面は**オリジナル**で書く（公式テキストの逐語転載はしない）。事実（住所/価格/時間/沿革）は引用OK、確証なき値は「目安」と明記。

---

## 5. ローカル実機デバッグ（Playwright + Chromium）

外部画像はローカルでは読めない（ネット制限）ので、**レイアウト幾何・JS挙動・コンソール**を検証する。Chromium本体は同梱済み。

```bash
# 1) ローカル配信（sites をルートに）
cd /home/user/<repo>/sites && python3 -m http.server 8123 --bind 127.0.0.1 &

# 2) Playwright（グローバル導入済み・ESMは絶対パスのデフォルトimport）
#    PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers に Chromium あり
cat > /tmp/check.mjs <<'EOF'
import pkg from '/opt/node22/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b=await chromium.launch();
const p=await (await b.newContext({viewport:{width:1280,height:900}})).newPage();
const errs=[]; p.on('pageerror',e=>errs.push(String(e)));
await p.goto('http://127.0.0.1:8123/<slug>/',{waitUntil:'domcontentloaded'}); await p.waitForTimeout(400);
for(const r of ['home','menu','story','shop','order']){
  await p.evaluate(rt=>location.hash=rt==='home'?'#/':'#/'+rt, r); await p.waitForTimeout(180);
  console.log(r, await p.evaluate(()=>[...document.querySelectorAll('.view')].filter(v=>v.classList.contains('is-active')&&!v.hidden).map(v=>v.dataset.route)));
}
await p.evaluate(()=>location.hash='#/order'); await p.waitForTimeout(200);
await p.click('.add-cart'); await p.waitForTimeout(150);
console.log('cartTotal', await p.$eval('#cart-total',e=>e.textContent), 'pageErrors', errs);
await b.close();
EOF
node /tmp/check.mjs
```
検証観点: 全ルートで `.view` が1つだけ表示 / 可視h1=1 / カート計算 / ヒーロー非重なり / `pageErrors`・`console error` が 0。

---

## 6. デプロイ（GitHub Pages）

- ワークフロー: `.github/workflows/pages.yml`
  - トリガー: `push` → ブランチ `main`、`paths: sites/**` または ワークフロー自身。
  - `sites/` を**そのままアーティファクトのルート**としてアップロード → `/<slug>/` で配信。
  - `actions/configure-pages@v5`（`enablement` は付けない）→ `upload-pages-artifact`（`path: sites`）→ `deploy-pages`。
- **重要な前提（設定済み・触らない）**:
  - 既定ブランチ = `main`。
  - `github-pages` 環境の **Deployment branches = No restriction**（これが無いとデプロイがブランチ保護で2秒失敗する）。
  - リポジトリは Public（Pages無料利用のため）。**機密の営業リスト等は履歴から除去済み**（`data/seed_candidates_websearch.csv`, `docs/site-audit-top5.md` を filter-branch で削除済み）。
- デプロイ確認: GitHub MCP（`mcp__github__actions_list` の `list_workflow_runs`, `resource_id: pages.yml`）で最新runの `conclusion: success` を確認。
- pushは `git push -u origin main`（ネット失敗時は指数バックオフで最大4回リトライ）。コミットメッセージ末尾に必ず:
  `https://claude.ai/code/session_019EnXotea6B91CYamKr9wRQ`（※新セッションでは自セッションのURLに置換）。

---

## 7. 制約・品質基準（プリンシパルWebディレクター視点）

- 目標品質: **95点以上**。SPA/カート/A11y(フォーカス管理・aria-live・コントラストAA以上・h1構造)/SEO(meta/OGP/JSON-LD)/CLS低減/レスポンシブを全サイトで担保。
- 既知の品質ポイント（過去に修正した実バグ）:
  - `.cart-count[hidden]{display:none}` が無いと**空カートでもバッジが出る**（class が `[hidden]` を上書き）。`.modal[hidden]{display:none}` も同様に必須。
  - ヒーローは**画像と文字を重ねない**（重ねると可読性NGの指摘あり）。
  - 文字入りバナー画像は `object-fit: contain`（cover だと文字が切れる）。
  - 料理カードは**全カード同一比率**（特集だけ別比率にしない）。
- IP配慮: 公式テキストの逐語コピー不可。オリジナル文面＋事実引用。デモECは「決済なし」を明記。

---

## 8. 現状サマリ（このセッション終了時点）

- 5サイト作成・公開済み（最新ビルド run #28 success）。
- うどん・みんみんは公式HTMLで精緻化済み。みっちゃん・四海樓・白龍は**WebSearch由来＋一部目安**。
- 直近の課題＝**3店を公式直取得で精緻化**＋**実写真取り込み**（本ファイルの「最優先タスク」）。

> 新セッションでは、まず §0 の到達確認 → 公式取得 → §3 の⚠項目を実データへ置換 → §5 で検証 → §6 でデプロイ、の順で進めてください。
