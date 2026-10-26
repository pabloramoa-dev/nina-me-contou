# Nina: As Duas Noivas do Mesmo Homem — ilustrações aprovadas

Roteiro avulso: `avulsos/nina-20261026-duas-noivas-imagens.json`.

**As 7 imagens originais foram transferidas e verificadas no GitHub**, na pasta `assets/nina_duas_noivas/`, em 26/10/2026.

| Cena | Arquivo |
| --- | --- |
| Abertura no salão | `01-abertura-salao.png` |
| Revelação no computador | `02-revelacao-computador.png` |
| As duas noivas na cafeteria | `03-aliancas-cafe.png` |
| Comprovantes de empréstimo | `04-comprovantes-cafe.png` |
| Entrada na igreja | `05-entrada-igreja.png` |
| Confronto no altar | `06-confronto-altar.png` |
| Férias das amigas | `07-viagem-amigas.png` |

O pipeline oficial lê `approved_visual_assets` no JSON, conserva as imagens sem geração adicional por API e sincroniza cada quadro com a fala. A oitava batida é o CTA obrigatório acrescentado automaticamente por `motor/cta.py`, que reutiliza a última imagem.

O workflow `.github/workflows/avulso.yml` é acionado em `main` quando há novo roteiro avulso. Produz com `motor/produzir.py`: Nina original, voz Kokoro Dora `pf_dora`, lip-sync, HyperFrames e Remotion, resultando em MP4/capa/Story. O avulso **não é publicado nas redes sociais** nem entra na fila automática de episódios.

Após o render, verificar as imagens em `saida/<id>/visual_images.json` (origem: `approved_asset`) e o MP4 no artifact e em `avulsos_prontos/`.
