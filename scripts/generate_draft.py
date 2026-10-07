"""Generate one unreviewed article draft. Never publish model output directly."""
import argparse
from datetime import datetime, timezone
import json
import os
import subprocess
from pathlib import Path
from urllib import request, error

ROOT=Path(__file__).resolve().parents[1]
TOPICS=['施工会社のホームページに載せる対応エリアの整理','制作依頼前に、会社紹介文をまとめる方法','外部予約リンクと専用予約システムの違い']
def save(path, article):
    path.write_text(json.dumps(article,ensure_ascii=False,indent=2)+'\n')
    if os.environ.get('PERSIST_DRAFT_TO_GIT')=='true':
        relative=str(path.relative_to(ROOT))
        subprocess.run(['git','add',relative],cwd=ROOT,check=True)
        changed=subprocess.run(['git','diff','--cached','--quiet','--',relative],cwd=ROOT).returncode
        if changed==1:
            subprocess.run(['git','-c','commit.gpgsign=false','commit','-m','Checkpoint article generation attempt','--',relative],cwd=ROOT,check=True)
            subprocess.run(['git','push','origin','HEAD:main'],cwd=ROOT,check=True)
        elif changed!=0:raise RuntimeError('Cannot check draft reservation changes')
def generate(topic=0):
    token=os.environ.get('OPENAI_API_KEY');model=os.environ.get('OPENAI_MODEL')
    if not token or not model:raise RuntimeError('OPENAI_API_KEY and an owner-selected OPENAI_MODEL are required. No API call made.')
    now=datetime.now(timezone.utc);folder=ROOT/'content/drafts';folder.mkdir(exist_ok=True)
    existing=list(folder.glob(now.strftime('%Y-%m')+'-*.json'))
    if len(existing)>=4:raise RuntimeError('Monthly draft call limit reached (4). No API call made.')
    key=now.strftime('%Y-%m-%d')+'-'+str(topic)
    if (folder/(key+'.json')).exists():raise RuntimeError('A draft/attempt for this day and topic already exists. No retry.')
    # Reserve before calling so failed responses cannot cause repeated billable attempts.
    destination=folder/(key+'.json');save(destination,{'status':'attempt_reserved','reviewed':False,'topic':TOPICS[topic]})
    facts=(ROOT/'PRICING.md').read_text()
    schema={'type':'object','additionalProperties':False,'properties':{'title':{'type':'string'},'description':{'type':'string'},'sections':{'type':'array','items':{'type':'object','additionalProperties':False,'properties':{'heading':{'type':'string'},'paragraphs':{'type':'array','items':{'type':'string'}},'items':{'type':'array','items':{'type':'string'}}},'required':['heading','paragraphs','items']}}},'required':['title','description','sections']}
    prompt='日本語の実務記事の下書きを作成。テーマ：'+TOPICS[topic]+'。事実は次の公開料金条件だけ。統計・受託実績・顧客名・成果・法的保証・未確認の工事費・順位保証を作らない。HTMLや外部リンク不要。4見出し、各2段落程度。\n'+facts
    payload={'model':model,'store':False,'max_output_tokens':4500,'input':prompt,'text':{'format':{'type':'json_schema','name':'article_draft','strict':True,'schema':schema}}}
    req=request.Request('https://api.openai.com/v1/responses',headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'},data=json.dumps(payload).encode())
    try:
        with request.urlopen(req,timeout=90) as response:result=json.load(response)
        if result.get('status')!='completed':raise RuntimeError('Draft generation incomplete; reserved attempt retained.')
        texts=[c['text'] for item in result.get('output',[]) for c in item.get('content',[]) if c.get('type')=='output_text']
        article=json.loads(''.join(texts));article.update(status='draft',reviewed=False,topic=TOPICS[topic],usage=result.get('usage',{}),model=model)
        save(destination,article);print('Draft saved for fact/quality review:',destination.name)
    except error.HTTPError as exc:raise RuntimeError('AI API rejected request (HTTP '+str(exc.code)+'); reserved attempt retained. No automatic retry.') from None
    except (error.URLError,TimeoutError):raise RuntimeError('AI response unavailable; reserved attempt retained. No automatic retry.') from None

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--topic',type=int,choices=range(len(TOPICS)),default=0);args=parser.parse_args();generate(args.topic)
