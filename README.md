# Nina Me Contou — piloto automático

Canal @ninamecontou (Instagram). Histórias FICCIONAIS de traição contadas pela
Nina, em duas partes: **parte 1 às 12h, parte 2 às 20h** (horário de Brasília).

## Como funciona

1. Você (ou o Claude) põe roteiros novos em `episodios/` — sempre em par:
   `epNNN-p1.json` + `epNNN-p2.json`.
2. O workflow **Produzir episódios** roda sozinho a cada push em `episodios/`:
   gera voz (Kokoro), lip sync, vídeo (Manim) e capa, e grava em `reels/`.
3. O workflow **Publicar Reel** roda às 12h e às 20h:
   - 12h: parte 1 do próximo episódio completo (as duas partes já renderizadas);
   - 20h: a parte 2 do episódio que saiu ao meio-dia.
   Nunca publica o mesmo vídeo duas vezes (`conteudo/publicados.json`).
4. **Vigia da fila** (8h): se houver menos de 3 episódios prontos, abre um aviso.
5. **Renovar a credencial** (segunda, 5h): renova o token de 60 dias sozinho.

## Configuração (uma vez)

Settings → Secrets and variables → Actions

| Tipo | Nome | Valor |
|---|---|---|
| Secret | `IG_USER_ID_NINA` | ID da conta do Instagram @ninamecontou |
| Secret | `IG_ACCESS_TOKEN_NINA` | token do app "Nina Me Contou bot" |
| Secret | `GH_PAT` | PAT clássico com escopo `repo` (renovação do token) |
| Variable | `RAW_BASE_URL` | `https://raw.githubusercontent.com/pabloramoa-dev/nina-me-contou/main` |
| Variable | `GRAPH_API_VERSION` | `v22.0` |
| Variable | `PUBLICAR_ATIVO` | `false` até o ensaio passar; depois `true` |

O repositório precisa ser **público** (o Instagram baixa o vídeo pelo link raw).

## Testar antes de ligar

Actions → **Publicar Reel** → Run workflow → horário `almoco`, ensaio marcado.
O log mostra qual episódio sairia, o link do vídeo e da capa, sem publicar.

História de ficção, inspirada em causo de família.
