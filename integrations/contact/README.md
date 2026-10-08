# 問い合わせ＋受付メール（接続準備済み・未稼働）

2026-10-08。ユーザー承認の受付メールを実装。Resendアカウントは作成済みとの本人回答。Cloudflareアカウントは未作成。メール配信の実接続・送信元認証・実受信は未確認。現行サイトはFormSubmitのままで、受付メールを送ると表示しない。

## 送る2通

1. 運営者 `yue.sadamatsu@gmail.com`：氏名、返信先、業種、相談本文、添付したサイト構成、固定値の流入元、同意記録。返信先は相談者。
2. 相談者の入力アドレス：定型のお礼・受付番号・追加相談の案内。返信先は `yue.sadamatsu@gmail.com`。氏名・相談本文・リンクなどの自由入力を転載しない。

送信元は `Page Atelier <contact@pageatelier.jp>`。このアドレスのGmail受信箱を新規作成する必要はない。Resendに登録したドメインから送信し、返信は既存Gmailへ届くようReply-Toを指定する。ユーザーが承認した文面はworker.mjsのRECEIPT。

## 本人の初期操作

1. https://dash.cloudflare.com/sign-up で本人のCloudflareアカウントを作る。Webサイト・ネームサーバーをCloudflareへ移す必要はない。公開サイトはGitHub Pagesのまま。
2. https://resend.com/domains で `pageatelier.jp` の状態を確認。未登録なら追加し、表示された送信認証用DNSレコードをお名前.comへ設定する。値はResendの実画面を使う。既存のWeb公開用A/CNAME、メール受信用MX、既存SPFを無断で削除・置換しない。指定されるレコード名がサブドメインなら、その名前へ追加する。Verified表示まで確認する。
3. Resendで、この送信ドメインに限定したSending accessのAPIキーを作る。本人がGitHub Actions Secret `RESEND_API_KEY` へ保存する。チャット・リポジトリには貼らない。既に別サイトのキーがある場合も、それを公開したり取り出して共有しない。
4. CloudflareのTurnstileでウィジェットを作成。ホスト名は `pageatelier.jp`、モードManaged。サイトキーは公開用、秘密キーはGitHub Secret `TURNSTILE_SECRET_KEY`。サイトキーだけはチャットで共有できる。
5. CloudflareのWorker公開用接続を行う。アカウントIDはGitHub Variable `CLOUDFLARE_ACCOUNT_ID`。APIトークンは対象アカウントのWorkerスクリプト編集に必要な権限に限定し、Secret `CLOUDFLARE_API_TOKEN`へ保存する。実際の画面と不足権限エラーを確認し、DNS全体編集や他アカウントへの権限を追加しない。
6. GitHub Actionsの `Deploy contact receipt service` を手動実行。既存のPUBLICATION_TOKENは使わない。Workerコード公開と、Cloudflare側の2つのシークレット設定を行う。サイトの送信先は自動で切り替えない。

アカウントの作成・サービス接続時は、本人の契約・利用枠・課金設定を確認する。新たな有料プランや広告費の支出は行っていない。40受付/日というアプリ側の枠は、プロバイダの無料枠や料金を保証するものではない。

## ローカル検証／公開方法

```
cd integrations/contact
npm ci
npm run check
```

Wrangler 4.148.0をpackage-lock.jsonで固定。Webサイト本体にnpm依存を追加する変更ではない。

本人がCLIを利用する場合は、Cloudflareへ正式にログインして `npm run deploy`、続いて `npx wrangler secret put RESEND_API_KEY` と `npx wrangler secret put TURNSTILE_SECRET_KEY`。値は対話入力する。公開URLの末尾 `/contact` をサイト側へ設定する。シークレットがない間は503で拒否する。

## 稼働を切り替える前の必須確認

- Resendで `pageatelier.jp` がVerified、Workerの設定と2つのシークレット、Turnstileのホスト名を確認。
- 公開フォームとprivacy.htmlの送信先説明をFormSubmitからCloudflare・Resendに更新する。実際の契約主体・処理地域・保持・委託条件・国外提供の案内を両サービスの最新資料と管理画面で照合してから公開する。既存の「FormSubmitが30日保存」の説明を新経路へ流用しない。変更用たたき台はprivacy-migration.md。
- assets/site-config.js：contactModeをresend、contactEndpointを実WorkerのHTTPS URL＋/contact、turnstileSiteKeyを実サイトキー、contactPolicyVersionを2026-10-08-resendへ設定。秘密キーはここに置かない。
- PC1440・1200・スマホ390で、Turnstile・構成添付・同意・送信・成功・通信失敗・再試行を確認。
- 本人のテスト用アドレスで実送信し、運営者メールと受付メールの両方を確認する。受付メールへ返信して、新しいGmailに着くことを確認する。Resendのacceptedと受信箱への到着は別。
- 本人の確認後に本番切替完了を記録する。外部接続がない現状では完了としない。

## 再送・制限・記録

- 入力検証、48KB上限、固定Origin、Turnstileのサーバー検証（hostnameとactionも確認）、エッジでIPごと5回/分。Originだけを認証として扱わない。
- 全体でUTC日付ごと40個の送信バッチ、同一送信先メールは3個/日。日本時間では午前9時が日付境界。過去の未確定処理の再試行もその日の枠へ数える。同じIDはその日の枠を重複消費しない。各バッチは2通。管理者への通知もAPI利用枠に含む。
- ブラウザは受付ID、入力のハッシュ、最初の同意時刻だけをsessionStorageへ保存し、同じ内容の再試行ではIDを維持する。本文・氏名・メール自体は保存しない。ストレージ拒否時はページ内メモリで維持する。
- Durable Objectは受付内容のハッシュ・時刻・送信状態・プロバイダのメールIDだけを記録。本文・氏名・メールは永続化しない。受付記録は30日、制限用のメールアドレスのハッシュは最後の更新から2日で削除する。Cloudflare/Resend自身の処理・保持、運営者Gmailの保持とは別。
- 同一IDの処理を直列化。2通をResendの一つのバッチにし、Idempotency-Keyを固定する。提供元の有効期間は24時間。送信結果不明のものは23時間を過ぎたら自動的に再送せず、運営者がResendログで確認する。30日後に記録が消えても古い同意日時のリクエストを新規扱いで送らない。
- 通信失敗時にFormSubmitへ自動転送しない。二重送信を避け、入力を保持して同じ受付IDで再確認する。
- 受付メールで受信者の存在を確認したことにはならない。本文を転載しない設計により、メールの入力間違いや第三者のアドレス指定時に相談の内容を送らない。
- アプリは本文・秘密キー・プロバイダ応答をログ出力しない。WorkerのObservabilityは無効。運用時も本文をログへ追加しない。

## 根拠と確認状況

- FormSubmit：AJAXとreCAPTCHA無効時は自動返信に非対応。https://formsubmit.co/documentation
- Resendバッチ・24時間のIdempotency-Key：https://resend.com/docs/api-reference/emails/send-batch-emails
- Turnstileはサーバー検証が必要、トークンは5分・1回限り：https://developers.cloudflare.com/turnstile/get-started/server-side-validation/
- CloudflareのエッジRate Limit：https://developers.cloudflare.com/workers/runtime-apis/bindings/rate-limit/
- これらの仕様は2026-10-08に取得して確認。ローカルの外部応答を差し替えた検証と、実サービスでの配信は区別する。

## 今回の検証記録

2026-10-08：外部送信なしのNodeテスト11件、1440/1200/390pxで構成添付・受付表示・同一IDでの再試行・入力保持・JavaScriptエラーなしを確認。現行FormSubmit経路でも同3幅の送信・同意・成功/失敗・添付・再試行を確認し、Turnstileを読み込まないことを確認。Wranglerのビルド、実際のローカルWorkersランタイム起動、CORS事前確認204・別Origin403・認証情報未設定503を確認。これらは本番のドメイン認証・実メール配信・受信を確認したものではない。
