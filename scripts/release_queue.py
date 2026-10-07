"""Release at most one already-reviewed article due today; never approve AI drafts."""
from datetime import datetime, timezone, timedelta
import argparse
import json
import build_content

def release(today=None, dry_run=True):
    today=today or datetime.now(timezone(timedelta(hours=9))).date().isoformat()
    candidates=[]
    for path in (build_content.ROOT/'content/journal').glob('*.json'):
        data=json.loads(path.read_text())
        if data.get('status')=='queued' and data.get('reviewed') is True and data.get('publish_after','9999')<=today:candidates.append((data['publish_after'],path,data))
    if not candidates:print('No due reviewed article. No AI calls, charges or publication.');return None
    _,path,data=sorted(candidates,key=lambda x:(x[0],x[1].name))[0]
    print(('Dry run: ' if dry_run else 'Release: ')+data['slug'])
    if dry_run:return data['slug']
    data.update(status='published',published=today)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');build_content.build();return data['slug']

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--publish-approved',action='store_true');parser.add_argument('--date');args=parser.parse_args();release(args.date,not args.publish_approved)
