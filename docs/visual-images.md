# Ilustrações automáticas da Nina

Todas as entradas de `motor/produzir.py` usam o mesmo preparo de cenas e o compositor HyperFrames.
O padrão em `motor/visual_images.json` gera seis ilustrações (mínimo 4, máximo 8),
alinhadas às batidas reais da voz. Roteiros com poucas batidas são divididos antes
da narração sem alterar suas palavras. Roteiros minúsculos sem material para quatro
cenas usam menos cenas, registrado no manifesto.

O estilo é cartoon editorial premium, adesivo recortado, cores vibrantes, contorno
escuro limpo, volume suave, composição central e fundo transparente. As imagens
não contêm títulos, legendas ou letras. A apresentadora original não é redesenhada.

## Ativação e configuração

Os workflows de produção, avulso e avulso rápido recebem o secret `OPENAI_API_KEY`.
A chave precisa ter acesso ao modelo de imagem e saldo/crédito na API. A integração
usa `POST /v1/images/generations`; nenhum segredo é gravado nos relatórios.

Configuração global: `motor/visual_images.json`. Sobrescrita por episódio:

```json
"visual_images": {
  "auto_visual_images": true,
  "hide_inner_caption_when_image": true,
  "bottom_caption_only": true,
  "min_images": 4,
  "max_images": 8,
  "target_images": 6,
  "fallback": "story_frame_text"
}
```

Cada chave também aceita variável `NINA_` + nome em maiúsculas, por exemplo
`NINA_AUTO_VISUAL_IMAGES=0`. Modelo, qualidade, tamanho, timeout e retries
estão no mesmo arquivo. O desligamento retorna ao banco de imagens anterior.

## Templates e falhas

- `story_frame_image`: título preservado em uma linha de layout própria;
  ilustração centralizada com `object-fit: contain` em outra área, sem texto interno.
  A imagem entra suavemente sem rotação ou zoom para fora dos limites.
- `story_frame_text`: usado quando não há imagem disponível. A fala permanece
  apenas na legenda inferior com `bottom_caption_only=true`. Textos curtos de
  apoio podem ser habilitados no modo de texto com `bottom_caption_only=false`.
- `hide_inner_caption_when_image=true` impede a criação de texto secundário em
  cenas com imagem. O template de imagem sempre reserva a área integral à imagem.
- `fallback=story_frame_text` mantém o título e a legenda inferior quando a API
  falha. `original_art` mantém o catálogo original como alternativa.

Cache por hash de roteiro completo, cena, estilo, modelo e qualidade dentro de
`saida/<id>/visual_cache/`. Não usa imagens de outro roteiro nem esconde falhas
como gerações bem-sucedidas. Cada execução produz `visual_images.json` com cenas,
tempos, prompts, origem (`generated`/`cache`) e motivo dos fallbacks. `render.json`
resume as quantidades. Arquivos de imagem não são versionados automaticamente.

O teste promocional usa a voz Kokoro `pf_dora` já escolhida naquele roteiro;
a voz padrão Thalita e as publicações regulares permanecem como configuradas.
O workflow de aprovação tem permissão somente de leitura, entrega artifacts
temporários e não coloca o teste na fila nem publica nas redes sociais.
