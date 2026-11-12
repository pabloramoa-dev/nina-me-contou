# Nina: listas rápidas de 3 sinais (12h e 15h)

A partir de 12/11/2026, o canal tem **três Reels por dia (BRT)**:
- **9h:** história única longa, aproximadamente 3 minutos, sem mudar personagem e voz.
- **12h:** "Nina: 3 sinais de que..." (alvo 20–30 s, limite estrito de 59,9 s).
- **15h:** listas sobre amizades, limites, convivência e relacionamentos (alvo 20–45 s, limite estrito de 59,9 s).

A automação prepara um estoque de dez dias de roteiros curtos originais, 2 por dia. Os temas são alternados sem repetição no período de reserva. O fluxo de produção mantém Nina, Kokoro Dora, HyperFrames, Remotion, os dez prompts e dez imagens obrigatórias da SiliconFlow. A abertura é o próprio gancho (sem cartão introdutório), seguida de três pontos rápidos e um CTA único de envio. As cenas podem trocar rápido, mas as legendas devem permanecer legíveis.

O comando `python motor/listas_virais.py --dias 10` cria apenas roteiros que ainda não existem; não edita os já publicados. O workflow "Produzir episódios" compila o banco de dez prompts por roteiro e prepara o estoque misto com ao menos quatro Reels longos e quatro curtos. A fila não mistura formatos: 9h aceita apenas história, 12h e 15h apenas lista curta. Duração acima de 59,9 s é bloqueada antes de publicar. O recuperador grava o slot no histórico e faz tentativas de recuperação sem antecipar os horários.

## Pesquisa editorial inicial (11/11/2026)

- [Meta — métricas de watch time e ganchos](https://about.fb.com/news/2023/04/instagram-reels-trending-audio-and-gifts-updates/): observar tempo médio, replays e ponto de abandono.
- [Metricool — guia de Reels 2026](https://metricool.com/instagram-reels-guide/): a combinação de gancho inicial, originalidade e compartilhamento.
- [FBI Law Enforcement Bulletin — limites dos sinais de mentira](https://leb.fbi.gov/articles/featured-articles/the-truth-about-lying-what-investigators-need-to-know): não existe gesto isolado capaz de provar que alguém mente.

**Limites editoriais:** listas originais, sem copiar vídeos da Internet, sem afirmar que um sinal isolado confirma mentira, traição, doença ou caráter. Priorizar atitudes observáveis, reciprocidade, limites e comunicação. O banco de temas é curadoria inicial baseada na pesquisa acima; ele **não faz pesquisa automática na Internet a cada dia**. Atualizar os temas periodicamente ao observar resultados do canal e novas pesquisas.

## Como validar

```bash
python -m unittest discover -s tests -p test_listas_virais.py -v
python motor/listas_virais.py --dias 10
python tools/preparar_banco_prompts.py
python -m src.fila --resumo
```

Publicação condicionada a `PUBLICAR_ATIVO=true`, aos segredos válidos, ao MP4, capa, hash e manifesto SiliconFlow. Esta implementação não cria publicações por si só: o workflow padrão é quem executa a programação.
