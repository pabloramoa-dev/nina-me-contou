# Nina Me Contou — piloto automático

Canal @ninamecontou (Instagram). Histórias FICCIONAIS de traição contadas pela
Nina, em duas partes. **4 vídeos por dia: 8h, 12h, 16h e 20h** (horário de Brasília),
sempre em sequência — 8h parte 1, 12h parte 2, 16h parte 1, 20h parte 2 (2 episódios/dia).
Os vídeos das **8h e das 20h também vão para os Stories**. Todo vídeo termina com o
CTA de seguir pra não perder a continuação (`motor/cta.py`).

## Como funciona

1. O workflow **Produzir episódios** começa pelo abastecedor automático
   (`motor/gerar_roteiros.py`), que mantém **60 histórias completas** na reserva.
   O plano anual possui **730 histórias / 1.460 vídeos**, suficientes para 365 dias no ritmo atual.
   Cada história entra em `episodios/` como `epNNN-p1.json` + `epNNN-p2.json`.
2. Na mesma execução, o estúdio pega os roteiros ainda sem MP4
   (uma máquina por parte, em paralelo): gera voz (**Thalita Neural pt-BR**), lip sync, vídeo
   (personagem Manim + composição HyperFrames), capa e a versão Story (≤59 s, mantendo o CTA final), e grava em `reels/`.
   Roteiro ou versão de render alterado depois do render volta sozinho pro estúdio (`reels/<id>.hash`).
3. O workflow **Publicar Reel** roda às 8h, 12h, 16h e 20h e publica o próximo da
   sequência: continuação pendente primeiro, depois a parte 1 do próximo episódio
   completo. Às 8h e às 20h publica também o Story.
   Nunca publica o mesmo vídeo duas vezes (`conteudo/publicados.json`).
4. **Vigia da fila** (6h30): se houver menos de 8 episódios prontos (4 dias), abre um aviso.
   O aviso agora significa falha de produção/render, porque os roteiros são reabastecidos automaticamente.
5. **Renovar a credencial** (segunda, 5h): renova o token de 60 dias sozinho.

## Voz oficial da Nina

A voz definitiva é **Microsoft `pt-BR-ThalitaNeural`**, com velocidade **`-6%`**.
O gerador canônico é `motor/gerar_voz_thalita.py` e `motor/produzir.py` chama esse motor por padrão.
Kokoro/Dora permanece apenas como código legado/manual e não deve ser usado na produção normal.
A troca de voz altera a versão de render, portanto vídeos ainda não publicados feitos com Dora retornam automaticamente ao estúdio para serem refeitos com Thalita.

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

Os próximos episódios usam o visual aprovado: Nina original, **voz Thalita**, varanda diurna ou noturna, recortes com fita e sombra, textura de papel, câmera, legendas com destaque, transições, mensagens, ilustrações animadas e trilha/efeitos originais sob a narração. A duração acompanha a fala, sem acelerar a voz para forçar um minuto.

Instale `requirements-estudio.txt`, execute `npm ci --prefix video` e `cd video && npx --no-install hyperframes browser ensure`. O workflow instala tudo automaticamente. Exporte normalmente com `python motor/produzir.py episodios/epNNN-p1.json --publicar-em saida_reels`.

As artes existentes do roteiro são preservadas, inclusive imagens `.b64` e todo o catálogo `objetos.py`. Títulos e painéis são derivados das falas; opcionalmente, cada batida pode trazer `"hf": {"titulo": "Texto curto", "selo": "Uma pista"}`. Não há frases fixas do episódio de teste nos próximos vídeos.

A assinatura da fila inclui a versão visual/voz. Os vídeos ainda não publicados com o motor antigo retornam ao estúdio; o histórico de publicação é preservado. Só entram na fila as duas partes prontas. O CTA continua exclusivamente no final. Capa e Story acompanham o novo render.

`NINA_MOTOR=manim` permite usar o motor anterior em uma execução explícita. HyperFrames é o padrão. Telemetria do compositor está desativada no estúdio e no CI. O workflow **Validar Nina HyperFrames** testa a composição, renderização, voz, capa e Story sem publicar.

## Som e acabamento (v3)

- **Voz:** a narração da Thalita passa pela cadeia do **Spotify Pedalboard** (`motor/audio_fx.py`): corte de grave, presença, compressão suave, ambiência curtinha de varanda e limitador. A duração não muda, então legenda e lip sync seguem iguais. Sem o pedalboard instalado, volta sozinho para o filtro ffmpeg antigo.
- **Trilha:** a mesma trilha original, abafada e com *ducking* — abaixa quando a Nina fala e volta nas pausas.
- **Efeitos sonoros** (`motor/sfx.py`), sintetizados por código (estilo sfxr, sem arquivos de terceiros nem licença) e presos às animações: papel + pop na entrada de cada cartão, whoosh no wipe amarelo, impacto + flash nas batidas com `"expr": "chocada"`, notificação em `celular`/`direct`/`notificacao`, digitação em `conversa`, tique-taque no `relogio`, tum-tum no `coracao`, portão na `porta`, passagem grave no `carro` e brilho no confete final.
- **Legenda:** a palavra falada fica amarela e dá um pulinho de escala.
- **Flash:** clarão de papel nas batidas `chocada`.

Para o flash e o impacto, basta marcar a batida com `"expr": "chocada"` no roteiro.

## Visual v4 (padrão desde out/2026)

Blocos do catálogo HyperFrames adaptados ao estilo papel da Nina (`motor/visual_v4.py`):

- **Legenda pílula (karaokê):** até 4 palavras num cartão claro; as palavras escurecem conforme a Nina fala.
- **Palavras de impacto:** ficam vermelhas, crescem e soltam partículas, com um "pop" no som. Escolhidas automaticamente; para escolher no roteiro: `"hf": {"destaque": ["Paula"]}`.
- **Título manuscrito** (fonte Caveat, OFL) escrito na hora, com traço de marca-texto por baixo.
- **Headline slam** nas batidas `"expr": "chocada"`: o título despenca com tremida.
- **Boca por fonema** com Rhubarb Lip Sync (MIT, modo fonético): 8 formatos de boca. Sem o Rhubarb, cai sozinho no lip sync por volume.

Para voltar ao visual anterior numa execução: `NINA_VISUAL=v3` e/ou `NINA_LIP=amplitude`.

## Fotos reais (v5)

Os objetos da história (aliança, relógio, carro, porta, celular, café, mala, perfume…) aparecem como **foto real em polaroid colada**, com tom de papel, granulado, fita e legenda. O motor (`motor/banco_imagens.py`) **baixa sozinho** as fotos de cada episódio no render — nada a fazer à mão.

- Fonte: Pexels e Pixabay se existirem os secrets `PEXELS_API_KEY` / `PIXABAY_API_KEY` (opcionais, gratuitos); sem eles, Openverse (só CC0, StockSnap/Rawpixel). Sem atribuição obrigatória; créditos ficam em `saida/<id>/fotos.json` e no log.
- Roteiro: `"foto": "busca em inglês"` ou `"foto": ["busca", "LEGENDA"]` pede a foto exata; sem isso, as artes de objeto usam a busca padrão (`FOTO_PADRAO`).
- Resultados com pessoas, ilustrações ou recortes são descartados. Se a busca falhar, a batida volta para a ilustração.
- `"foto": false` mantém a ilustração naquela batida; `NINA_FOTOS=0` desliga.
