"""Build reviewed articles and the editorial industry landing page (stdlib only)."""
from pathlib import Path
from html import escape as esc
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = 'https://pageatelier.jp'
DATE = '2026-10-07'
TRIAL = '/?utm_source=journal&utm_medium=article&utm_campaign=studio_guide#build'
CONTACT = '/?utm_source=journal&utm_medium=article&utm_campaign=studio_guide#contact'

def head(title, description, path, schema=None):
    data = json.dumps(schema, ensure_ascii=False).replace('<', '\\u003c') if schema else ''
    return f'''<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} | Page Atelier</title><meta name="description" content="{esc(description, quote=True)}"><link rel="canonical" href="{DOMAIN}{path}">
<meta property="og:type" content="{'article' if schema else 'website'}"><meta property="og:locale" content="ja_JP"><meta property="og:site_name" content="Page Atelier">
<meta property="og:title" content="{esc(title, quote=True)}"><meta property="og:description" content="{esc(description, quote=True)}"><meta property="og:url" content="{DOMAIN}{path}">
<meta property="og:image" content="{DOMAIN}/assets/images/pageatelier-share.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="まだ見えていない、あなたのサイトを。Page Atelier">
<meta name="twitter:card" content="summary_large_image"><link rel="stylesheet" href="/assets/acquisition.css">
<script src="/assets/site-config.js" defer></script><script src="/assets/marketing.js" defer></script>
{('<script type="application/ld+json">'+data+'</script>') if data else ''}</head><body>
<header class="header wrap"><a class="brand" href="/"><span class="mark" aria-hidden="true"></span>専門サイト工房</a><nav aria-label="メインメニュー"><a href="/journal/">制作の手引き</a><a href="{esc(CONTACT,quote=True)}">無料相談</a></nav></header>'''

def footer():
    return '''<footer class="footer wrap"><span>© 2026 Page Atelier</span><nav aria-label="関連ページ"><a href="/#price">制作範囲・料金</a><a href="/for-builders.html">施工会社向けの例</a><a href="/journal/">制作の手引き</a><a href="/operator.html">運営者情報</a><a href="/commerce.html">取引条件</a><a href="/privacy.html">プライバシー</a></nav></footer></body></html>'''

def actions(industry=None):
    trial = TRIAL if industry is None else TRIAL.replace("/?", "/?industry=" + industry + "&")
    label = "サイト設計を体験する" if industry is None else "工務店のサイト設計を体験する"
    return f'<div class="actions"><a class="action primary" href="{esc(trial,quote=True)}">{label} →</a><a class="action" href="{esc(CONTACT,quote=True)}">無料で相談する</a><a class="action" href="https://lin.ee/VZsDkE9" data-line target="_blank" rel="noopener">LINEで相談する</a></div>'

def listing(articles):
    return '<ul class="article-list">' + ''.join(f'<li><a href="/journal/{a["slug"]}.html"><time datetime="{a["published"]}">{a["published"]}</time><div><h2>{esc(a["title"])}</h2><p>{esc(a["description"])}</p></div><span aria-hidden="true">↗</span></a></li>' for a in articles) + '</ul>'

def articles():
    result = []
    for path in sorted((ROOT / 'content/journal').glob('*.json')):
        article = json.loads(path.read_text())
        if article['status'] != 'published': continue
        assert article.get('reviewed') is True, path
        assert re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', article['slug']), path
        assert path.stem == article['slug'], path
        result.append(article)
    return sorted(result, key=lambda x: (x['published'], x['slug']), reverse=True)

def build():
    output = ROOT / 'journal'; output.mkdir(exist_ok=True)
    items = articles()
    for a in items:
        path = '/journal/' + a['slug'] + '.html'
        schema = {'@context': 'https://schema.org', '@type': 'Article', 'headline': a['title'], 'description': a['description'], 'datePublished': a['published'], 'dateModified': a['published'], 'inLanguage': 'ja', 'author': {'@type': 'Organization', 'name': 'Page Atelier', 'url': DOMAIN}, 'mainEntityOfPage': DOMAIN + path}
        text = head(a['title'], a['description'], path, schema)
        text += f'<main class="wrap reading"><a class="back" href="/journal/">← 制作の手引き</a><p class="caption">JOURNAL / サイト制作の準備</p><h1>{esc(a["title"])}</h1><p class="article-meta">{a["published"]} / Page Atelier</p><p class="intro">{esc(a["description"])}</p>'
        for s in a['sections']:
            text += '<section><h2>' + esc(s['heading']) + '</h2>'
            text += ''.join('<p>' + esc(p) + '</p>' for p in s['paragraphs'])
            if s.get('items'):text += '<ul>' + ''.join('<li>' + esc(p) + '</li>' for p in s['items']) + '</ul>'
            text += '</section>'
        text += '<aside><h2>自社に必要なサイトを、まず整理する。</h2><p>ページ数や必要な機能が決まっていなくても構いません。制作体験で構成を試し、その内容を相談フォームに添付できます。</p><p><a href="/#price">制作範囲・料金を見る →</a></p>' + actions() + '</aside></main>' + footer()
        (output / (a['slug'] + '.html')).write_text(text)
    text = head('制作の手引き', '会社のサイト制作を始める前に。素材、掲載写真、ページ数、見積りの比較など、依頼の判断材料をまとめました。', '/journal/')
    text += '<main class="wrap growth-main"><p class="caption">JOURNAL / 制作の手引き</p><h1>つくる前の、<br>小さな整理。</h1><p class="intro">会社の強みを伝えるために、何を用意するか。制作を依頼する前の判断材料をまとめました。</p>' + listing(items) + '</main>' + footer()
    (output / 'index.html').write_text(text)
    text = head('リフォーム・外構会社のホームページ制作', '施工例、対応エリア、会社の強みを整理するサイト制作。税込55,000円から、静的サイト中心。必要条件が揃ってから2週間が目安です。', '/for-builders.html')
    text += '''<main class="wrap growth-main"><div class="breadcrumbs"><a href="/">ホーム</a> / 施工会社のサイト制作</div>
<div class="growth-hero"><div><p class="caption">FOR BUILDERS / リフォーム・外構・工務店</p><h1>いい仕事に、<br>伝わる輪郭を。</h1><p class="growth-lead">施工の写真。対応できる地域。会社が大切にしていること。ばらばらの情報を、相談へつながるサイトに整理します。</p><p class="growth-lead">小規模な施工会社の、初めてのサイトや作り直しに。文章・写真は支給を基本として、静的サイトを制作します。</p>''' + actions('builder') + '''</div>
<figure class="frame-sheet"><p class="mock-label">FRAME / 制作サンプル</p><div class="mock-page"><div class="mock-nav"><b>施工会社のサイト構成例</b><span>会社案内 / ご相談</span></div><h2>暮らしの続きを、<br>つくる仕事。</h2><div class="mock-photo" role="img" aria-label="レイアウト説明用の素材写真"><span>施工例を、仕事の説明と一緒に。</span></div><div class="mock-columns"><span>01 / 対応する工事<br>できることを明確に。</span><span>02 / ご相談の流れ<br>次の一歩を分かりやすく。</span></div></div><figcaption>架空の構成・素材写真を使った制作サンプルです。受託案件や施工実績ではありません。</figcaption></figure></div>
<section><div class="section-top"><p class="caption">01 / CONTENT</p><h2>写真を並べるだけで、<br>終わらせない。</h2></div><div class="rows"><div><span class="number">01</span><h3>何を頼める会社か。</h3><p>実際に対応する工事と得意な内容を整理し、相談先として判断できる情報を掲載します。</p></div><div><span class="number">02</span><h3>どんな仕事をしてきたか。</h3><p>許可を得た施工写真に、工事内容と対応したことを添えます。架空の実績は作りません。</p></div><div><span class="number">03</span><h3>どこから相談できるか。</h3><p>対応エリアと相談の流れを案内し、フォームやLINE、外部サービスへつなぎます。</p></div></div></section>
<section><div class="section-top"><p class="caption">02 / SCOPE & PRICE</p><h2>必要な情報量から、<br>範囲を決める。</h2></div><div class="prices"><div class="price-block"><h3>会社の紹介を、1ページに。</h3><p class="price-amount">55,000円<small>税込</small></p><p>1ページ・8セクションまで。会社紹介、主な工事、施工例、対応エリア、相談先をひと続きに整理します。</p></div><div class="price-block"><h3>工事や施工例を、分けて伝える。</h3><p class="price-amount">110,000円<small>税込</small></p><p>トップを含む5ページまで。サービス・施工例・会社案内など、内容に合わせてページを分けます。</p></div></div><p class="note">共通：構成整理・デザイン・スマホ対応・公開設定・検索向け基本設定・フォーム1つ・地図・外部予約/SNSリンク。文章・写真は支給が基本。軽微な修正2回を含みます。支給されたプライバシーポリシー1ページは上記ページ数とは別に含みます。</p><p class="note">CMS・検索・独自予約・決済・撮影・新規原稿作成は個別見積り。ドメイン・サーバー・有料サービス等の実費は別途。任意の更新サポートは税込月5,500円、月2回・合計60分までです。<a href="/commerce.html">取引条件を見る →</a></p></section>
<section><div class="section-top"><p class="caption">03 / PROCESS</p><h2>素材と範囲が揃ってから、<br>2週間を目安に。</h2></div><div class="rows"><div><span class="number">01</span><h3>無料相談・範囲の整理</h3><p>現在のサイト、対応する工事、写真の有無を伺い、制作範囲・費用・実際の納期を確認します。</p></div><div><span class="number">02</span><h3>合意・素材・着手金</h3><p>仕様・必要素材・着手金が揃ってから2週間（14日間）が目安。制作費は銀行振込で着手前50％、最終確認後・公開前50％です。</p></div><div><span class="number">03</span><h3>制作・確認・公開</h3><p>構成とデザインを確認し、スマホや問い合わせ導線を検証します。最終承認と残金確認後に公開し、データと更新方法を案内します。</p></div></div></section>
<section><div class="section-top"><p class="caption">04 / BEFORE YOU START</p><h2>依頼する前の、<br>判断材料。</h2></div>''' + listing(items) + '''</section><section><p class="caption">05 / START A CONVERSATION</p><h2>まだ、まとまっていなくても。</h2><p>会社のサイトに必要な情報を、一緒に整理します。制作体験は無料で、この操作や相談だけで有料契約は成立しません。</p>''' + actions('builder') + '</section></main>' + footer()
    (ROOT / 'for-builders.html').write_text(text)
    # Keep existing legal URLs/dates; add only pages actually built.
    ns = 'http://www.sitemaps.org/schemas/sitemap/0.9';ET.register_namespace('', ns)
    tree = ET.parse(ROOT / 'sitemap.xml'); base = tree.getroot()
    latest = max((x['published'] for x in items), default=DATE)
    additions = {'/for-builders.html': latest, '/journal/': latest}
    additions.update({'/journal/' + x['slug'] + '.html': x['published'] for x in items})
    for path, date in additions.items():
        existing = next((u for u in base if u.find('{'+ns+'}loc').text == DOMAIN+path), None)
        node = existing if existing is not None else ET.SubElement(base, '{'+ns+'}url')
        if existing is None:ET.SubElement(node, '{'+ns+'}loc').text = DOMAIN+path
        last = node.find('{'+ns+'}lastmod')
        if last is None:last = ET.SubElement(node, '{'+ns+'}lastmod')
        last.text = date
    ET.indent(tree, space='  ');tree.write(ROOT / 'sitemap.xml', encoding='unicode', xml_declaration=True)
    print('Built landing page, journal index and', len(items), 'reviewed articles.')

if __name__ == '__main__':build()
