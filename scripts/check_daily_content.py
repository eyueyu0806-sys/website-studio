"""Check daily publication inputs and rendered assets without third-party packages."""
from datetime import date
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]

def jpeg_dimensions(data):
    assert data[:2]==b'\xff\xd8','Not a JPEG'
    i=2
    while i<len(data):
        assert data[i]==255,'Malformed JPEG marker'
        while data[i]==255:i+=1
        marker=data[i];i+=1
        if marker in {0xd8,0xd9}:continue
        size=int.from_bytes(data[i:i+2],'big')
        assert size>=2,'Malformed JPEG segment'
        if marker in {0xc0,0xc1,0xc2}:
            return int.from_bytes(data[i+5:i+7],'big'),int.from_bytes(data[i+3:i+5],'big')
        i+=size
    raise AssertionError('JPEG dimensions missing')

def check():
    articles={}
    for path in (ROOT/'content/journal').glob('*.json'):
        a=json.loads(path.read_text())
        assert path.stem==a['slug'] and re.fullmatch(r'[a-z0-9-]+',a['slug']),path
        assert a['status'] in {'published','queued'},path
        assert a.get('reviewed') is True,path
        date.fromisoformat(a['published'] if a['status']=='published' else a['publish_after'])
        assert len(a['sections'])>=3 and all(s['heading'] and s['paragraphs'] for s in a['sections']),path
        articles[a['slug']]=a
    posts=json.loads((ROOT/'business/marketing/social-posts.json').read_text())
    ids=set();days=set()
    for p in posts:
        assert p['id'] not in ids and re.fullmatch(r'[a-z0-9-]{1,80}',p['id']),p['id']
        ids.add(p['id']);date.fromisoformat(p['publish_after'])
        assert p.get('reviewed') is True,p['id']
        assert p['publish_after'] not in days,'More than one scheduled Instagram post for a day'
        days.add(p['publish_after'])
        assert 0<len(p['caption'])<=2000,p['id']
        assert p['image_url']==f"https://pageatelier.jp/assets/marketing/{p['id']}.jpg",p['id']
        image=ROOT/'assets/marketing'/f"{p['id']}.jpg"
        assert image.stat().st_size<8_000_000 and jpeg_dimensions(image.read_bytes())==(1080,1350),p['id']
        assert p['article_path']==f"/journal/{p['id']}.html",p['id']
        a=articles[p['id']]
        assert a.get('publish_after',a.get('published'))<=p['publish_after'],p['id']
        assert a['title'] in p['caption'],p['id']
        c=p['card'];assert c['layout'] in {'notes','comparison','steps','checklist'} and len(c['points'])==3,p['id']
        assert all(x['label'] and x['text'] for x in c['points']),p['id']
    print(f'PASS {len(articles)} reviewed article inputs, {len(posts)} distinct daily posts, JPEG dimensions, dates and article links')

if __name__=='__main__':check()
