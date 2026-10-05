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
| `DEPLOYMENT.md` | 公開、メール受信、Search Consoleの設定記録 |
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

公開対象は `index.html`、`assets/`、`CNAME`、`robots.txt`、`sitemap.xml`、`.nojekyll` です。Search ConsoleのHTMLファイルで確認する場合は、その確認用ファイルも公開します。確認画像や運用資料は配信に含めません。

公開後は、HTTPS応答・同梱画像とフォント・シミュレーション・フォームを確認します。メール送信の検証は応答を差し替えた画面テストと、所有者による実受信確認を区別してください。

具体的なドメイン設定と受信確認状況は [DEPLOYMENT.md](DEPLOYMENT.md) を参照してください。
