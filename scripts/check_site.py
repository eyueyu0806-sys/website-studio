"""Verify real local links, assets, canonical URLs, and reviewed publication input."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json
import re
import xml.etree.ElementTree as ET
import hashlib
import build_content

ROOT = build_content.ROOT
PUBLIC_FILES = ['index.html', 'operator.html', 'commerce.html', 'privacy.html', 'for-builders.html', 'robots.txt', 'sitemap.xml', 'CNAME', '.nojekyll']

def public_files():
    return sorted(PUBLIC_FILES + [str(p.relative_to(ROOT)) for folder in ['assets', 'journal'] for p in (ROOT/folder).rglob('*') if p.is_file() and p.suffix.lower() in {'.html', '.css', '.js', '.woff', '.woff2', '.png', '.jpg', '.jpeg', '.webp', '.svg', '.txt', '.md'}])

class Page(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.ids=[];self.canonical=[];self.h1=0;self.headings=[];self.json=[];self.in_json=False
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'):self.ids.append(a['id'])
        if tag=='h1':self.h1 += 1
        for attr in ['href', 'src']:
            if a.get(attr):self.links.append(a[attr])
        if tag=='link' and a.get('rel')=='canonical':self.canonical.append(a.get('href'))
        if tag=='script' and a.get('type')=='application/ld+json':self.in_json=True
    def handle_endtag(self, tag):
        if tag=='script':self.in_json=False
    def handle_data(self, data):
        if self.in_json:self.json.append(data)

def check():
    files=public_files(); errors=[]; parsed={}
    for name in files:
        path=ROOT/name
        if not path.is_file():errors.append('Missing public file: '+name);continue
        if path.suffix=='.html':
            p=Page();p.feed(path.read_text());parsed[name]=p
            if p.h1 != 1:errors.append(f'{name}: expected one h1, found {p.h1}')
            if len(p.ids)!=len(set(p.ids)):errors.append(name+': duplicate IDs')
            canonical=build_content.DOMAIN+'/'+(name[:-10] if name.endswith('index.html') else name)
            if p.canonical != [canonical]:errors.append(name+': incorrect canonical '+str(p.canonical))
            for data in p.json:
                try:json.loads(data)
                except ValueError:errors.append(name+': invalid structured data')
    for name,p in parsed.items():
        for link in p.links:
            u=urlsplit(link)
            if u.scheme or u.netloc:continue
            target=(ROOT/unquote(u.path.lstrip('/'))) if u.path.startswith('/') else (ROOT/name).parent/unquote(u.path)
            if not u.path:target=ROOT/name
            if target.is_dir():target=target/'index.html'
            try:relative=str(target.resolve().relative_to(ROOT))
            except ValueError:errors.append(name+': link escapes root');continue
            if relative not in files:errors.append(name+': missing local link '+link);continue
            if u.fragment and relative in parsed and unquote(u.fragment) not in parsed[relative].ids:errors.append(name+': missing anchor '+link)
    for name in [x for x in files if x.endswith('.css')]:
        for ref in re.findall(r'url\([\'\"]?([^\)\'\"]+)',(ROOT/name).read_text()):
            if not ref.startswith(('data:', 'https:', 'http:')) and not ((ROOT/name).parent/ref).is_file():errors.append(name+': missing CSS asset '+ref)
    urls=ET.parse(ROOT/'sitemap.xml').getroot()
    for node in urls:
        loc=node.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text
        u=urlsplit(loc)
        relative=u.path.lstrip('/') or 'index.html'
        if relative.endswith('/'):relative+='index.html'
        if u.netloc!='pageatelier.jp' or relative not in parsed:errors.append('Invalid sitemap URL '+loc)
    for a in build_content.articles():
        text=json.dumps(a,ensure_ascii=False)
        if re.search(r'必ず.{0,10}(?:上位|受注|問い合わせ)|受注実績\s*\d|検索順位を保証',text):errors.append(a['slug']+': prohibited promise')
        assert a.get('reviewed') is True
    if errors:raise RuntimeError('\n'.join(errors))
    print(f'PASS {len(parsed)} HTML pages, {len(files)} public files, local links/assets/canonicals/sitemap and reviewed articles')
    return files

if __name__=='__main__':check()
