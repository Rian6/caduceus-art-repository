# Publicar a distribuição pronta

Use **D:\caduceus-art-repository** para o repositório do servidor. A base
completa em **D:\caduceus-art-database** preserva os originais e extras.

A distribuição pronta tem aproximadamente 3,4 GiB de imagens. No GitHub,
um único push tem limite de 2 GiB; o envio inicial deve ser dividido em
lotes. [Documentação oficial do GitHub](https://docs.github.com/en/get-started/using-git/troubleshooting-the-2-gb-push-limit).

As imagens foram mantidas como arquivos Git comuns, permitindo que o servidor
busque diretamente os PNGs nos caminhos `PS2/<codigo>/...`.

## Preparação local

O envio inicial desta base foi preparado na branch `main` para
`https://github.com/Rian6/caduceus-art-repository`. Os comandos de preparação
abaixo servem para uma nova distribuição ainda sem commits.
O script abaixo, sem opções, somente mostra o plano; não grava commits nem envia arquivos:

```powershell
cd D:\caduceus-art-repository
python tools/git_batches.py
```

Para criar commits locais com lotes de até 400 MiB por grupo de artes:

```powershell
python tools/git_batches.py --prepare
```

Se o Git solicitar sua identificação, configure `user.name` e `user.email`
neste repositório usando seus próprios dados. A preparação mantém as artes
de cada código juntas e coloca o catálogo no último commit.

## Envio ao seu repositório

Crie um repositório remoto **vazio**, e configure a URL:

```powershell
git remote add origin https://github.com/Rian6/caduceus-art-repository.git
python tools/git_batches.py --push
```

O comando `--push` é a etapa que publica os arquivos. Ele envia um commit de
cada vez e registra o progresso em `.validation/`; pode ser repetido para
retomar um envio interrompido. Não usa force push e não redefine históricos.
Se o remoto já tiver commits, faça a reconciliação do histórico antes de usar
este fluxo inicial.

Depois da publicação, o catálogo ficará em:

```text
https://raw.githubusercontent.com/USUARIO/REPOSITORIO/main/catalogo/index.json
```

Passe o endereço do repositório para configurar a nova origem no servidor
Caduceus. Nesta preparação, nenhum arquivo foi publicado e nenhuma origem do
aplicativo foi alterada.
