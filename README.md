# Nina Me Contou — piloto automático

Canal @ninamecontou (Instagram). Histórias FICCIONAIS de traição contadas pela
Nina, em duas partes. **4 vídeos por dia: 8h, 12h, 16h e 20h** (horário de Brasília),
sempre em sequência — 8h parte 1, 12h parte 2, 16h parte 1, 20h parte 2 (2 episódios/dia).
Os vídeos das **8h e das 20h também vão para os Stories**. Todo vídeo termina com o
CTA de seguir pra não perder a continuação (`motor/cta.py`).

## Como funciona

1. Você (ou o Claude) põe roteiros novos em `episodios/` — sempre em par:
   `epNNN-p1.json` + `epNNN-p2.json`.
2. O workflow **Produzir episódios** roda sozinho a cada push em `episodios/`
   (uma máquina por parte, em paralelo): gera voz (Kokoro), lip sync, vídeo
   (personagem Manim + composição HyperFrames), capa e a versão Story (≤59 s, mantendo o CTA final), e grava em `reels/`.
   Roteiro editado depois do render volta sozinho pro estúdio (`reels/<id>.hash`).
3. O workflow **Publicar Reel** roda às 8h, 12h, 16h e 20h e publica o próximo da
   sequência: continuação pendente primeiro, depois a parte 1 do próximo episódio
   completo. Às 8h e às 20h publica também o Story.
   Nunca publica o mesmo vídeo duas vezes (`conteudo/publicados.json`).
4. **Vigia da fila** (6h30): se houver menos de 4 episódios prontos (2 dias), abre um aviso.
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

Actions → **Publicar Reel** → Run workflow → horário `manha`, ensaio marcado.
O log mostra qual episódio sairia, o link do vídeo e da capa, sem publicar.

História de ficção, inspirada em causo de família.


## Visual padrão: HyperFrames

Os próximos episódios usam o visual aprovado: Nina e voz Dora originais, varanda diurna ou noturna, recortes com fita e sombra, textura de papel, câmera, legendas com destaque, transições, mensagens, ilustrações animadas e trilha/efeitos originais sob a narração. A duração acompanha a fala, sem acelerar a voz para forçar um minuto.

Instale `requirements-estudio.txt`, execute `npm ci --prefix video` e `cd video && npx --no-install hyperframes browser ensure`. O workflow instala tudo automaticamente. Exporte normalmente com `python motor/produzir.py episodios/epNNN-p1.json --publicar-em saida_reels`.

As artes existentes do roteiro são preservadas, inclusive imagens `.b64` e todo o catálogo `objetos.py`. Títulos e painéis são derivados das falas; opcionalmente, cada batida pode trazer `"hf": {"titulo": "Texto curto", "selo": "Uma pista"}`. Não há frases fixas do episódio de teste nos próximos vídeos.

A assinatura da fila inclui a versão visual. Os vídeos ainda não publicados com o motor antigo retornam ao estúdio; o histórico de publicação é preservado. Só entram na fila as duas partes prontas. O CTA continua exclusivamente no final. Capa e Story acompanham o novo render.

`NINA_MOTOR=manim` permite usar o motor anterior em uma execução explícita. HyperFrames é o padrão. Telemetria do compositor está desativada no estúdio e no CI. O workflow **Validar Nina HyperFrames** testa a composição, renderização, voz, capa e Story sem publicar.
