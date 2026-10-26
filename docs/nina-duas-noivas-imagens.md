# Nina: As Duas Noivas do Mesmo Homem — imagens geradas

Este episódio avulso está em `avulsos/nina-20261026-duas-noivas-imagens.json`.

**Importante:** só executar/mesclar depois de incluir os arquivos PNG abaixo na mesma branch. A referência `approved_visual_assets` já foi preparada para que o motor use EXATAMENTE as imagens aprovadas, sem fazer uma nova geração pela API.

Caminhos obrigatórios na raiz do repositório:

- `assets/nina_duas_noivas/01-abertura-salao.png`
- `assets/nina_duas_noivas/02-revelacao-computador.png`
- `assets/nina_duas_noivas/03-aliancas-cafe.png`
- `assets/nina_duas_noivas/04-comprovantes-cafe.png`
- `assets/nina_duas_noivas/05-entrada-igreja.png`
- `assets/nina_duas_noivas/06-confronto-altar.png`
- `assets/nina_duas_noivas/07-viagem-amigas.png`

A oitava batida é o CTA obrigatório do canal e reutiliza a sétima imagem. O emparelhamento com as cenas é calculado com `target_images=8` em `visual_images.py`.

## Renderização oficial

Após anexar as artes e mesclar para `main`, a alteração em `avulsos/*.json` aciona `.github/workflows/avulso.yml`, o fluxo **Produzir vídeo avulso**. Ele executa `python motor/produzir.py`, com voz Kokoro Dora, personagem original, lip-sync HyperFrames e acabamento Remotion, e grava MP4/capa/Story em `avulsos_prontos/`. **Não publica** em Instagram ou TikTok.

A instalação da imagem no arquivo com caminho relativo à raiz é essencial; sem ela o motor registra `invalid_approved_asset` e pode renderizar sem a arte. Antes de renderizar, conferir se todos os sete PNGs estão presentes.

As artes originais podem ser fornecidas em um ZIP com a hierarquia `assets/nina_duas_noivas/` (criado na conversa ChatGPT) e enviadas ao GitHub nesta branch.
