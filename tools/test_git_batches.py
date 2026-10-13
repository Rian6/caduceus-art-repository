"""Exercise commit batches and resumable pushes against a temporary local bare repository."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
def command(*args):
    return subprocess.run(list(map(str,args)),check=True,capture_output=True,text=True,encoding='utf-8')
def main():
    with tempfile.TemporaryDirectory(prefix='caduceus-git-batches-test-',dir=ROOT.parent) as directory:
        base=Path(directory)
        repo=base/'repo';remote=base/'remote.git'
        (repo/'tools').mkdir(parents=True)
        shutil.copyfile(ROOT/'tools/git_batches.py',repo/'tools/git_batches.py')
        (repo/'README.md').write_text('Test fixture\n',encoding='utf-8')
        (repo/'.gitignore').write_text('.validation/\n',encoding='utf-8')
        (repo/'catalogo').mkdir()
        assets=[]
        for number,size in enumerate([600000,300000,600000],69):
            gid=f'SLUS_212.{number}'
            relative=f'PS2/{gid}/{gid}_COV.png'
            path=repo/relative;path.parent.mkdir(parents=True)
            path.write_bytes(bytes([number])*size)
            assets.append({'path':relative,'bytes':size,'gameId':gid})
        (repo/'catalogo/index.json').write_text(json.dumps({'distribution':'runtime'}),encoding='utf-8')
        (repo/'catalogo/assets.jsonl').write_text(''.join(json.dumps(a)+'\n' for a in assets),encoding='utf-8')
        command('git','init','--initial-branch=main',repo)
        command('git','-C',repo,'config','user.name','Caduceus Art Test')
        command('git','-C',repo,'config','user.email','validation@example.invalid')
        tool=[sys.executable,repo/'tools/git_batches.py','--batch-mib','1']
        plan=json.loads(command(*tool).stdout)
        assert plan['assetCount']==3 and len(plan['batches'])==2
        assert all(batch['MiB']<=1 for batch in plan['batches'])
        assert not (repo/'.validation').exists(),'Planning mutated repository'
        command(*tool,'--prepare')
        state=json.loads((repo/'.validation/git-batches-state.json').read_text(encoding='utf-8'))
        assert state['complete'] and len(state['commits'])==4 and not state['pushed']
        first=head=command('git','-C',repo,'rev-parse','HEAD').stdout.strip()
        command(*tool,'--prepare')
        assert command('git','-C',repo,'rev-parse','HEAD').stdout.strip()==first
        command('git','init','--bare',remote)
        command('git','-C',repo,'remote','add','origin',remote)
        command(*tool,'--push')
        assert command('git','--git-dir='+str(remote),'rev-parse','refs/heads/main').stdout.strip()==head
        pushed=json.loads((repo/'.validation/git-batches-state.json').read_text(encoding='utf-8'))
        assert pushed['pushed']==4
        command(*tool,'--push')
        assert command('git','--git-dir='+str(remote),'rev-parse','refs/heads/main').stdout.strip()==head
    print('PASS: batch limits, non-mutating plan, local commits, repeated preparation and resumable local pushes')
if __name__=='__main__':main()
