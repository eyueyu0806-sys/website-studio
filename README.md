# 専門サイト工房 / pageatelier.jp

公開サイト: https://pageatelier.jp/

## 編集用の保存先

最新版のソースは、このリポジトリの `main` ブランチに保存します。これまでの `design/editorial-first-view-20261004` ブランチには制作過程の履歴が残っています。

| ファイル | 内容 |
| --- | --- |
| `index.html` | ページ構成、スタイル、シミュレーション、問い合わせフォーム |
| `assets/` | 同梱フォント、ライセンス、プレビュー画像 |
| `CNAME` | 独自ドメイン |
| `robots.txt` / `sitemap.xml` | 検索エンジン向けの案内 |
| `operator.html` / `commerce.html` / `privacy.html` | 運営者情報・取引条件・プライバシーのページ |
| `assets/legal.css` | 上記3ページ共通のフレーム・罫線・タイポグラフィ |
| `DEPLOYMENT.md` | 公開、メール受信、Search Consoleの設定記録 |
| `PRICING.md` | 基本料金・標準範囲・追加費用・見積り時の確認事項 |
| `PORTFOLIO.md` | 制作サンプル・自主制作・受託案件の区分、画面と許可の扱い |
| `LAUNCH-CHECKLIST.md` | LINE接続、非公開書類、検索掲載、反響対応など残りの作業 |
| `business/` | 個人情報未記入の見積書・制作契約書・任意サポート申込書。記入済み書類は非公開で別に保管 |
| `business/operations/` | 集客自動化設計・受託から納品の手順・35本のAIプロンプト・業種/媒体/予算/接続の比較結果。Word/PDF付き |
| `design-preview/` | デザインの確認画像。公開ファイルには含めません |

今後このチャットで編集を依頼する場合は、`eyueyu0806-sys/website-studio` の `main` を指定してください。GitHubには変更履歴が残るので、以前の状態を参照できます。

## 開発

依存パッケージやビルドは不要です。リポジトリのルートで静的HTTPサーバーを起動します。

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

サイト制作体験はルールベースです。編集時は業種・目的・機能の選択、屋号、生成結果、プレビュー、相談への構成添付を維持してください。

## 公開

GitHub Pagesは `gh-pages` ブランチのルートを配信します。`main` に保存する操作と公開する操作は別です。

公開対象は `index.html`、`assets/`、`CNAME`、`robots.txt`、`sitemap.xml`、`.nojekyll` です。運営者情報等の3ページを公開する際は `operator.html`、`commerce.html`、`privacy.html` も含めます。運営者の正式情報そのものはリポジトリへ保存しません。開示対応と外部サービスの取扱いの記録は [drafts/legal/README.md](drafts/legal/README.md) を参照してください。Search ConsoleのHTMLファイルで確認する場合は、その確認用ファイルも公開します。確認画像や運用資料は配信に含めません。

公開後は、HTTPS応答・同梱画像とフォント・シミュレーション・フォームを確認します。メール送信の検証は応答を差し替えた画面テストと、所有者による実受信確認を区別してください。

具体的なドメイン設定と受信確認状況は [DEPLOYMENT.md](DEPLOYMENT.md) を参照してください。
