"""Install selected games from this database to an OPL ART directory (offline)."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil

ROOT=Path(__file__).resolve().parents[1]
def normalize(value):
    match=re.fullmatch(r'([A-Z0-9]{4})[-_](\d{3})\.?([0-9]{2})',value.strip(),re.I)
    if not match:raise ValueError('Código inválido: '+value)
    return f'{match[1].upper()}_{match[2]}.{match[3]}'
def safe_source(relative):
    path=(ROOT/relative).resolve()
    if not path.is_relative_to(ROOT):raise ValueError('Arquivo fora da base: '+relative)
    return path
def plan(ids, art):
    index=json.loads((ROOT/'catalogo/index.json').read_text(encoding='utf-8'))
    operations=[]
    missing=[]
    for gid in sorted(set(normalize(value) for value in ids)):
        info=index['games'].get(gid)
        if not info:missing.append({'id':gid,'reason':'Jogo ausente na base'});continue
        game=json.loads(safe_source(info['manifest']).read_text(encoding='utf-8'))
        for kind,suffix in [('cover','COV'),('disc','ICO'),('background','BG')]:
            asset=game[kind]
            if asset:operations.append((asset,art/f'{gid}_{suffix}.png'))
            else:missing.append({'id':gid,'reason':'Arte ausente: '+kind})
        for asset in game['backgrounds']:
            if re.fullmatch(re.escape(gid)+r'_BG_0[1-6]\.png',Path(asset['path']).name):
                operations.append((asset,art/Path(asset['path']).name))
    return operations,missing
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--art-dir',type=Path,required=True,help='Destino ART do compartilhamento PS2')
    parser.add_argument('--ids',nargs='+',default=[])
    parser.add_argument('--ids-file',type=Path,help='TXT com um código por linha; # inicia comentário')
    parser.add_argument('--dry-run',action='store_true',help='Exibe o plano sem gravar arquivos')
    parser.add_argument('--overwrite',action='store_true',help='Substitui artes diferentes já existentes')
    parser.add_argument('--report',type=Path,help='Grava relatório JSON fora da base')
    args=parser.parse_args()
    ids=list(args.ids)
    if args.ids_file:
        ids.extend(line.split('#',1)[0].strip() for line in args.ids_file.read_text(encoding='utf-8-sig').splitlines() if line.split('#',1)[0].strip())
    if not ids:parser.error('Informe --ids ou --ids-file.')
    art=args.art_dir.resolve()
    if art==ROOT or art.is_relative_to(ROOT):parser.error('Use um destino ART fora da pasta da base.')
    operations,missing=plan(ids,art)
    results=[]
    for asset,target in operations:
        source=safe_source(asset['path'])
        digest=hashlib.sha256(source.read_bytes()).hexdigest()
        if digest!=asset['sha256']:raise SystemExit('Falha de integridade: '+asset['path'])
        same=target.is_file() and hashlib.sha256(target.read_bytes()).hexdigest()==digest
        if same:status='unchanged'
        elif target.exists() and not args.overwrite:status='preserved'
        elif args.dry_run:status='would-copy'
        else:
            art.mkdir(parents=True,exist_ok=True)
            temp=target.with_name(target.name+'.caduceus-art.tmp')
            shutil.copyfile(source,temp)
            temp.replace(target)
            status='copied'
        results.append({'source':asset['path'],'destination':str(target),'status':status,'bytes':asset['bytes']})
    report={'dryRun':args.dry_run,'overwrite':args.overwrite,'files':results,'missing':missing}
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
