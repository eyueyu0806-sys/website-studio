# Page Atelier 運用ドキュメント一式

2026年10月7日版。編集できるWord3冊と、表示確認用のPDF3冊を`pageatelier-operations-kit.zip`にまとめています。顧客情報・正式な運営者情報・銀行情報・認証情報は未記入です。

追加の比較結果は[集客方針の推奨・比較結果（Word）](https://github.com/eyueyu0806-sys/website-studio/raw/refs/heads/main/business/operations/04-acquisition-recommendation.docx)と[PDF](https://github.com/eyueyu0806-sys/website-studio/raw/refs/heads/main/business/operations/04-acquisition-recommendation.pdf)。業種・媒体・予算・接続の判断は、こちらを先に読んでください。既存の3冊のZIPには含めていません。

その後の実装・公開・検証と、本人の接続が必要な残作業は[05 実行結果（Word）](https://github.com/eyueyu0806-sys/website-studio/raw/refs/heads/main/business/operations/05-launch-execution.docx)と[PDF](https://github.com/eyueyu0806-sys/website-studio/raw/refs/heads/main/business/operations/05-launch-execution.pdf)。現在の状態を知るときはこちらを優先します。[集客開始セット](https://github.com/eyueyu0806-sys/website-studio/raw/refs/heads/main/business/marketing/pageatelier-launch-kit.zip)には画像、投稿文、接続手順、空欄管理表を含みます。

## ダウンロード

[Word・PDF一式をダウンロード](https://github.com/eyueyu0806-sys/website-studio/raw/refs/heads/main/business/operations/pageatelier-operations-kit.zip)

| 書類 | PDFページ数 | 内容 |
| --- | --- | --- |
| `01-marketing-automation.docx` | 17 | 集客対象の仮案、記事・SNS・広告、n8n/GitHubの構成、台帳、検査、重複防止、停止・費用・導入手順 |
| `02-delivery-operations.docx` | 15 | 相談、法人の稟議、見積り、契約、素材、2週間工程、修正、QA、承認、入金、公開、納品、連絡文 |
| `03-ai-prompts.docx` | 19 | 共通ルール、案件ブリーフ、相談・制作・検証・公開・集客・引継ぎの35プロンプト |

Wordのナビゲーションウィンドウを使うと各章・プロンプトへ移動できます。プロンプトはテキストとしてコピーできます。PDFは日本語フォントを使って実際に出力し、原文の全段落・表・プロンプトが残り、ページ外の文字がないことを確認しています。

## 起床後の最短ルート

1. 受託の全体像は`02`の「01 今日から使う手順」「05 2週間の制作計画」を読む。
2. 最初の相談が来たら、非公開の案件フォルダを作り、`03`の共通ルール・案件ブリーフ・P01/P02で整理する。
3. 見積り・契約は、上位の`business/`にある最新の空欄ひな形をコピーして使う。2週間の目安と案件ごとの確定日を区別する。
4. 集客方針は`04`の比較結果から、対象業種・SNS1媒体・月額許容額・記事/計測の追加範囲を決める。
5. アカウント接続と初期ルールが揃ったら、`01`の「10 導入の順番」「13 実装担当者向けの設定表」で導入する。

`01`は前夜の仮案です。追加の`04`では、小規模リフォーム・外構施工会社を主力候補、売却・管理特化の不動産会社を次点に推奨しています。自動化の本体もGitHub Actionsを先に検討し、n8nは業務連携が増えてから再評価します。どちらも未採用の提案で、対象業種・媒体・費用は所有者が判断できます。物件検索DB等を標準料金に含めません。

## 完了したもの・未導入のもの

LINEへのリンクは公開サイトの全3ボタンに接続済みです。友だち追加・相談の実受信・返信・通知は本人のスマホで確認してください。

`01`〜`03`は設計と手順の書類です。その後、業種ページ・4記事の公開とワークフロー登録まで実施しました。GA4、週次記事公開、SNS配信、AI生成、広告は接続が残っています。通常の記事公開と未接続の自動配信を区別します。外部への営業連絡・SNS投稿・広告課金は実行していません。最新の実行状態は`05`を参照してください。

通常の記事は合意した品質ゲートで予約公開でき、料金・顧客実績・契約・予算の変更等は確認へ送る設計です。受託の契約・実入金・公開承認はAIの推定で代用しません。

## 保存・編集

このフォルダは空欄の運用ひな形だけを保存する編集用です。GitHub Pagesには配信しません。記入済みの契約・案件ブリーフ・顧客の素材や相談・口座・秘密情報はリポジトリ外の非公開フォルダへ保存してください。

元の本文は同名のMarkdownです。`generate_documents.py`がWordを生成します。再生成にはPythonと`python-docx`、PDF確認には日本語フォントとLibreOffice等が必要です。Wordで直接編集した内容は、スクリプトを再実行すると上書きされるため、元Markdownか非公開コピーを編集してください。

書体はNoto Sans CJK JP/Noto Serif CJK JP。端末にない場合、Wordの表示や改ページが変わることがあります。配布する確定版はその端末でPDFに出力して確認してください。

現在の料金と条件は`PRICING.md`・`commerce.html`・`business/README.md`と合わせています。実際の取引は記入済みの契約・見積書・別紙と双方の合意を基準にします。運用書の更新で締結済み契約を自動変更しません。
