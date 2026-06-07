# プロジェクト引き継ぎ（HANDOFF）— リニューアル提案サイト群

> このファイルは「新しいセッション（ネットワーク許可済み環境）」へ作業文脈を完全に引き継ぐためのものです。
> 新セッションでこのリポジトリ（`ryutarote/web-renewal-studio` / ブランチ `main`）を開き、本ファイルを最初に読んでから着手してください。

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
- リポジトリ: `ryutarote/web-renewal-studio` / 作業ブランチ: **`main`**（既定ブランチも `main`）
- 公開: **GitHub Pages**（`sites/` をルートにサブディレクトリ配信）
- 公開トップ（5サイト一覧）: https://ryutarote.github.io/web-renewal-studio/

### サイト一覧
| slug（`sites/<slug>/`） | 店舗 | ジャンル/地域 | 公開URL | 公式サイト | 配色(primary) | モチーフ |
|---|---|---|---|---|---|---|
| `udonbakaichidai` | 手打十段 うどんバカ一代 | 讃岐うどん/香川 | …/udonbakaichidai/ | http://www.udonbakaichidai.co.jp/ | 藍 #1a3a5c | 🍜（実写真あり） |
| `utsunomiya-minmin` | 宇都宮みんみん | 餃子/栃木 | …/utsunomiya-minmin/ | https://www.minmin.co.jp/ | 朱赤 #9c1f1f | 🥟 |
| `hiroshima-mitchan` | みっちゃん総本店 八丁堀本店 | お好み焼/広島 | …/hiroshima-mitchan/ | 橙赤 #b3471f | https://www.okonomi.co.jp/ | 🍳 |
| `nagasaki-shikairou` | 中華料理 四海樓 | ちゃんぽん/長崎 | …/nagasaki-shikairou/ | https://shikairou.com/ | 紺 #1f5673 | 🍜 |
| `morioka-jajamen` | 白龍（パイロン）本店 | じゃじゃ麺/盛岡 | …/morioka-jajamen/ | https://www.pairon.iwate.jp/ | 味噌茶 #6b4423 | 🍜 |
| `fukui-yoroppaken` | ヨーロッパ軒 総本店 | ソースカツ丼/福井 | …/fukui-yoroppaken/ | http://yo-roppaken.gourmet.coocan.jp/ | ソース茶 #6b3f1f | 🍱（shadcn設計） |

### 第2弾（リニューアル候補10件 / shadcn設計）— ✅全10件 完成・公開
| slug | 店舗 | ジャンル/地域 | 配色(primary) | モチーフ | 備考 |
|---|---|---|---|---|---|
| `fukui-yoroppaken` | ヨーロッパ軒 総本店 | ソースカツ丼/福井 | ソース茶 #6b3f1f | 🍱 | 雛形 |
| `sendai-ajitasuke` | 味太助 | 牛タン/仙台 | 炭黒 #2f2a26 | 🥩 | 牛タン焼発祥 |
| `sapporo-ajinosanpei` | 味の三平 | 味噌ラーメン/札幌 | 味噌茶 #6b4a26 | 🍜 | 味噌ラーメン発祥／自社通販でない旨明記 |
| `osaka-daruma` | 串かつだるま | 串カツ/大阪 | だるま朱赤 #b32d28 | 🍢 | 串カツ発祥・二度づけ禁止 |
| `hakata-rakutenchi` | 元祖もつ鍋 楽天地 | もつ鍋/博多 | 緑 #27512f | 🍲 | 公式通販の実価格反映 |
| `kochi-myojinmaru` | 藁焼き鰹たたき 明神丸 | 鰹たたき/高知 | 土佐の海紺 #234d5e | 🐟 | 塩たたき発祥・明神水産 |
| `izumo-haneya` | 献上そば 羽根屋 | 出雲そば/島根 | 藍墨 #33475c | 🥢 | 江戸末期創業・献上そば |
| `okinawa-agarie` | 東江そば | 沖縄そば/沖縄 | 海teal #1f6f76 | 🍜 | 自家製生麺・公式通販反映 |
| `kitakata-genraiken` | 源来軒 | 喜多方ラーメン/福島 | 醤油茶 #5e4126 | 🍜 | 元祖。**2024年閉店**のため“新規構築型提案”と明記 |
| `nagoya-houraiken` | あつた蓬莱軒 | ひつまぶし/名古屋 | 漆 #5a2f22 | 🍱 | ひつまぶし発祥(登録商標)・四つの食べ方 |

- 全15サイト（第1弾5＋第2弾10）をPlaywrightで一括検証済み: 各サイト全ルートで`.view`単一表示・可視h1=1・カート計算正常・pageError 0。
- 各サイトは公式/食べログ/観光サイト等で実データ取得。確証なき値は「目安」と可視明記、自社通販でない店はECにその旨補足、ECは全て「デモ（決済なし）」明記。

> **デザイン方針（第2弾〜）**: shadcn/ui（New York）を**素のCSSへ移植**して適用（ビルド不要・MCP不使用）。`fukui-yoroppaken/css/style.css` の `:root` が雛形＝HSLトークン(`--background/--foreground/--card/--primary/--secondary/--accent/--border/--input/--ring/--radius`)＋`hsl(var(--x))`参照、`--shadow-sm/--shadow/--shadow-lg`、角丸`.625rem`、フォーカスは2pxオフセットのリング、`.badge/.btn(primary|outline)/.card/.menu-table` 等のコンポーネント。新サイトはこのCSSを雛形に色トークンだけ差し替える。

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

### みっちゃん総本店 八丁堀本店（`hiroshima-mitchan` / https://www.okonomi.co.jp/）— ✅公式直取得で精緻化済み（2026-06）
- ✅ 昭和25年(1950)創業・広島お好み焼の元祖（初代 井畝満夫）。八丁堀本店は昭和43年(1968)開店
- ✅ 住所 広島市中区八丁堀6-7 チュリス八丁堀1F／**電話 082-221-5438**／47席・禁煙・各種カード可
- ✅ 営業 平日 11:30–14:30 / 17:30–21:00、土日祝 11:00–14:30 / 17:00–21:00（L.O.閉店30分前）／定休 火曜（祝日は翌水曜）
- ✅ 全メニュー実価格反映（そば/うどん肉玉子 ¥960、スペシャル ¥1,500、特製 ¥1,830、DX ¥2,030、カキ入 ¥1,840、トッピング、鉄板焼き、ドリンク）
- ✅ 通販＝公式EC(okonomi.jp)の実商品・実価格・公式商品画像（weserv経由）を反映。地域別送料。プロトン凍結・賞味約1年

### 四海樓（`nagasaki-shikairou` / https://shikairou.com/）— ✅公式直取得で精緻化済み（2026-06）
- ✅ 明治32年(1899)創業・創業者 陳平順（福建省福州出身）・ちゃんぽん/皿うどん発祥。昭和48年(1973)松が枝町へ移転、平成12年(2000)100周年新築
- ✅ **〒850-0921 長崎市松が枝町4-5（確定）／電話 095-822-1296・FAX 095-826-7353（確定）**
- ✅ 営業 昼 11:30–15:00(最終入店14:30)／夜 17:00–20:00(最終入店19:30)、1F売店 10:00–17:30／定休 水曜（隔週・月2回）
- ✅ ちゃんぽん/皿うどんの公式画像・初代陳平順の写真を反映（weserv経由）
- ⚠ メニュー全価格＝公式サイト非掲載（現状「目安」表記のまま）。四海樓は**自社通販なし**（Amazon/店頭1F売店）。ECは提案デモと明記済み。
- 注: 2F ミュージアム/5F 展望レストランは公式サイトに記載が無いため、可視テキストからは記述を控えめにし営業時間表記へ置換済み

### 白龍（パイロン）本店（`morioka-jajamen` / https://www.pairon.iwate.jp/）— ✅公式直取得で精緻化（2026-06）
- ✅ 創業者 高階貫勝・盛岡じゃじゃ麺発祥（旧満州の炸醤麺を盛岡風に）。※創業年は公式は「約60年」表記のみ（昭和28年は二次情報）
- ✅ 住所 盛岡市内丸5-15／**電話 019-624-2247（確定・新規反映）**／姉妹店（分店・川徳店・フェザン店）
- ✅ 食べ方を公式手順（味調整→混ぜる→卵割り→店員にちーたんたん依頼）に精緻化。じゃじゃ麺の公式画像・本店外観写真を反映（weserv経由）
- ⚠ 営業時間/定休は公式サイト非掲載（現状は公開情報ベースの値を維持）。じゃじゃ麺 小/大・サイド・楽天通販の実価格は楽天がbot遮断で未取得＝「目安」のまま

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

## 8. 現状サマリ（最新セッション 2026-06 終了時点）

- 5サイト作成・公開済み。
- **5サイト全て公式直取得で精緻化完了**：うどん・みんみんに加え、みっちゃん・四海樓・白龍も公式サイト/公式ECから実データ取得し反映。
  - みっちゃん：電話・全メニュー実価格・公式EC実商品/実画像/地域別送料。
  - 四海樓：住所/電話/FAX/営業時間/定休（公式確定値）・ちゃんぽん/皿うどん/初代の公式画像。
  - 白龍：電話番号（新規）・公式の食べ方手順・じゃじゃ麺/外観の公式画像。
- 全サイト共通バグ修正：空カートCTAがテンプレ流用の`#/ec`（うどん文言）で壊れていた箇所を各サイトの`#/order`へ修正。
- ローカル検証（Playwright）：全ルートで .view 単一表示・可視h1=1・カート計算正常・pageError 0 を確認。weserv画像URLは全て200(webp)を確認。
- 残課題（⚠）：四海樓のメニュー価格（公式非掲載）、白龍の小/大価格・楽天通販（bot遮断）は「目安」のまま。別接続での楽天再取得 or 店舗確認が必要。

> 新セッションでは、まず §0 の到達確認 → 公式取得 → §3 の⚠項目を実データへ置換 → §5 で検証 → §6 でデプロイ、の順で進めてください。

---

## 9. UI/UXレビュー反映（全15サイト一括改修・2026-06）

グッドパッチ・シニアディレクター視点のレビューを受け、全15サイトへ一括適用（`scripts/uiux_refine.py`／冪等）。各サイトの `css/style.css` 末尾に共通上書きブロック（マーカー: `UI/UX 改修（レビュー反映・全サイト共通追記）`）、`index.html`・`js/main.js` を編集。

**適用済み**
- **P0 絵文字撤去**: ヒーローの巨大絵文字を撤去しクリーンなカラーバンドに（`.hero-media::after{content:""}`）。空の料理/商品タイルは絵文字を抑制（grayscale+低opacity）し「写真は準備中です」の控えめプレースホルダを表示。※実写真タイル（`--photo`/`<img>`入り＝`:empty`非該当）は無影響。
- **P0 SEO**: 全サイト `robots` を `noindex, nofollow` に。公式URL向きの `canonical` を除去（本物との混同・誤クロール防止）。
- **P0/P2 信頼**: 画面左下に「提案デモ（モック）」リボンを常時表示（`.demo-ribbon`）。
- **P1 A11y**: モバイルナビ閉時に `inert`（画面外メニューへのTab侵入を防止）。**デスクトップ幅では inert にしない**よう `matchMedia("(max-width:1024px)")` でガード＋リサイズ追従。現在地ナビを色のみ依存から下線＋太字へ。タップ領域拡大（`.qty button`/`.cart-remove` を最小40px）。ghostボタンのコントラスト確保。
- **P1 UX**: カート追加時の**ドロワー自動展開を廃止**（トーストのみ／文言「右上のカートからご確認いただけます」）。回遊（複数商品検討）を阻害しない。
- **P2**: 画面遷移アニメを短縮（`.16s`、reduced-motion時はほぼ無効）。

**検証**: Playwrightで全15サイト合格（全ルートで .view 単一表示・可視h1=1・カート計算正常・autoOpen=false・モバイルinert=true/デスクトップinert=false・noindex・canonical無・ribbon有・pageError 0）。console error は外部地図iframe/画像のTLS失敗（`ERR_CERT_AUTHORITY_INVALID`／ローカル制約・§5既知）のみ。

**見送り項目への着手（2026-06・続き）**
- ✅ **地図iframeのプライバシー/パフォーマンス**（`scripts/uiux_refine2.py`）: Google Maps を「クリックで読み込むファサード」化。表示時に第三者iframeを自動ロードしない。
- ✅ **チェックアウトのインラインエラー**（`scripts/uiux_refine2.py`）: ネイティブ依存を廃し、デザインに馴染むエラー＋`aria-invalid`/`role=alert`、入力時に自動解除。
- ✅ **トークン体系の統一**（`scripts/uiux_tokens.py`）: 第1弾5サイト（udon/mitchan/nagasaki/morioka/minmin）を shadcn系HSLセマンティックトークン（`--primary`/`--accent`/`--background`/`--foreground`/`--border`/`--ring`/`--destructive` 等）を唯一の真実とする構成へ。既存コンポーネントは無改修、旧名（`--indigo` 等）は同色エイリアスとして保持。Playwright計測で**レンダリング色差Δ≤2（HSL丸めのみ・視覚的に等価）**を確認。※旧 `--muted` はテキスト色のため `--muted-foreground` を参照（shadcnの背景用 `--muted` とは別運用）。
- ✅ **ヒーローのレイアウト多様化**（`scripts/uiux_layout.py`）: 全サイト同型を解消し3バリエーションを店ごとに割当て＝**default(中央/実写真ヒーロー3) / hero--minimal(左寄せテキスト先行・6) / hero--split(PCで左テキスト＋右カラーパネル・6)**。
- ✅ **バナー導線のコンテンツ化**（`scripts/uiux_layout.py`）: `banners--text` の4サイト（mitchan/morioka/nagasaki/minmin）の導線を「タイトル＋説明」のコンテンツカードへ（絵文字撤去・ナビとの重複解消）。

**未対応（次セッションの判断事項）**
- **実料理写真**: ユーザー判断で当面「写真準備中」プレースホルダ維持。AI生成は「誤った写真の流用は厳禁」(§4)の趣旨に反するため不採用。実写真は公式取り込み or 撮影ディレクションが前提。
- **セクション順序のバリエーション**（ヒーロー以外の構成多様化）は店ごとの内容依存のため未着手。necessなら個別に。
