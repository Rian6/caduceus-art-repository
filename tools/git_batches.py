"""Plan, prepare local commits or explicitly push a runtime repository in small batches."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
STATE=ROOT/'.validation/git-batches-state.json'
def git(*args,check=True,capture=True):
    return subprocess.run(['git','-C',str(ROOT),*args],check=check,
        capture_output=capture,text=capture,encoding='utf-8' if capture else None)
def save(state):
    STATE.parent.mkdir(parents=True,exist_ok=True)
    STATE.write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8')
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch-mib',type=int,default=400)
    parser.add_argument('--prepare',action='store_true',help='Creates local commits; does not upload')
    parser.add_argument('--push',action='store_true',help='Explicitly uploads prepared commits to the selected remote')
    parser.add_argument('--remote',default='origin')
    args=parser.parse_args()
    if not 1<=args.batch_mib<=1024:parser.error('Use lotes entre 1 e 1024 MiB.')
    index=json.loads((ROOT/'catalogo/index.json').read_text(encoding='utf-8'))
    if index.get('distribution')!='runtime':parser.error('Use esta ferramenta em D:/caduceus-art-repository, a distribuição runtime.')
    assets=[json.loads(line) for line in (ROOT/'catalogo/assets.jsonl').read_text(encoding='utf-8').splitlines()]
    grouped=defaultdict(list)
    for asset in assets:
        path=(ROOT/asset['path']).resolve()
        if not path.is_relative_to(ROOT) or not asset['path'].startswith('PS2/'):
            parser.error('Caminho de arte inválido.')
        if path.stat().st_size!=asset['bytes']:parser.error('Tamanho alterado; valide o catálogo antes de publicar.')
        if asset['bytes']>=100*1024**2:parser.error('Arquivo acima de 100 MiB; requer distribuição separada.')
        grouped[asset['gameId']].append(asset)
    limit=args.batch_mib*1024**2
    batches=[];current=[];size=0
    for gid,items in sorted(grouped.items()):
        total=sum(item['bytes'] for item in items)
        if total>limit:parser.error('As artes de '+gid+' excedem o tamanho do lote.')
        if current and size+total>limit:batches.append({'paths':current,'bytes':size});current=[];size=0
        current.extend(item['path'] for item in items);size+=total
    if current:batches.append({'paths':current,'bytes':size})
    plan={'assetCount':len(assets),'bytes':sum(a['bytes'] for a in assets),'batchMiB':args.batch_mib,
        'batches':[{'number':i,'files':len(batch['paths']),'MiB':round(batch['bytes']/1024**2,2)} for i,batch in enumerate(batches,1)]}
    print(json.dumps(plan,indent=2),flush=True)
    if not args.prepare and not args.push:return
    if not (ROOT/'.git').is_dir():parser.error('Execute git init --initial-branch=main nesta pasta.')
    state=json.loads(STATE.read_text(encoding='utf-8')) if STATE.exists() else None
    branch=git('symbolic-ref','--short','HEAD').stdout.strip()
    if args.prepare:
        if git('var','GIT_AUTHOR_IDENT',check=False).returncode:
            parser.error('Configure user.name e user.email no Git deste repositório antes de preparar os commits.')
        head=git('rev-parse','--verify','HEAD',check=False)
        if state is None:
            if head.returncode==0:parser.error('Esta preparação inicial requer o repositório local sem commits. Não redefine históricos existentes.')
            if git('diff','--cached','--name-only').stdout.strip():parser.error('Há arquivos previamente preparados no índice Git.')
            state={'branch':branch,'batchMiB':args.batch_mib,'commits':[],'complete':False,'pushed':0}
            save(state)
        else:
            if state['branch']!=branch or state['batchMiB']!=args.batch_mib:parser.error('A configuração difere da preparação anterior.')
            if state['commits'] and head.stdout.strip()!=state['commits'][-1]:parser.error('O histórico mudou depois da preparação. Nenhum histórico será sobrescrito.')
        control=[p.name for p in ROOT.iterdir() if p.name not in ['.git','.validation','PS2','catalogo','__pycache__','.cache'] and not p.name.endswith('.log')]
        stages=[control]+[batch['paths'] for batch in batches]+[['catalogo']]
        for number,paths in enumerate(stages):
            if number<len(state['commits']):continue
            pathspec=ROOT/'.validation/git-pathspec.bin'
            pathspec.write_bytes(b''.join(path.encode('utf-8')+b'\x00' for path in paths))
            git('add','--pathspec-from-file='+str(pathspec),'--pathspec-file-nul',capture=False)
            label='Documentação e ferramentas' if number==0 else 'Catálogo e cobertura' if number==len(stages)-1 else f'Artes PS2 - lote {number}/{len(batches)}'
            git('commit','-m',label,capture=False)
            state['commits'].append(git('rev-parse','HEAD').stdout.strip());save(state)
        state['complete']=True;save(state)
    if args.push:
        if not state or not state['complete']:parser.error('Prepare os commits com --prepare antes de enviar.')
        if state['branch']!=branch:parser.error('A branch mudou depois da preparação.')
        if git('rev-parse','HEAD').stdout.strip()!=state['commits'][-1]:parser.error('O histórico mudou depois da preparação.')
        git('remote','get-url',args.remote)
        for number,commit in enumerate(state['commits']):
            if number<state['pushed']:continue
            git('push',args.remote,commit+':refs/heads/'+branch,capture=False)
            state['pushed']=number+1;save(state)
        print('Envio dos lotes concluído.',flush=True)
if __name__=='__main__':main()
