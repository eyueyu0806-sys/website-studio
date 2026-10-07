# 本人の操作が必要な接続

2026年10月7日。サイトと記事は公開済み。GA4作成と測定ID `G-64G59Z1ERS` は本人の画像で確認済み。本人から拡張計測機能オフの回答を受け、同意後のみの計測を有効にした。クラウド実行環境のAI/Instagram認証情報は未設定です。GitHubのSecrets/Variables一覧の参照は現連携がHTTP 403のため、本人がActionsへPUBLICATION_TOKENを保存した。2026年10月7日の手動テストで、トークンの認証とmain/gh-pagesへの変更なしのpush検査が成功。APIキーやトークンをチャットに貼らないでください。

## 1. GA4：最初に行う

1. https://analytics.google.com/ を本人のGoogleアカウントで開く。「測定を開始」または管理画面からアカウント・プロパティを作成する。名称は `Page Atelier`、タイムゾーンは日本、通貨は円を候補にする。
2. Webデータストリームを作成し、URLは `https://pageatelier.jp` にする。
3. **拡張計測機能はオフ**にする。今回のサイトはページ閲覧と必要な操作をコードから送る構成で、フォームやリンクの自動収集は使わない。
4. `G-...` の測定IDを取得する。IDは公開用の設定値なので、このチャットで知らせても構わない。Googleのパスワードや認証コードは送らない。
5. `assets/site-config.js` の `ga4MeasurementId` を設定し、拡張計測機能オフを確認後に `ga4Enabled` をtrueとして保存・公開する。今回は本人のIDと回答から実施済み。
6. 公開サイトで解析への同意を選び、GA4のリアルタイムで閲覧を確認する。同意しない／同意撤回でも制作体験とフォームが使えることを確認する。コードの接続試験は応答を差し替えた検証。その後、本人からGA4管理画面でアクセスを確認できたと報告を受けた。操作イベントごとの管理画面受信は別途確認。
7. `generate_lead` はフォームサービスの成功応答で送るイベント。GA4でキーイベントに指定する場合も、実受信や有効相談・契約とは別に扱う。`line_click` を問い合わせ完了として数えない。

## 2. 自動公開用GitHub接続（接続テスト済み）

1. https://github.com/settings/personal-access-tokens/new でFine-grained personal access tokenを作成。実際の画面で本人のResource ownerと `website-studio` のみを選ぶ。
2. Repository permissionsの **Contents: Read and write** を設定する。Metadataは必要な読み取り。今回の公開処理にSecrets管理・顧客データ・他のリポジトリへの権限は不要。組織の承認が必要な場合はその正式な手順を使う。
3. 期限と失効時の交換日を非公開メモへ残す。期限切れのときは自動公開を止め、トークンの無期限運用を前提にしない。
4. https://github.com/eyueyu0806-sys/website-studio/settings/secrets/actions を開き、New repository secretで名前 **PUBLICATION_TOKEN** として保存する。値はこの管理画面だけへ入力する。
5. https://github.com/eyueyu0806-sys/website-studio/actions の `Release reviewed content` → Run workflowで初回確認する。公開日より前なら公開対象なしになる。
6. 記事公開は月曜09:00日本時間の予約。GitHubの実行は遅延する場合がある。10月12日、19日の確認済み記事を各1本用意した。公開済みの4記事とは別。
7. 処理はmainへ記事を保存し、公開対象のみgh-pagesへ反映する。Pagesのビルドと公開URLが正常かを確認する。公開済みの同じ記事は再度キューから出ない。

2026年10月7日の[接続テストrun 37627676705](https://github.com/eyueyu0806-sys/website-studio/actions/runs/37627676705)はsuccess。トークンによる認証、main/gh-pagesへのpush dry-run、10 HTML・30公開ファイルの検査を確認した。当日は公開期日前のため予約キューを維持し、新記事の保存・本番pushは行っていない。初回の実予約公開は10月12日09:00日本時間の枠以降。GitHubの実行は遅れる場合がある。トークン期限は画面から本人が非公開で記録し、期限前に同じSecretの値を交換する。

このトークンはGitHub Actions側の設定です。クラウド環境設定に保存しただけではActionsへ移りません。現在のGitHub連携の認証情報を取り出して流用することもしません。

## 3. Instagram：公式経路で接続

1. 本人のInstagramを事業用のプロフェッショナルアカウントへ設定する。表示名候補は「サイト工房｜Page Atelier」。ハンドル `pageatelier_studio` の空きは未確認。プロフィールURLは `https://pageatelier.jp/for-builders.html?utm_source=instagram&utm_medium=social&utm_campaign=builders_launch`。
2. 自動投稿は **Instagram API with Instagram Login** を使用する案。公式資料ではBusinessまたはCreatorアカウントが対象。この経路と、Facebook Page連携が必要なFacebook Login経路を混同しない。
3. https://developers.facebook.com/documentation/instagram-platform/instagram-api-with-instagram-login の正式なアプリ設定・OAuth手順に従い、本人のアカウントを許可する。権限は `instagram_business_basic` と `instagram_business_content_publish`。標準／上位アクセス、アプリのモードや審査の要否は本人の利用形態で確認する。
4. 自動投稿に必要なアカウントID、対象APIバージョン、アクセストークンを取得する。トークンとその期限は非公開で管理。
5. 同じGitHub設定のSecretsに **INSTAGRAM_ACCESS_TOKEN**、Variablesに **INSTAGRAM_ACCOUNT_ID** と **INSTAGRAM_API_VERSION** を保存する。公式の取得済み公開資料の例は `v25.0`。これが常に最新だと決めつけず、アプリで利用可能な版を確認する。
6. 投稿JPEGは `assets/marketing/`、投稿文は `business/marketing/social-posts.json`。確認済み4件を月曜／木曜09:00の枠へ用意した。公開可能日より前には送らない。
7. `Publish reviewed Instagram post` を初回実行して、投稿ID・画像・本文をInstagram本体で確認する。現在は実投稿未確認。送信結果不明の記録がある投稿を、確認せず再実行しない。

Metaが画像を取得できる公開HTTPSのJPEGを使います。公式公開資料でJPEGのみ対応と確認したためPNGを送る実装にはしていません。権限・認証期限・画像取得・実投稿の全確認後に接続完了とします。

## 4. AI API：初期公開には必須ではない

確認済み4記事と2本の予約記事にはAIのAPI接続は不要。原稿の追加生成を使う場合だけ接続します。

1. 本人のOpenAI APIアカウントでプロジェクト・請求設定・現在のモデル価格を確認する。ChatGPTの月額契約とは別の課金。
2. GitHub Secretsに **OPENAI_API_KEY**、Variablesに **OPENAI_MODEL** を保存する。モデルは本人のアカウントで使える、構造化出力対応の文章用モデルを実単価から選ぶ。
3. API予算は月2,000円以内を事業側の枠とする。ダッシュボードの予算が通知だけかを確認し、厳密な支出停止と同一視しない。スクリプトは月4回まで、1回最大4,500出力トークン、再試行なし。モデルによってはこの回数でも枠を超えるので、単価確認前に動かさない。
4. `Create article draft (no publication)` の手動実行で下書きを作る。公開情報だけを入力し、顧客の相談全文や秘密情報を送らない。
5. 原稿の事実・価格・納期・重複・権利・独自の判断材料を確認し、合格したものを `content/journal/` の予約キューへ移す。AI出力は自動で承認済みにしない。日常の原稿確認は次の作業でこちらが行える。

## 5. LINEと受信確認

`https://lin.ee/VZsDkE9` のサイト導線は接続済み。本人のスマホで友だち追加、あいさつ、受信、返信、通知を確認します。Gmailの実受信は本人の確認済みですが、今後も迷惑メールと通知を確認してください。

## 6. 検索掲載と広告

Search Consoleでトップ・業種ページ・記事のURL検査、サイトマップ `https://pageatelier.jp/sitemap.xml` の送信状態を確認。リクエスト済みとインデックス済みは別です。

広告は、実受信・GA4着信・有効相談の記録・業種ページが確認できてから。`google-ads-draft.md`に草案を保存。Google広告の本人の請求・期間・予算設定と実際の検索数・単価を確認するまで出稿しません。GA4から広告への計測連携は未実装・未検証です。
