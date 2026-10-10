# 自動化の進行管理

最終確認：2026年10月10日、日本時間21:21。最新の稼働状況は [毎日の点検](https://github.com/eyueyu0806-sys/website-studio/actions/workflows/automation-health.yml) のSummaryを参照。

## 進め方

本人操作が必要な作業を待ち事項として分離し、独立して実装・検証・公開できる作業を先に進める。接続待ちや未実施を「完了」と扱わない。認証情報はGitHubのSecrets/Variablesへ本人が保存し、チャットやソースには置かない。新たな有料サービス契約・広告費の支出、本人しかできない認証が必要なときは、その操作だけ依頼する。

## 稼働・検証済み

- 記事公開：毎日09:00＋12:00再確認、1日最大1本。GitHubによる遅延あり。10月9日の飲食店記事を [run 37890168118](https://github.com/eyueyu0806-sys/website-studio/actions/runs/37890168118) で公開し、HTTPS 200とcanonicalを確認。予約記事は10月10日〜21日の12本。
- 自動点検：毎日15:30。7日間の原稿在庫、当日記事、未確定投稿、公開URL、GitHub認証、接続設定、DNSを確認。読み取り専用で投稿・メール送信は行わない。点検が失敗しても記事公開ワークフローを止めない。
- [点検run 37890726169](https://github.com/eyueyu0806-sys/website-studio/actions/runs/37890726169)：記事在庫、公開ページ、GitHub書き込み権限の応答は正常。Instagramと自動返信は接続待ち。
- サイト：料金・プラン相談・構成添付・失敗時の別窓口を改善済み。1440/1200/390pxで検証。現行のFormSubmit窓口を維持。

## 本人操作待ち（他の作業の停止理由にしない）

1. **自動返信の接続状態**：pageatelier.jpのDNS3レコード、Resend APIキー、Cloudflare Account ID、Turnstileの設定はそろった。Worker公開と秘密情報2件の登録は [run 38051445785](https://github.com/eyueyu0806-sys/website-studio/actions/runs/38051445785) で成功。公開URLは `https://pageatelier-contact.pageatelier-020acba5.workers.dev/contact`。
2. **HTTPS接続待ち**：新規workers.devアドレスを登録済み。ただし公開エンドポイントの接続確認は [run 38051542545](https://github.com/eyueyu0806-sys/website-studio/actions/runs/38051542545) で失敗。このため公開フォームはFormSubmitを維持。メールの実受信・自動返信到達は未確認。接続が回復したらOPTIONS 204、無効POST 400を確認し、公開説明と経路を同時に切り替えて本人の実受信テストへ進む。
3. **実装検証**：Workerの11テストに合格。模擬受付サービスを使い1440/1200/390pxでプラン、構成添付、入力保持、再送、JavaScriptエラー・横はみ出しを確認。模擬テストは実メールを送らない。
4. **Instagram**：本人のMetaアプリ設定とInstagram Loginの接続。Secret `INSTAGRAM_ACCESS_TOKEN`、Variables `INSTAGRAM_ACCOUNT_ID` / `INSTAGRAM_API_VERSION`が未設定。画像・文章14件を用意済み。実投稿・アクセストークン有効性は未確認。

## 次にこちらで進める作業

- 次の7〜14日分の原稿・投稿素材の制作と内容確認。原稿残数だけでなく配信可能日を確認する。未確認のAI下書きを自動承認しない。
- 自動返信用の公開説明を公式資料と照合。Resendの主体・米国処理・保持の基準を確認済み。Cloudflareのプライバシーポリシー・Customer DPA・Turnstile方針も10月10日に取得して照合済み。詳細は `integrations/contact/privacy-migration.md`。
- 本人の接続設定が届いたら毎日の点検を再実行し、該当箇所の実接続を確認。既存の作業・確認を最初からやり直さない。
- 実際の流入・相談数が蓄積したら、固定ラベルの計測と実受信を照合して改善。架空の口コミ・実績・受注件数を追加しない。顧客情報を公開GitHubへ保存しない。
