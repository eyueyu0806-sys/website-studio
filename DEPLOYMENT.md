# pageatelier.jp

完成版の公開先は GitHub Pages、独自ドメインは `pageatelier.jp` です。

公開ファイルは `gh-pages` ブランチにあります。ルートの `CNAME` に独自ドメインを指定しています。ドメインの取得・DNS設定・GitHub Pagesの有効化が完了するまでは、公開済みとは扱いません。

## ドメインのDNS設定

ドメインを取得した管理サービスで、次のレコードを設定します。管理画面によってルートの名前は `@` または空欄です。

| 種類 | 名前 | 値 |
| --- | --- | --- |
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |
| CNAME | www | eyueyu0806-sys.github.io |

`www` のCNAMEにはリポジトリ名や `https://` を含めません。MXやメール用TXTなど、サイト接続と関係のないレコードは維持します。ルートの既存レコードが別のサイトを指している場合は、切り替え対象を確認してから変更します。

## GitHub Pages

[このリポジトリのPages設定](https://github.com/eyueyu0806-sys/website-studio/settings/pages)で次を指定します。

1. Source: `Deploy from a branch`
2. Branch: `gh-pages`、Folder: `/(root)`、Save
3. Custom domain: `pageatelier.jp`。ブランチの `CNAME` と一致させます。
4. DNSの確認と証明書の発行が完了したら、`Enforce HTTPS` を有効にします。

公開後のURLは `https://pageatelier.jp/` です。`www.pageatelier.jp` も設定した場合は、GitHub Pagesが指定した正規ドメインへ転送します。

DNS、HTTPS証明書、ページ本体、同梱フォント・画像、業種選択、Builderの生成と相談添付を確認してから公開完了とします。

公式手順: [GitHub Pagesの独自ドメイン管理](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)
