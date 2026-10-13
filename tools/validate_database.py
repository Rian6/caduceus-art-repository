"""Verify every catalogued asset and the files selected by each game manifest."""
import hashlib
import io
import json
from pathlib import Path
import sys
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
def main():
    index=json.loads((ROOT/'catalogo/index.json').read_text(encoding='utf-8'))
    assets={}
    errors=[]
    total=0
    def check(asset):
        relative=asset['path']
        path=(ROOT/relative).resolve()
        try:
            assert path.is_relative_to(ROOT),'Path outside database'
            data=path.read_bytes()
            assert len(data)==asset['bytes'],'File size mismatch'
            assert hashlib.sha256(data).hexdigest()==asset['sha256'],'SHA-256 mismatch'
            with Image.open(io.BytesIO(data)) as image:
                assert image.size==(asset['width'],asset['height']),'Dimensions mismatch'
                if asset['kind'] in ['cover','disc','background']:
                    assert image.format=='PNG','OPL-ready asset is not a PNG'
                image.verify()
            return asset,len(data),None
        except Exception as error:return asset,0,{'path':relative,'error':str(error)}
    entries=[json.loads(line) for line in (ROOT/'catalogo/assets.jsonl').read_text(encoding='utf-8').splitlines()]
    with ThreadPoolExecutor(max_workers=8) as workers:
        for number,(asset,size,error) in enumerate(workers.map(check,entries),1):
            if error:errors.append(error)
            elif asset['path'] in assets:errors.append({'path':asset['path'],'error':'Duplicate asset path'})
            else:assets[asset['path']]=asset;total+=size
            if number%5000==0:print(f'Validando: {number} imagens',flush=True)
    for gid,reference in index['games'].items():
        try:
            game=json.loads((ROOT/reference['manifest']).read_text(encoding='utf-8'))
            assert game['id']==gid
            for kind in ['cover','disc','background']:
                asset=game[kind]
                assert reference[kind]==(asset['path'] if asset else None)
                if asset:
                    assert assets[asset['path']]==asset
                    assert asset['gameId']==gid
                    if kind=='cover':assert (asset['width'],asset['height'])==(192,272)
                    if kind=='background':assert (asset['width'],asset['height'])==(640,480)
                    if kind=='disc':assert asset['source']['id']=='local-disc-pack'
            for asset in game['backgrounds']+game['extras']+game['alternatives']['covers']+game['alternatives']['discs']:
                assert assets[asset['path']]==asset
        except Exception as error:errors.append({'id':gid,'error':str(error)})
    if len(assets)!=index['summary']['assets']:errors.append({'error':'Asset count mismatch'})
    if total!=index['summary']['bytes']:errors.append({'error':'Total bytes mismatch'})
    result={'valid':not errors,'games':len(index['games']),'assets':len(assets),'bytes':total,'errors':errors}
    print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
    output=ROOT/'.validation/integrity.json'
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if errors:sys.exit(1)
if __name__=='__main__':main()
