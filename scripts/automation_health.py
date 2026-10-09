"""Read-only automation health report. Never publishes content or sends email."""
import argparse
from datetime import date, datetime, timedelta, timezone
import json
import os
from pathlib import Path
import re
from urllib import request, error

ROOT = Path(__file__).resolve().parents[1]
JST = timezone(timedelta(hours=9))
REPO = 'eyueyu0806-sys/website-studio'
ORIGIN = 'https://pageatelier.jp'
PENDING = {'creating', 'created', 'publishing'}


def first_gap(items, today, days=7):
    """Simulate one release per day; overdue items count once, future ones only when due."""
    pool = sorted(x['publish_after'] for x in items)
    for offset in range(1, days + 1):
        day = (today + timedelta(days=offset)).isoformat()
        if not pool or pool[0] > day:
            return day
        pool.pop(0)
    return None


def inventory(root, today):
    articles = [json.loads(p.read_text()) for p in (root/'content/journal').glob('*.json')]
    posts = json.loads((root/'business/marketing/social-posts.json').read_text())
    ledger = json.loads((root/'business/marketing/publication-log.json').read_text())
    queued = [a for a in articles if a.get('reviewed') is True and a['status'] == 'queued']
    published = [a for a in articles if a['status'] == 'published']
    social = [p for p in posts if p.get('reviewed') is True and p['id'] not in ledger]
    blocked = [key for key, value in ledger.items() if value.get('state') in PENDING]
    unknown = [key for key, value in ledger.items() if value.get('state') not in PENDING | {'published'}]
    return dict(queued=queued, published=published, social=social, blocked=blocked, unknown=unknown,
                article_gap=first_gap(queued, today), social_gap=first_gap(social, today))


def fetch(url, token=None):
    headers = {'User-Agent': 'PageAtelier-Automation-Health'}
    if token:
        if not url.startswith('https://api.github.com/'):
            raise RuntimeError('Authentication destination rejected')
        headers['Authorization'] = 'Bearer ' + token
    try:
        with request.urlopen(request.Request(url, headers=headers), timeout=20) as response:
            return response.read(600000).decode('utf-8')
    except error.HTTPError as exc:
        raise RuntimeError('HTTP ' + str(exc.code)) from None
    except (error.URLError, TimeoutError, OSError):
        raise RuntimeError('接続または応答を確認できませんでした') from None


def report(root=ROOT, now=None, live=False, env=None, get=fetch):
    now = (now or datetime.now(JST)).astimezone(JST)
    today = now.date()
    env = os.environ if env is None else env
    rows = []
    add = lambda state, name, detail: rows.append(dict(state=state, name=name, detail=detail))
    data = inventory(root, today)
    if data['article_gap']:
        add('error', '記事の在庫', '翌日から7日間の配信に不足。最初の不足日：' + data['article_gap'])
    else:
        add('ok', '記事の在庫', f"確認済みの未公開記事 {len(data['queued'])}本。翌日から7日間の枠を確保。")
    # An overdue article after the two morning runs should not look healthy.
    due = any(a['publish_after'] <= today.isoformat() for a in data['queued'])
    done = any(a['published'] == today.isoformat() for a in data['published'])
    if due and not done and now.hour >= 13:
        add('error', '今日の記事', '13時を過ぎても公開待ちの予約記事があります。Release reviewed contentの結果を確認。')
    else:
        add('ok', '今日の記事', '本日分は公開済み。' if done else '公開時刻前、または本日の予約対象なし。')
    if data['blocked'] or data['unknown']:
        add('error', 'Instagram配信記録', '送信結果未確定または不明な状態があります。記録を削除して再送せず、Instagram本体で確認。')
    else:
        add('ok', 'Instagram配信記録', '送信結果が未確定の記録なし。実投稿済みを意味する表示ではありません。')
    add('warning' if data['social_gap'] else 'ok', 'Instagram原稿',
        '翌日から7日間の在庫に不足：' + data['social_gap'] if data['social_gap'] else f"確認済みの未送信原稿 {len(data['social'])}件。")
    social_names = ['INSTAGRAM_ACCESS_TOKEN', 'INSTAGRAM_ACCOUNT_ID', 'INSTAGRAM_API_VERSION']
    missing = [n for n in social_names if env.get('HAS_' + n) != 'true']
    add('waiting' if missing else 'ok', 'Instagram接続',
        '未設定：' + ', '.join(missing) if missing else '必要設定は存在。トークンの有効性・権限・実投稿は別途確認。')
    receipt_names = ['CLOUDFLARE_API_TOKEN', 'CLOUDFLARE_ACCOUNT_ID', 'RESEND_API_KEY', 'TURNSTILE_SECRET_KEY']
    receipt_missing = [n for n in receipt_names if env.get('HAS_' + n) != 'true']
    config = (root/'assets/site-config.js').read_text()
    active = bool(re.search(r"contactMode:\s*['\"]resend['\"]", config))
    if receipt_missing:
        add('error' if active else 'waiting', '自動返信接続', '未設定：' + ', '.join(receipt_missing) + ('。既存フォームを継続。' if not active else '。有効化済みの設定を点検。'))
    else:
        add('ok' if active else 'waiting', '自動返信接続', '必要設定は存在。DNS認証・Worker接続・両メールの受信を確認するまで完了扱いにしない。')
    if not live:
        add('waiting', '外部接続', '--live未指定。ネットワーク・トークンの有効性は検証していません。')
        return rows
    token = env.get('GH_TOKEN')
    if not token:
        add('error', '記事公開の認証', 'PUBLICATION_TOKENが未設定です。')
    else:
        try:
            metadata = json.loads(get('https://api.github.com/repos/' + REPO, token=token))
            assert metadata.get('permissions', {}).get('push') is True
            add('ok', '記事公開の認証', 'GitHub認証とリポジトリ書き込み権限の応答を確認。')
        except (RuntimeError, ValueError, AssertionError):
            add('error', '記事公開の認証', 'トークンの有効性・対象リポジトリ・Contents権限を確認してください。')
    latest = max(data['published'], key=lambda a: (a['published'], a['slug']), default=None)
    paths = [('', 'トップページ')]
    if latest:
        paths.append(('/journal/' + latest['slug'] + '.html', '最新公開記事'))
    for path, label in paths:
        url = ORIGIN + (path or '/')
        try:
            html = get(url)
            assert '<link rel="canonical" href="' + url + '">' in html
            add('ok', label, url + ' のHTTPS応答とcanonicalを確認。')
        except (RuntimeError, AssertionError):
            add('error', label, '公開URLまたはcanonicalを確認できません。Pagesの公開結果を確認。')
    records = [('resend._domainkey', 'TXT', None), ('rsend', 'CNAME', 'rsend-apne1.forge.rmta.net.'), ('send', 'CNAME', 'send.forge.rmta.net.')]
    for host, kind, expected in records:
        try:
            dns = json.loads(get('https://dns.google/resolve?name=' + host + '.pageatelier.jp&type=' + kind))
            answers = dns.get('Answer', [])
            found = dns.get('Status') == 0 and any(
                a.get('type') == (16 if kind == 'TXT' else 5) and
                ('p=' in a.get('data', '') if expected is None else a.get('data', '').lower() == expected)
                for a in answers)
            add('ok' if found else ('error' if active else 'waiting'), 'DNS：' + host,
                '公開DNSに存在。ResendのVerified表示は別途確認。' if found else '指定レコードを確認できません。お名前.comのpageatelier.jpの登録済み一覧と照合。')
        except (RuntimeError, ValueError):
            add('warning', 'DNS：' + host, 'DNS照会の応答を確認できません。設定不備とは断定していません。')
    return rows


def markdown(rows, now):
    labels = {'ok': '確認済み', 'waiting': '接続待ち', 'warning': '注意', 'error': '要対応'}
    lines = ['# Page Atelier 自動化点検', '', now.astimezone(JST).strftime('%Y-%m-%d %H:%M JST'), '',
             '読み取り専用の点検です。記事・Instagramの投稿やメール送信は行いません。', '',
             '| 状態 | 項目 | 確認結果 |', '| --- | --- | --- |']
    for row in rows:
        clean = lambda s: str(s).replace('|', '／').replace('\n', ' ')
        lines.append('| ' + ' | '.join([labels[row['state']], clean(row['name']), clean(row['detail'])]) + ' |')
    lines += ['', '点検の失敗は投稿処理を停止しません。公開処理は別のワークフローです。',
              '接続待ちは完了扱いにしません。認証情報の値・顧客情報はこのレポートに記録しません。',
              '失敗通知の受信はGitHubの通知設定に依存します。']
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--live', action='store_true')
    args = parser.parse_args()
    now = datetime.now(JST)
    rows = report(now=now, live=args.live)
    text = markdown(rows, now)
    print(text)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as f:
            f.write(text)
    if any(r['state'] == 'error' for r in rows):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
