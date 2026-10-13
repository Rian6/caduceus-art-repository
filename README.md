# Caduceus — artes prontas para PS2

Distribuição para publicação e uso pelo servidor Caduceus. Inclui capas PNG
192×272, discos locais na melhor resolução disponível e fundos PNG 640×480.
As imagens ficam em `PS2/<codigo>/`, com os nomes OPL `_COV`, `_ICO`, `_BG`
e variantes `_BG_01` a `_BG_06` quando disponíveis.

Consulte `catalogo/index.json` e `catalogo/jogos/<codigo>.json`. Os caminhos
são relativos à raiz, com dimensões, tamanho, SHA-256 e procedência.
`catalogo/cobertura.csv` lista quais artes existem por código.

Instalação offline (Python 3.10+):

```powershell
python tools/install_art.py --art-dir "D:/smb-server/jogos/PS2/ART" --ids SLUS_212.69 --dry-run
python tools/install_art.py --art-dir "D:/smb-server/jogos/PS2/ART" --ids SLUS_212.69
```

Arquivos existentes são preservados. Use `--overwrite` para substituir.
Os originais, capas 3D, screenshots e demais extras permanecem na base
completa em `D:/caduceus-art-database`, separados desta distribuição.

Fontes e commits estão em `catalogo/fontes.json`, e os créditos em `creditos/`.
Capas: xlenore/ps2-covers. Fundos: Luden02/psx-ps2-opl-art-database / OPL Manager.
Discos: coleção local NTSC Hi-Res 8-bit e complemento regional.
As artes pertencem aos respectivos titulares; não se atribui licença nova.

Para validar: instale `tools/requirements.txt` e execute
`python tools/validate_database.py`. O servidor Caduceus será configurado
para o endereço deste repositório em uma etapa posterior.

## Publicação

Consulte [PUBLICAR.md](PUBLICAR.md) para preparar commits e enviar as imagens
em lotes. `python tools/git_batches.py` mostra o plano sem criar commits ou
publicar arquivos. O Git local está inicializado em `main`, sem endereço remoto.
