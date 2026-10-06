# Nina Me Contou — Skill canônica

Use este arquivo como fonte de verdade ao trabalhar no projeto `pabloramoa-dev/nina-me-contou`.

## Identidade

- Personagem: **Nina**.
- Canal: **@ninamecontou**.
- Formato: Reels/Shorts verticais com histórias ficcionais em duas partes.
- Visual oficial: personagem original da Nina, varanda, estética de recortes/papel e composição **HyperFrames**.
- HyperFrames é o compositor padrão; Manim puro é apenas fallback/legado explícito.

## Voz oficial — regra obrigatória

- Voz definitiva da Nina: **Microsoft `pt-BR-ThalitaNeural`**.
- Velocidade oficial: **`-6%`**.
- Gerador: `motor/gerar_voz_thalita.py`.
- Entrada do pipeline: `motor/produzir.py`.
- Não trocar automaticamente para Dora/Kokoro em produção.
- `motor/gerar_voz_kokoro.py` permanece somente como legado/manual.
- Se houver mudança futura de voz, atualizar também `motor/render_version.py` para invalidar renders ainda não publicados.

## Pipeline visual obrigatório

O padrão aprovado inclui:

- animações HyperFrames;
- movimentos de câmera;
- transições;
- legendas destacadas e sincronizadas;
- lip sync por fonema com Rhubarb (`motor/lipsync_rhubarb.py`, 8 bocas em `nina_lib.boca_fonema`), com queda automática para amplitude;
- visual v4 (`motor/visual_v4.py`): legenda pílula karaokê, partículas nas palavras de impacto, título manuscrito com marca-texto, slam nas batidas `chocada`;
- voz masterizada com Pedalboard (`motor/audio_fx.py`), trilha com ducking e efeitos sonoros sintetizados (`motor/sfx.py`) presos às animações;
- palavra falada com destaque amarelo + pulo de escala; flash + impacto nas batidas `chocada`;
- CTA somente no final;
- capa e Story gerados a partir do mesmo episódio;
- duração acompanhando a fala, sem acelerar a voz apenas para caber em um minuto;
- **fotos reais de banco de imagens** em polaroid colada (`motor/banco_imagens.py`), baixadas sozinhas a cada render;
- **uma única legenda de fala**: a narração aparece somente na legenda dinâmica inferior; o cartão superior fica reservado ao título/arte curta;
- **apoio visual automático**: batidas textuais sem arte curta tentam inferir objetos/lugares da fala (carro/viatura, celular, calendário, prédio, mala, mapa etc.), com foto quando disponível e ilustração local como fallback.

## Fotos reais (banco de imagens)

- O motor baixa as fotos sozinho no render (Pexels/Pixabay se houver secret, senão Openverse CC0 sem chave).
- Batidas com arte de objeto (aliança, relógio, carro, porta, celular, café, mala, perfume...) viram foto automaticamente; o texto curto da arte vira a legenda da polaroid.
- Ao escrever roteiros novos, prefira pedir a foto exata da cena com `"foto"` (busca em **inglês**, objeto ou lugar concreto):
  `"foto": "glove compartment car"` ou `"foto": ["velvet ring box", "CAIXINHA"]`. Funciona até em batida sem `arte`.
- Nunca pedir foto de pessoa/rosto (a história é ficção de traição). Pessoas, títulos, conversas, manchetes, coração, interrogação e extrato continuam ilustrados.
- `"foto": false` numa batida mantém a ilustração. `NINA_FOTOS=0` desliga tudo.

## Fluxo de produção

1. Roteiro em `episodios/epNNN-p1.json` e `episodios/epNNN-p2.json`.
2. `motor/produzir.py` gera a narração Thalita, masteriza com Pedalboard e grava `segs.json`.
3. `motor/lipsync_rhubarb.py` produz o lip sync (fallback `lipsync_amplitude.py`).
4. `motor/hyperframes.py` compõe o vídeo final.
5. O workflow `.github/workflows/produzir.yml` grava MP4, capa e Story em `reels/`.
6. `src/fila.py` só considera pronto o material cuja assinatura corresponde à versão atual do render.

## Proteções

- Não alterar a aparência original da Nina sem pedido explícito.
- Não remover HyperFrames do padrão.
- Não retirar o CTA final.
- Não publicar parte 1 sem a parte 2 estar pronta.
- Não reaproveitar uma voz antiga em novos episódios.
- Preservar histórico de publicações ao invalidar renders antigos.

## Configuração atual

- Render version: `nina-hyperframes-thalita-6-legenda-unica-visuais`.
- Voz: `pt-BR-ThalitaNeural`.
- Rate: `-6%`.
- Gap entre batidas: `0.25s`.
- Saída de voz: WAV mono 44.1 kHz, masterizado (Pedalboard) antes do lip sync/render.
- Novos efeitos sonoros: acrescentar em `motor/sfx.py` (SONS, VOLUME e eventos) mantendo sincronia com `compor()`.
