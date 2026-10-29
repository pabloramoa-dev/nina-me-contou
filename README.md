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
   (uma máquina por parte, em paralelo): gera voz (**Kokoro Dora pf_dora, local**), lip sync, vídeo
   (Nina original/HyperFrames + acabamento Remotion), capa e a versão Story (≤59 s, mantendo o CTA final), e grava em `reels/`.
   Roteiro ou versão de render alterado depois do render volta sozinho pro estúdio (`reels/<id>.hash`).
3. O workflow **Publicar Reel** roda às 8h, 12h, 16h e 20h e publica o próximo da
   sequência: continuação pendente primeiro, depois a parte 1 do próximo episódio
   completo. Às 8h e às 20h publica também o Story.
   Nunca publica o mesmo vídeo duas vezes (`conteudo/publicados.json`).
4. **Vigia da fila** (6h30): se houver menos de 8 episódios prontos (4 dias), abre um aviso.
   O aviso agora significa falha de produção/render, porque os roteiros são reabastecidos automaticamente.
5. **Renovar a credencial** (segunda, 5h): renova o token de 60 dias sozinho.

## Voz principal da Nina (aprovada em 23/10/2026)

A voz principal agora é **Kokoro Dora (`pf_dora`)**, em português brasileiro,
com velocidade **1.02**, executada localmente no GitHub Actions, sem depender
do serviço Edge TTS. O código `motor/gerar_voz_kokoro.py` é a fonte padrão;
`NINA_VOICE_ENGINE=thalita` ou `voice_engine` no roteiro são opções explícitas
de reversão. A narração continua passando pelo master de áudio e o Rhubarb.

O novo renderizador final padrão é **Remotion**, usando o vídeo base da própria
Nina gerado pelo HyperFrames. Mantém os quadros animados no alto e as legendas
brancas soltas, com contorno e **posição inferior**, sem caixa escura.
`NINA_FINAL_COMPOSITOR=hyperframes` restaura o acabamento anterior sem
alterar os fluxos de publicação. Sem esse override, a publicação automática
usa o novo visual. A alteração da assinatura pede novos renders **somente
de vídeos ainda não publicados**, preservando o histórico das postagens.


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

## Motor base HyperFrames e acabamento final Remotion

Os próximos episódios usam o visual aprovado: Nina original, **voz Kokoro Dora**, varanda diurna ou noturna, recortes com fita e sombra, textura de papel, câmera, legendas com destaque, transições, mensagens, ilustrações animadas e trilha/efeitos originais sob a narração. A duração acompanha a fala, sem acelerar a voz para forçar um minuto.

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
# Ilustrações automáticas por cena

O compositor agora seleciona `story_frame_text` ou `story_frame_image` automaticamente.
O modo de imagem mantém o título e reserva um espaço central exclusivo para a arte,
sem legenda secundária no quadro. A fala continua na legenda dinâmica inferior.

O motor planeja de 4 a 8 cenas (seis por padrão), gera ilustrações cartoon coerentes
com as falas e registra cache, origem e falhas em `visual_images.json` de cada render.
Configuração: `motor/visual_images.json`; detalhes em [docs/visual-images.md](docs/visual-images.md).

**Ativação da API pendente:** o teste de 07/10/2026 detectou `OPENAI_API_KEY` ausente
nos secrets do repositório. Até cadastrar essa chave, novos episódios usam o fallback
configurado. O teste promocional de layout usa explicitamente seis imagens aprovadas;
isso não comprova geração nova pela API. A voz principal Kokoro Dora e a apresentadora original são preservadas.

## Cinema 2D nas historias da Nina (29/10/2026)

Aprovado a partir do piloto de cenas cinematograficas do Caixeiro. Os videos
novos da Nina ganham ilustrações 2D originais feitas com Pillow/CPU, cenarios
com profundidade, personagens secundarios FICTICIOS e objetos escolhidos a
partir do texto de cada cena (celular, fotos, aliança, carta, carro, casa etc.).
Nao existe chave de API paga nem necessidade de GPU para essas artes.

O Remotion, compositor final padrao, agora incorpora as imagens de apoio
na faixa superior e troca o quadro **a cada 7 segundos**, com movimento
suave de camera (pan/zoom). A apresentadora, a voz Kokoro Dora, o lip-sync
e as legendas inferiores continuam como antes. A composição HyperFrames
também utiliza o novo estilo nos quadros locais de reserva.

- Padrao: `NINA_STORY_STYLE=cinematic_2d`.
- Rollback: `NINA_STORY_STYLE=classic` (mantem acabamento anterior).
- Opcional por roteiro: `"visual_style": "classic"`.
- Imagens explicitamente aprovadas (`approved_visual_assets`) têm
  prioridade, inclusive no acabamento Remotion.
- `NINA_ALLOW_PAID_IMAGE_API=0` continua protegendo de custos por API.
- Nenhum fluxo de publicação ou configuração de conta foi alterado.
- A nova assinatura de render afeta apenas episodios pendentes, sem
  republicar os que ja saíram.

O movimento e feito na camera sobre ilustracoes 2D, nao e
animacao independente de braços/pernas dos personagens secundarios.
