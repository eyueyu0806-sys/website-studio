"""Exercise daily limits and publication ordering with no external traffic."""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import build_content
import release_queue
import publish_instagram as social

class Response:
    status=200
    def __init__(self,content_type,body):
        self.body=body
        self.headers=type('Headers',(),{'get_content_type':lambda _:content_type})()
    def __enter__(self):return self
    def __exit__(self,*_):return False
    def read(self,n):return self.body[:n]

class DailyPublication(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.posts=self.root/'posts.json';self.ledger=self.root/'ledger.json';self.ledger.write_text('{}')
        self.posts.write_text(json.dumps([dict(id=f'post-{i}',reviewed=True,publish_after='2020-01-01',image_url=f'https://pageatelier.jp/assets/marketing/post-{i}.jpg',article_path=f'/journal/post-{i}.html',caption='Reviewed test caption') for i in [1,2]]))
        self.patches=[patch.object(social,'POSTS',self.posts),patch.object(social,'LEDGER',self.ledger),patch.dict(os.environ,{'INSTAGRAM_ACCESS_TOKEN':'synthetic-test-token','INSTAGRAM_ACCOUNT_ID':'123','INSTAGRAM_API_VERSION':'v25.0','PERSIST_LEDGER_TO_GIT':'false'})]
        for p in self.patches:p.start()
    def tearDown(self):
        for p in reversed(self.patches):p.stop()
        self.temp.cleanup()
    def response(self,url,**_):
        if '/journal/' in url:return Response('text/html',('<link rel="canonical" href="'+url+'">').encode())
        return Response('image/jpeg',b'\xff\xd8')
    def api(self,path,*_,**__):
        return {'status_code':'FINISHED'} if 'status_code' in path else {'id':'synthetic-id'}

    def test_article_one_per_day_even_when_multiple_are_overdue(self):
        folder=self.root/'content/journal';folder.mkdir(parents=True)
        for i in [1,2]:
            (folder/f'a-{i}.json').write_text(json.dumps(dict(slug=f'a-{i}',status='queued',reviewed=True,publish_after='2020-01-01')))
        with patch.object(build_content,'ROOT',self.root),patch.object(build_content,'build'):
            self.assertEqual(release_queue.release('2026-10-08',False),'a-1')
            self.assertIsNone(release_queue.release('2026-10-08',False))
            self.assertEqual(release_queue.release('2026-10-09',False),'a-2')

    def test_instagram_one_per_day_including_forced_other_post(self):
        with patch.object(social.request,'urlopen',side_effect=self.response),patch.object(social,'api',side_effect=self.api) as calls:
            social.publish(dry_run=False);self.assertEqual(calls.call_count,3)
            social.publish('post-2',False);self.assertEqual(calls.call_count,3)
        self.assertEqual(list(json.loads(self.ledger.read_text())),['post-1'])

    def test_unavailable_article_prevents_any_instagram_side_effect(self):
        with patch.object(social.request,'urlopen',side_effect=HTTPError('synthetic',404,'Not yet available',None,None)),patch.object(social,'api') as calls:
            social.publish(dry_run=False);calls.assert_not_called()
        self.assertEqual(json.loads(self.ledger.read_text()),{})

    def test_wrong_canonical_is_not_treated_as_ready(self):
        with patch.object(social.request,'urlopen',return_value=Response('text/html',b'<h1>Not found</h1>')),patch.object(social,'api') as calls:
            social.publish(dry_run=False);calls.assert_not_called()

    def test_lost_publish_response_blocks_next_post_and_preserves_state(self):
        def lost(path,*args,**kwargs):
            if path.endswith('/media_publish'):raise RuntimeError('Synthetic lost response')
            return self.api(path,*args,**kwargs)
        with patch.object(social.request,'urlopen',side_effect=self.response),patch.object(social,'api',side_effect=lost) as calls:
            with self.assertRaisesRegex(RuntimeError,'Synthetic lost'):social.publish('post-1',False)
            self.assertEqual(json.loads(self.ledger.read_text())['post-1']['state'],'publishing')
            count=calls.call_count
            social.publish('post-1',False)
            with self.assertRaisesRegex(RuntimeError,'unresolved'):social.publish('post-2',False)
            self.assertEqual(calls.call_count,count)

    def test_actual_publication_date_handles_crossing_midnight(self):
        self.assertEqual(social.posting_day({'posting_day':'2026-10-07','published_at':'2026-10-07T15:01:00+00:00'}),'2026-10-08')

    def test_no_network_or_ledger_change_on_dry_run(self):
        with patch.object(social.request,'urlopen') as network,patch.object(social,'api') as api:
            social.publish(dry_run=True);network.assert_not_called();api.assert_not_called()
        self.assertEqual(json.loads(self.ledger.read_text()),{})

if __name__=='__main__':unittest.main()
