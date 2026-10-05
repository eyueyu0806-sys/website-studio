# pageatelier.jp

完成版の公開先は GitHub Pages、独自ドメインは `pageatelier.jp` です。

編集用の最新版は `main` ブランチ、配信ファイルは `gh-pages` ブランチです。今後の編集は `main` から開始します。`main` への保存だけでは公開内容は更新されないため、確認後に公開対象のファイルを `gh-pages` へ反映します。

公開ファイルは `gh-pages` ブランチにあります。ルートの `CNAME` に独自ドメインを指定しています。ドメインはお名前.comで取得済みです。2026年10月5日に独自ドメインのHTTPS応答、公開HTMLとテスト済み完成版の一致、`www.pageatelier.jp` から正規URLへの転送を確認しました。所有者が `Enforce HTTPS` を有効にし、HTTPからHTTPSへの301転送とHTTPSの200応答を確認済みです。GitHub PagesのAPIでも `https_enforced: true`、ルートと `www` の証明書が `approved` であることを確認しました。

## 問い合わせ

受信先は `eyu.eyu0806@gmail.com` です。フォームはFormSubmitのAJAXエンドポイントへ送信し、メールアプリへの切り替えなしでサイト内に結果を表示します。相談者の名前・返信先メールアドレス・業種・相談内容・シミュレーションで作成した構成を送ります。構成の添付は外すこともできます。通信失敗時は入力内容を保持し、処理中の二重送信を防ぎます。

結果の「この内容で無料相談する」は、構成を添付してフォームの先頭へ直接スクロールします。移動先をセクション全体から入力フォームへ変更し、モバイルでも入力欄が画面内に収まることを確認しました。送信中はフォーム入力を保護し、成功時だけクリアします。1440px・1200px・390pxのブラウザ検証では送信サービスの応答を差し替え、成功・失敗・タイムアウト・再試行と送信内容を確認しました。実メールを送るテストとは区別してください。

### 受信先の初回承認（必須）

1. 公開サイトから自分の名前とメールアドレスでテスト問い合わせを送信します。
2. `eyu.eyu0806@gmail.com` に届くFormSubmitの確認メールを開き、受信先を承認します。迷惑メールフォルダも確認してください。
3. 承認後にもう一度テスト送信し、本文とサイト構成がGmailへ届くことを確認します。最初の送信だけで受信完了とは判断しないでください。

2026年10月5日、所有者から初回承認・承認後の再送信・相談内容とサイト構成のGmail受信を確認できたとの報告があり、メール問い合わせの受信確認は完了しました。これは所有者による実受信の確認で、上記のブラウザ検証とは別の証拠です。LINE相談のURLはまだ仮設定です。

公式のAJAX仕様: https://formsubmit.co/ajax-documentation

## ドメインのDNS設定

### お名前.com Navi

1. [お名前.com Navi](https://navi.onamae.com/)へログインします。
2. `pageatelier.jp` のDNS設定を開き、「DNSレコード設定を利用する」へ進みます。
3. 下のレコードを1件ずつ追加します。ルートのホスト名は空欄です。TTLは初期値のままで構いません。
4. 確認画面の「DNSレコード設定用ネームサーバーへ変更する」に相当する項目を確認し、保存します。すでにDNSレコード設定用ネームサーバーを利用している場合は、変更不要です。

| 種類 | 名前 | 値 |
| --- | --- | --- |
| A | 空欄 | 185.199.108.153 |
| A | 空欄 | 185.199.109.153 |
| A | 空欄 | 185.199.110.153 |
| A | 空欄 | 185.199.111.153 |
| CNAME | www | eyueyu0806-sys.github.io |

`www` のCNAMEにはリポジトリ名や `https://` を含めません。MXやメール用TXTなど、サイト接続と関係のないレコードは維持します。ルートの既存レコードが別のサイトを指している場合は、切り替え対象を確認してから変更します。

DNSレコード設定用ネームサーバーは `01.dnsv.jp`、`02.dnsv.jp`、`03.dnsv.jp`、`04.dnsv.jp` です。DNSの反映・証明書の発行には時間がかかる場合があります。

## GitHub Pages

[このリポジトリのPages設定](https://github.com/eyueyu0806-sys/website-studio/settings/pages)で次を指定します。

1. Source: `Deploy from a branch`
2. Branch: `gh-pages`、Folder: `/(root)`、Save
3. Custom domain: `pageatelier.jp`。ブランチの `CNAME` と一致させます。
4. DNSの確認と証明書の発行が完了したら、`Enforce HTTPS` を有効にします。

公開後のURLは `https://pageatelier.jp/` です。`www.pageatelier.jp` も設定した場合は、GitHub Pagesが指定した正規ドメインへ転送します。

DNS、HTTPS証明書、ページ本体、同梱フォント・画像、業種選択、Builderの生成と相談添付を確認してから公開完了とします。

公式手順: [GitHub Pagesの独自ドメイン管理](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)

## Google検索 / Search Console

正規URLは `https://pageatelier.jp/` です。HTMLのcanonicalとWebSite構造化データに同じURLを指定しています。`robots.txt` はクロールを許可し、`sitemap.xml` を案内します。サイトマップには実在するトップページのみを掲載します。セクションのアンカーや、シミュレーション内の架空のサイトを別ページとして登録しません。`lastmod` はページ内容を実際に変更したときに更新してください。

Search Consoleは所有者のGoogleアカウントで登録します。所有者から提供されたHTML確認タグを `index.html` に追加しています。Search Console画面での所有権確認・サイトマップ送信・インデックス登録リクエストは所有者の操作待ちです。

1. [Google Search Console](https://search.google.com/search-console/welcome)へログインします。
2. 「URLプレフィックス」に `https://pageatelier.jp/` を入力します。
3. 所有権確認の「HTMLタグ」を開き、発行されたmetaタグを `index.html` のheadへ追加して公開します。確認タグは以後も削除しません。
4. 公開反映後にSearch Consoleへ戻り、「確認」を押します。
5. 「サイトマップ」に `sitemap.xml` を送信します。
6. 「URL検査」に `https://pageatelier.jp/` を入力し、必要に応じて「公開URLをテスト」した後、「インデックス登録をリクエスト」を押します。

所有権確認の完了と検索結果への掲載は別の状態です。Search Consoleでインデックス状況を確認します。
