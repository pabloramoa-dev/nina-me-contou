# Prompts pré-cadastrados da Nina

O acervo atual tem 369 roteiros (327 episódios, incluindo partes legadas, e 42 avulsos), com dez prompts por roteiro em `motor/prompts_banco.json`.

Os prompts são compilados localmente a partir das falas de cada cena, sem API de texto. A produção lê os prompts prontos, verifica a assinatura do roteiro e a cobertura das dez cenas, e usa os tempos reais da voz para exibi-las. A SiliconFlow continua responsável pelas imagens pagas; as verificações de origem e qualidade continuam obrigatórias.

Antes de produzir uma história nova ou modificada:

```sh
python tools/preparar_banco_prompts.py
python -m pytest -q tests/test_prompts_banco.py
```

Revise os prompts no JSON e salve o banco junto com as alterações do roteiro. Um roteiro ausente ou modificado bloqueia a produção antes de voz e imagens; não há geração automática por modelo de texto como alternativa.

O campo `bloqueados` documenta roteiros antigos que já não passam pela regra de antecipação. Seus prompts foram preparados a partir do texto existente, mas a produção permanece bloqueada pela mesma regra; após corrigir o gancho, compile novamente. Roteiros legados com imagens locais aprovadas ou configuração inferior a dez imagens também continuam sujeitos à política SiliconFlow existente.

Nenhuma imagem paga foi solicitada para preparar este banco. Os prompts mantêm o estilo revistinha moderna e o trecho literal de cada cena; sua qualidade visual final deve ser avaliada nas imagens geradas. Vozes, agenda e publicação não são alteradas.

## Atualização 04/11/2026 — prompts manuais em inglês e correções do pipeline

- Os 76 episódios da fila (ep113–ep187 e ep999) têm agora 10 prompts escritos à mão, em inglês, em `motor/prompts_episodios/epNNN.json` (ficha dos personagens, cenário e as 10 cenas). O FLUX.1-schnell da SiliconFlow entende inglês muito melhor e lê no máximo ~256 tokens, por isso a cena vem no começo do prompt. `tools/preparar_banco_prompts.py` usa esses arquivos com prioridade; roteiros sem arquivo manual continuam com o prompt compilado.
- A assinatura do banco passou a considerar só título + falas (`banco-historias-v2`). Antes, os campos visuais que o HyperFrames acrescenta às batidas (`arte`, `_visual_auto`) mudavam a assinatura e ~200 roteiros falhavam com "Roteiro sem prompts pré-cadastrados".
- `render_version.py` normaliza as variáveis `NINA_*` pelo tipo do JSON. O `.hash` gravado no render (com `NINA_IMAGE_RETRIES='0'` em texto) nunca batia com o da fila, então nenhum vídeo ficava "pronto" e o ep186 era renderizado de novo a cada rodada.
- Gancho de antecipação: os 20 roteiros bloqueados por "História sem pista específica" ganharam pergunta com substantivo concreto (ou frase neutra), e sumiu o "Mas o que dois tinha a ver com isso?".
- `motor/pendentes.py` pula roteiros que falhariam antes da voz, e o job `abastecer` recompila e grava o banco quando entram roteiros novos.
- Imagens: até 2 novas tentativas por cena (`image_retries: 2`) em erro de rede/429/5xx.
