"""Single-image Instagram Login publishing; durable ledger avoids blind retries."""
import argparse
from datetime import datetime, timezone, timedelta
import json
import os
from pathlib import Path
import re
import subprocess
import time
from urllib import request, error

ROOT=Path(__file__).resolve().parents[1]
LEDGER=ROOT/'business/marketing/publication-log.json'
POSTS=ROOT/'business/marketing/social-posts.json'
BASE='https://graph.instagram.com'

def save(data):
    temp=LEDGER.with_suffix('.tmp');temp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');temp.replace(LEDGER)
    if os.environ.get('PERSIST_LEDGER_TO_GIT')=='true':
        relative=str(LEDGER.relative_to(ROOT))
        subprocess.run(['git','add',relative],cwd=ROOT,check=True)
        changed=subprocess.run(['git','diff','--cached','--quiet','--',relative],cwd=ROOT).returncode
        if changed==1:
            subprocess.run(['git','-c','commit.gpgsign=false','commit','-m','Checkpoint Instagram publication state','--',relative],cwd=ROOT,check=True)
            # Before an API side effect, the checkpoint must be durable remotely.
            # After publication, a failed push leaves the earlier publishing checkpoint.
            subprocess.run(['git','push','origin','HEAD:main'],cwd=ROOT,check=True)
        elif changed!=0:raise RuntimeError('Cannot check publication ledger changes')

def api(path, token, data=None):
    req=request.Request(BASE+path,headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'},data=json.dumps(data).encode() if data is not None else None)
    try:
        with request.urlopen(req,timeout=30) as response:return json.load(response)
    except error.HTTPError as exc:
        # Error bodies/URLs can contain credential information. Do not log them.
        raise RuntimeError('Instagram API rejected request (HTTP '+str(exc.code)+'); check permissions/token. No automatic retry.') from None
    except (error.URLError,TimeoutError):raise RuntimeError('Instagram response unavailable. Inspect ledger before retrying.') from None

def publish(post_id=None, dry_run=True):
    posts=json.loads(POSTS.read_text());ledger=json.loads(LEDGER.read_text())
    today=datetime.now(timezone(timedelta(hours=9))).date().isoformat()
    active=[p for p in posts if p.get('reviewed') is True and p.get('publish_after','9999')<=today and p['id'] not in ledger]
    if post_id:
        if post_id in ledger:print('Recorded post: '+post_id+'. Not publishing again.');return
        active=[p for p in active if p['id']==post_id]
    if not active:print('No due reviewed social post.');return
    post=sorted(active,key=lambda p:(p['publish_after'],p['id']))[0]
    assert re.fullmatch(r'[a-z0-9-]{1,80}',post['id'])
    assert re.fullmatch(r'https://pageatelier\.jp/assets/marketing/[a-z0-9-]+\.jpg',post['image_url'])
    assert 0<len(post['caption'])<=2000
    print(('Dry run: ' if dry_run else 'Publishing: ')+post['id'])
    if dry_run:return
    token=os.environ.get('INSTAGRAM_ACCESS_TOKEN');account=os.environ.get('INSTAGRAM_ACCOUNT_ID');version=os.environ.get('INSTAGRAM_API_VERSION')
    if not token or not account or not version:raise RuntimeError('Set INSTAGRAM_ACCESS_TOKEN, INSTAGRAM_ACCOUNT_ID and INSTAGRAM_API_VERSION securely first.')
    assert re.fullmatch(r'\d+',account) and re.fullmatch(r'v\d+\.0',version)
    with request.urlopen(post['image_url'],timeout=20) as response:
        assert response.status==200 and response.headers.get_content_type()=='image/jpeg'
        assert response.read(2)==b'\xff\xd8'
    ledger[post['id']]={'state':'creating','at':datetime.now(timezone.utc).isoformat()};save(ledger)
    try:
        container=api('/'+version+'/'+account+'/media',token,{'image_url':post['image_url'],'caption':post['caption']})['id']
        ledger[post['id']].update(state='created',container_id=container);save(ledger)
        ready=False
        for _ in range(12):
            state=api('/'+version+'/'+container+'?fields=status_code',token).get('status_code')
            if state=='FINISHED':ready=True;break
            if state in ['ERROR','EXPIRED']:raise RuntimeError('Instagram container not publishable; inspect status before retry.')
            time.sleep(5)
        if not ready:raise RuntimeError('Instagram container preparation timed out; inspect before retry.')
        ledger[post['id']]['state']='publishing';save(ledger)
        result=api('/'+version+'/'+account+'/media_publish',token,{'creation_id':container})
        ledger[post['id']].update(state='published',media_id=result['id'],published_at=datetime.now(timezone.utc).isoformat());save(ledger)
        print('Confirmed media ID:',result['id'])
    except Exception:
        # Persist the last known state. Do not delete a publishing entry after a timeout.
        save(ledger);raise

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--publish',action='store_true');parser.add_argument('--post');args=parser.parse_args();publish(args.post,not args.publish)
