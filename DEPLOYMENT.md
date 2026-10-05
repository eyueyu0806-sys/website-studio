# pageatelier.jp

完成版の公開先は GitHub Pages、独自ドメインは `pageatelier.jp` です。

公開ファイルは `gh-pages` ブランチにあります。ルートの `CNAME` に独自ドメインを指定しています。ドメインはお名前.comで取得済みです。2026年10月5日に独自ドメインのHTTPS応答、公開HTMLとテスト済み完成版の一致、`www.pageatelier.jp` から正規URLへの転送を確認しました。所有者が `Enforce HTTPS` を有効にし、HTTPからHTTPSへの301転送とHTTPSの200応答を確認済みです。GitHub PagesのAPIでも `https_enforced: true`、ルートと `www` の証明書が `approved` であることを確認しました。

## 問い合わせ

受信先は `eye.eyu0806@gmail.com` です。現在のフォームはブラウザからメールを直接送信する方式ではなく、`mailto:` でメールアプリに宛先・相談内容・体験したサイト構成を引き渡します。利用者がメールアプリで送信を確定する必要があります。実際の受信確認は未実施です。LINE相談のURLはまだ仮設定です。

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
