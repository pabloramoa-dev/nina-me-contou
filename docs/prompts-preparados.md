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
