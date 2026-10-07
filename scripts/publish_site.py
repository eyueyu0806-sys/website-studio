"""Publish only checked public files. Keeps business documents/secrets off Pages."""
from pathlib import Path
import argparse
import os
import subprocess
import tempfile
import check_site

ROOT=check_site.ROOT
def git(*args, env=None, input=None):
    return subprocess.check_output(['git',*args],cwd=ROOT,env=env,input=input,text=True).strip()

def publish(do_publish=False):
    files=check_site.check()
    if git('status','--porcelain','--',*files):raise RuntimeError('Commit checked public files before publishing')
    git('fetch','origin','refs/heads/gh-pages:refs/remotes/origin/gh-pages')
    base=git('rev-parse','origin/gh-pages')
    with tempfile.TemporaryDirectory(prefix='pageatelier-publish-') as directory:
        env=os.environ.copy();env['GIT_INDEX_FILE']=str(Path(directory)/'index')
        git('read-tree',base,env=env)
        for name in files:
            blob=git('rev-parse','HEAD:'+name)
            git('update-index','--add','--cacheinfo','100644,'+blob+','+name,env=env)
        tree=git('write-tree',env=env)
        changed=git('diff','--name-only',base,tree).splitlines()
        assert all(name in files for name in changed), changed
        if not changed:print('Public files already match checked source');return None
        print('Public changes:',', '.join(changed))
        if not do_publish:print('Dry run: no remote publication');return None
        commit=git('commit-tree',tree,'-p',base,input='Publish checked Page Atelier pages from '+git('rev-parse','--short','HEAD')+'\n')
        git('push','origin',commit+':refs/heads/gh-pages')
        print('PUBLIC_COMMIT='+commit)
        return commit

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--publish',action='store_true');args=parser.parse_args();publish(args.publish)
