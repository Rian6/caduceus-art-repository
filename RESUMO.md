# Entrega — 13/10/2026

Base de artes do [repositório Caduceus](https://github.com/Rian6/caduceus-art-repository).

| Conteúdo | Quantidade |
| --- | ---: |
| Códigos com arte disponível | 10.986 |
| Capas PNG 192×272 | 10.944 |
| Discos locais | 2.599 |
| Fundos PNG 640×480 | 14.659 |
| Total de imagens | 28.202 |
| Espaço das imagens | 3,36 GiB |

O catálogo tem os caminhos relativos, dimensões, tamanhos, SHA-256 e fontes.
Os fundos cobrem 5.959 códigos; os discos preservam a maior resolução local
disponível. Consulte `catalogo/cobertura.csv` para localizar um jogo pelo nome
ou código e identificar artes ausentes.

Os originais, capas 3D e demais extras foram preservados em
`D:\caduceus-art-database`, com 103.153 imagens e cerca de 14,44 GiB de imagens.
Os clones das fontes estão separados em `D:\caduceus-art-sources`.

Leia [README.md](README.md) para usar a base offline e [PUBLICAR.md](PUBLICAR.md)
para preparar uma nova distribuição. O envio inicial divide as artes em
**9 lotes de até 400 MiB**, mantendo todos os arquivos de cada código juntos.
O Git utiliza `main` e o remoto `Rian6/caduceus-art-repository`.

As 28.202 imagens e as referências dos manifestos passaram na validação de
formatos, dimensões, tamanhos e SHA-256, sem erros.
O instalador foi testado em uma pasta temporária. O envio em lotes foi testado
contra um repositório Git temporário local. A pasta `ART` dos seus jogos está
preservada. O código do servidor Caduceus foi configurado para buscar capas,
discos e fundos deste repositório. Downloads ausentes preservam as artes locais.
