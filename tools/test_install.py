"""Check real sample installation without changing the user's installed ART."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
tool=ROOT/'tools/install_art.py'
def execute(*args):
    result=subprocess.run([sys.executable,str(tool),*map(str,args)],capture_output=True,text=True,encoding='utf-8',check=True)
    return json.loads(result.stdout)
def main():
    with tempfile.TemporaryDirectory(prefix='caduceus-art-validation-',dir=ROOT.parent) as directory:
        art=Path(directory)/'ART'
        args=['--art-dir',art,'--ids','SLUS-21269','SLUS_212.69','SLES_525.85','ZZZZ_000.00']
        report=execute(*args,'--dry-run')
        assert not art.exists(),'Dry run changed the filesystem'
        assert any(item['id']=='ZZZZ_000.00' for item in report['missing'])
        targets=[f['destination'] for f in report['files']]
        assert len(set(targets))==len(targets),'Duplicate installs for aliased IDs'
        installed=execute(*args)
        assert any(f['status']=='copied' for f in installed['files'])
        for file in installed['files']:
            assert Path(file['destination']).read_bytes()==(ROOT/file['source']).read_bytes()
        repeated=execute(*args)
        assert all(f['status']=='unchanged' for f in repeated['files'])
        disc=art/'SLUS_212.69_ICO.png'
        assert disc.exists()
        disc.write_bytes(b'existing-custom-art')
        preserved=execute(*args)
        assert disc.read_bytes()==b'existing-custom-art'
        assert any(f['status']=='preserved' for f in preserved['files'])
        replaced=execute(*args,'--overwrite')
        assert disc.read_bytes()==(ROOT/'PS2/SLUS_212.69/SLUS_212.69_ICO.png').read_bytes()
        assert any(f['status']=='copied' for f in replaced['files'])
    print('PASS: offline installation, serial aliases, dry run, missing games, hashes, idempotence, preservation and overwrite')
if __name__=='__main__':main()
