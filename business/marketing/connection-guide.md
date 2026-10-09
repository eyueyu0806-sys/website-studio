# 本人の操作が必要な接続

2026年10月8日更新。業種を限定しない方針へ変更。サイトと記事は公開済み。GA4作成と測定ID `G-64G59Z1ERS` は本人の画像で確認済み。本人から拡張計測機能オフの回答を受け、同意後のみの計測を有効にした。クラウド実行環境のAI/Instagram認証情報は未設定です。GitHubのSecrets/Variables一覧の参照は現連携がHTTP 403のため、本人がActionsへPUBLICATION_TOKENを保存した。2026年10月7日の手動テストで、トークンの認証とmain/gh-pagesへの変更なしのpush検査が成功。APIキーやトークンをチャットに貼らないでください。

## 1. GA4：最初に行う

1. https://analytics.google.com/ を本人のGoogleアカウントで開く。「測定を開始」または管理画面からアカウント・プロパティを作成する。名称は `Page Atelier`、タイムゾーンは日本、通貨は円を候補にする。
2. Webデータストリームを作成し、URLは `https://pageatelier.jp` にする。
3. **拡張計測機能はオフ**にする。今回のサイトはページ閲覧と必要な操作をコードから送る構成で、フォームやリンクの自動収集は使わない。
4. `G-...` の測定IDを取得する。IDは公開用の設定値なので、このチャットで知らせても構わない。Googleのパスワードや認証コードは送らない。
5. `assets/site-config.js` の `ga4MeasurementId` を設定し、拡張計測機能オフを確認後に `ga4Enabled` をtrueとして保存・公開する。今回は本人のIDと回答から実施済み。
6. 公開サイトで解析への同意を選び、GA4のリアルタイムで閲覧を確認する。同意しない／同意撤回でも制作体験とフォームが使えることを確認する。コードの接続試験は応答を差し替えた検証。その後、本人からGA4管理画面でアクセスを確認できたと報告を受けた。操作イベントごとの管理画面受信は別途確認。
7. `generate_lead` はフォームサービスの成功応答で送るイベント。GA4でキーイベントに指定する場合も、実受信や有効相談・契約とは別に扱う。`line_click` を問い合わせ完了として数えない。

## 2. 自動公開用GitHub接続（接続テスト済み）

2026年10月8日追記：同日のrun 37733773555ではPUBLICATION_TOKENがなく公開をスキップしていたため、本人がRepository Secretへ再保存。[再確認run 37759574387](https://github.com/eyueyu0806-sys/website-studio/actions/runs/37759574387)で認証とmain/gh-pagesへのpush dry-runが成功。公開ファイルは既に最新で、新規投稿はなかった。今後はSecret欠落を成功扱いにせず、Actionsに失敗として表示する。

1. https://github.com/settings/personal-access-tokens/new でFine-grained personal access tokenを作成。実際の画面で本人のResource ownerと `website-studio` のみを選ぶ。
2. Repository permissionsの **Contents: Read and write** を設定する。Metadataは必要な読み取り。今回の公開処理にSecrets管理・顧客データ・他のリポジトリへの権限は不要。組織の承認が必要な場合はその正式な手順を使う。
3. 期限と失効時の交換日を非公開メモへ残す。期限切れのときは自動公開を止め、トークンの無期限運用を前提にしない。
4. https://github.com/eyueyu0806-sys/website-studio/settings/secrets/actions を開き、New repository secretで名前 **PUBLICATION_TOKEN** として保存する。値はこの管理画面だけへ入力する。
5. https://github.com/eyueyu0806-sys/website-studio/actions の `Release reviewed content` → Run workflowで初回確認する。公開日より前なら公開対象なしになる。
6. 記事公開は毎日09:00日本時間の予約と12:00の再確認、1日最大1本。GitHubの実行は遅延する場合がある。10月8日〜21日の確認済み記事14本を用意した。公開済みの4記事とは別。
7. 処理はmainへ記事を保存し、公開対象のみgh-pagesへ反映する。Pagesのビルドと公開URLが正常かを確認する。公開済みの同じ記事は再度キューから出ない。

2026年10月7日の[接続テストrun 37627676705](https://github.com/eyueyu0806-sys/website-studio/actions/runs/37627676705)はsuccess。トークンによる認証、main/gh-pagesへのpush dry-run、10 HTML・30公開ファイルの検査を確認した。当日は公開期日前のため予約キューを維持し、新記事の保存・本番pushは行っていない。毎日運用に変更し、初回の実予約公開は10月8日09:00日本時間の枠以降。GitHubの実行は遅れる場合がある。トークン期限は画面から本人が非公開で記録し、期限前に同じSecretの値を交換する。

このトークンはGitHub Actions側の設定です。クラウド環境設定に保存しただけではActionsへ移りません。現在のGitHub連携の認証情報を取り出して流用することもしません。

## 3. Instagram：公式経路で接続

1. 本人のInstagramを事業用のプロフェッショナルアカウントへ設定する。表示名候補は「サイト工房｜Page Atelier」。ユーザーネームは本人申告の `pageatelier.jp`。Instagramプロフィールは `https://www.instagram.com/pageatelier.jp/`、プロフィールの外部リンクは `https://pageatelier.jp/?utm_source=instagram&utm_medium=social&utm_campaign=studio_launch`。業種限定の紹介文は使わず、[最新プロフィール・集客方針](all-industries-plan.md)を参照。
2. 自動投稿は **Instagram API with Instagram Login** を使用する案。公式資料ではBusinessまたはCreatorアカウントが対象。この経路と、Facebook Page連携が必要なFacebook Login経路を混同しない。
3. https://developers.facebook.com/documentation/instagram-platform/instagram-api-with-instagram-login の正式なアプリ設定・OAuth手順に従い、本人のアカウントを許可する。権限は `instagram_business_basic` と `instagram_business_content_publish`。標準／上位アクセス、アプリのモードや審査の要否は本人の利用形態で確認する。
4. 自動投稿に必要なアカウントID、対象APIバージョン、アクセストークンを取得する。トークンとその期限は非公開で管理。
5. 同じGitHub設定のSecretsに **INSTAGRAM_ACCESS_TOKEN**、Variablesに **INSTAGRAM_ACCOUNT_ID** と **INSTAGRAM_API_VERSION** を保存する。公式の取得済み公開資料の例は `v25.0`。これが常に最新だと決めつけず、アプリで利用可能な版を確認する。
6. 投稿JPEGは `assets/marketing/`、投稿文は `business/marketing/social-posts.json`。確認済み14件を10月8日〜21日の毎日枠へ用意した。10:00と18:00に準備を確認し、最大1日1件だけ送る。対応する記事が公開済みでなければ延期し、公開可能日より前には送らない。
7. `Publish reviewed Instagram post` を初回実行して、投稿ID・画像・本文をInstagram本体で確認する。現在は実投稿未確認。送信結果不明の記録がある投稿を、確認せず再実行しない。

Metaが画像を取得できる公開HTTPSのJPEGを使います。公式公開資料でJPEGのみ対応と確認したためPNGを送る実装にはしていません。権限・認証期限・画像取得・実投稿の全確認後に接続完了とします。

## 4. AI API：初期公開には必須ではない

公開済み4記事と14本の予約記事にはAIのAPI接続は不要。原稿の追加生成を使う場合だけ接続します。

1. 本人のOpenAI APIアカウントでプロジェクト・請求設定・現在のモデル価格を確認する。ChatGPTの月額契約とは別の課金。
2. GitHub Secretsに **OPENAI_API_KEY**、Variablesに **OPENAI_MODEL** を保存する。モデルは本人のアカウントで使える、構造化出力対応の文章用モデルを実単価から選ぶ。
3. API予算は月2,000円以内を事業側の枠とする。ダッシュボードの予算が通知だけかを確認し、厳密な支出停止と同一視しない。スクリプトは月4回まで、1回最大4,500出力トークン、再試行なし。モデルによってはこの回数でも枠を超えるので、単価確認前に動かさない。
4. `Create article draft (no publication)` の手動実行で下書きを作る。公開情報だけを入力し、顧客の相談全文や秘密情報を送らない。
5. 原稿の事実・価格・納期・重複・権利・独自の判断材料を確認し、合格したものを `content/journal/` の予約キューへ移す。AI出力は自動で承認済みにしない。日常の原稿確認は次の作業でこちらが行える。

## 5. LINEと受信確認

`https://lin.ee/VZsDkE9` のサイト導線は接続済み。本人のスマホで友だち追加、あいさつ、受信、返信、通知を確認します。10月8日に変更した `yue.sadamatsu@gmail.com` への問い合わせ到着は本人確認済みです。迷惑メールと通知も確認してください。

## 6. 検索掲載と広告

Search Consoleでトップ・業種ページ・記事のURL検査、サイトマップ `https://pageatelier.jp/sitemap.xml` の送信状態を確認。リクエスト済みとインデックス済みは別です。

広告は、実受信・GA4着信・有効相談の記録・業種ページが確認できてから。`google-ads-draft.md`に草案を保存。Google広告の本人の請求・期間・予算設定と実際の検索数・単価を確認するまで出稿しません。GA4から広告への計測連携は未実装・未検証です。

毎日運用のテーマ・品質確認・継続方法は[daily-publishing-plan.md](daily-publishing-plan.md)を参照。

## 2026年10月8日の方針・原稿更新

業種を限定しない記事・投稿14本へ置き換え。10月8日分1本を公開対象へ移し、残り13本を予約。Instagramは @pageatelier.jp と本人申告。プロフィールの外部リンクは総合トップへ変更する。アカウントのビジネス化・API接続・実投稿は未確認。

## 問い合わせメール変更（2026-10-08）

サイト・法務ページ・配布書類の窓口は `yue.sadamatsu@gmail.com` へ統一。Instagramの公開メール、Metaアプリの連絡先、LINE管理画面の通知メールは本人の画面で変更を確認する。Google・GitHub等のログインアカウントを自動的に移行する変更ではない。LINEのトークは引き続きLINEで受信し、Gmailへの自動転送は設定していない。

## 受付メール（準備済み・接続待ち）

本人が自動返信文面を承認。Resend・Cloudflareは作成済み。Turnstileウィジェットを作成し、Site Keyを保存。TURNSTILE_SECRET_KEYのGitHub保存は本人報告済み（接続は未検証）。手順は [問い合わせ配信の接続](../../integrations/contact/README.md)。コード・PC/スマホでの応答差替テストは準備済み。現行FormSubmitを維持し、受付メールの実送信は未実施。

## 自動点検（2026年10月9日追加）

[Check automation health](https://github.com/eyueyu0806-sys/website-studio/actions/workflows/automation-health.yml) が日本時間15:30に点検します。実行はGitHubの都合で遅れる場合があります。各実行のSummaryで、翌日から7日間の原稿在庫、当日記事、Instagram未確定記録、GitHubの認証・書き込み権限、公開ページ、接続設定の有無、Resend用DNSを確認できます。

原稿不足・期限切れ等の認証失敗・公開不備は失敗として表示します。まだ設定していないInstagramと、未有効化の自動返信は「接続待ち」と表示し、他の作業を止めません。Instagramの設定が存在するだけで実投稿成功とは判定しません。実メール・SNS投稿はこの点検では送信しません。失敗通知の受信は本人のGitHub通知設定に依存します。
