"""Read-only monitoring catches stale queues and blocked sends without API side effects."""
from datetime import date, datetime
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import automation_health as health


class AutomationHealth(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for path in ['content/journal', 'business/marketing', 'assets']:
            (self.root/path).mkdir(parents=True)
        self.now = datetime(2026, 10, 9, 15, 30, tzinfo=health.JST)
        self.write('content/journal/current.json', dict(slug='current', status='published', published='2026-10-09', reviewed=True))
        for i in range(10, 18):
            self.write(f'content/journal/day-{i}.json', dict(slug=f'day-{i}', status='queued', publish_after=f'2026-10-{i}', reviewed=True))
        self.write('business/marketing/social-posts.json', [dict(id=f'post-{i}', reviewed=True, publish_after=f'2026-10-{i}') for i in range(10, 18)])
        self.write('business/marketing/publication-log.json', {})
        (self.root/'assets/site-config.js').write_text("contactMode: 'formsubmit'")
    def tearDown(self):
        self.temp.cleanup()
    def write(self, name, value):
        (self.root/name).write_text(json.dumps(value))
    def rows(self, **kwargs):
        return health.report(root=self.root, now=self.now, env={}, **kwargs)
    def test_future_dated_items_do_not_hide_gap(self):
        items = [dict(publish_after='2026-10-20') for _ in range(20)]
        self.assertEqual(health.first_gap(items, date(2026, 10, 9)), '2026-10-10')
    def test_overdue_items_fill_only_one_day_each(self):
        self.assertEqual(health.first_gap([dict(publish_after='2026-10-01')]*2, date(2026,10,9)), '2026-10-12')
    def test_missing_connections_are_waiting_not_success(self):
        rows = self.rows()
        self.assertFalse(any(r['state']=='error' for r in rows))
        self.assertEqual(next(r for r in rows if r['name']=='Instagram接続')['state'], 'waiting')
    def test_low_article_stock_is_actionable(self):
        for p in (self.root/'content/journal').glob('day-*.json'):
            p.unlink()
        self.assertTrue(any(r['name']=='記事の在庫' and r['state']=='error' for r in self.rows()))
    def test_unresolved_or_unknown_ledger_is_not_retried(self):
        for state in ['publishing', 'created', 'creating', 'invalid']:
            data={'post-10':dict(state=state)}
            self.write('business/marketing/publication-log.json',data)
            self.assertTrue(any(r['name']=='Instagram配信記録' and r['state']=='error' for r in self.rows()))
            self.assertEqual(json.loads((self.root/'business/marketing/publication-log.json').read_text()),data)
    def test_overdue_article_after_morning_is_error(self):
        self.write('content/journal/current.json',dict(slug='current',status='queued',publish_after='2026-10-09',reviewed=True))
        self.assertTrue(any(r['name']=='今日の記事' and r['state']=='error' for r in self.rows()))
        early=health.report(self.root,now=self.now.replace(hour=8),env={})
        self.assertFalse(any(r['name']=='今日の記事' and r['state']=='error' for r in early))
    def test_live_only_reads_fixed_endpoints_and_does_not_log_token(self):
        calls=[]
        def get(url, token=None):
            calls.append((url,token))
            if 'api.github.com' in url:return json.dumps({'permissions':{'push':True}})
            if 'dns.google' in url:return json.dumps({'Status':3})
            return '<link rel="canonical" href="'+url+'">'
        rows=health.report(self.root,now=self.now,env={'GH_TOKEN':'synthetic-sensitive-value'},live=True,get=get)
        self.assertFalse(any(r['state']=='error' for r in rows))
        self.assertEqual(len(calls),6)
        self.assertTrue(all(token is None for url,token in calls if 'api.github.com' not in url))
        self.assertNotIn('synthetic-sensitive-value',health.markdown(rows,self.now))
    def test_bad_credentials_and_wrong_public_page_are_errors(self):
        def get(url,token=None):
            if 'api.github.com' in url:raise RuntimeError('HTTP 401')
            if 'dns.google' in url:return '{"Status":3}'
            return '<h1>Wrong page</h1>'
        rows=health.report(self.root,now=self.now,env={'GH_TOKEN':'synthetic'},live=True,get=get)
        failures={r['name'] for r in rows if r['state']=='error'}
        self.assertTrue({'記事公開の認証','トップページ','最新公開記事'} <= failures)
    def test_dns_presence_does_not_claim_resend_verified(self):
        def get(url,token=None):
            if 'api.github.com' in url:return '{"permissions":{"push":true}}'
            if 'type=TXT' in url:return json.dumps({'Status':0,'Answer':[{'type':16,'data':'"p=synthetic"'}]})
            if 'name=rsend.' in url:return json.dumps({'Status':0,'Answer':[{'type':5,'data':'rsend-apne1.forge.rmta.net.'}]})
            if 'name=send.' in url:return json.dumps({'Status':0,'Answer':[{'type':5,'data':'send.forge.rmta.net.'}]})
            return '<link rel="canonical" href="'+url+'">'
        rows=health.report(self.root,now=self.now,env={'GH_TOKEN':'synthetic'},live=True,get=get)
        dns=[r for r in rows if r['name'].startswith('DNS')]
        self.assertEqual(len(dns),3)
        self.assertTrue(all(r['state']=='ok' and '別途確認' in r['detail'] for r in dns))
    def test_active_receipt_missing_credentials_is_error(self):
        (self.root/'assets/site-config.js').write_text("contactMode: 'resend'")
        self.assertTrue(any(r['name']=='自動返信接続' and r['state']=='error' for r in self.rows()))

if __name__=='__main__':unittest.main()
