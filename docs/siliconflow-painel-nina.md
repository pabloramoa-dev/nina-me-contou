# Nina: ilustrações SiliconFlow no quadro de apoio superior

O rosto, a voz e o lip-sync da apresentadora permanecem no vídeo Manim.
O quadro superior do Remotion foi ampliado de 930×548 para 980×660;
a apresentadora ficou um pouco menor para dar espaço ao novo painel.
As legendas continuam soltas na parte inferior, sem painel escuro.

## API e limite de gastos

- Provedor: SiliconFlow (endpoint internacional).
- Modelo: `black-forest-labs/FLUX.1-schnell` (licença Apache 2.0).
- Geração configurada: **até 10 imagens** por episódio, **768×512**.
- Referência de preço: US$ 0,0014 por imagem, cerca de **US$ 0,014**
  por episódio completo de dez imagens, antes de tentativas adicionais,
  taxas ou impostos.
- Criar secret no GitHub: `SILICONFLOW_API_KEY`.
- Para permitir chamadas pagas, criar Repository Variable
  `NINA_ALLOW_PAID_IMAGE_API` com valor `1`.
- **Padrão seguro: 0**. Sem secret/variável o processo usa o
  desenho local gratuito. Nenhuma postagem foi modificada.

## Fluxo

1. O roteiro da Nina é organizado em até 10 cenas, cada uma com
   um prompt de revistinha digital e continuidade visual.
2. HyperFrames gera a imagem pela API e baixa imediatamente
   a URL temporária (validade anunciada de uma hora).
3. O cache salva a arte dentro de `saida/<episodio>/visual_cache`;
   a composição final Remotion copia as imagens para o quadro superior.
4. O Remotion troca a cena do painel a cada ~7 segundos, sem cobrir a Nina
   nem as legendas. Cenas mais longas podem reutilizar uma das dez imagens,
   com movimento suave de enquadramento.
5. Caso falte uma imagem, usa o quadro local sem bloquear o vídeo.

## Checklist para liberar o piloto

- Conferir o Secret e o limite mensal configurado no painel SiliconFlow.
- Executar testes sem rede:
  `python -m unittest discover -s tests -p 'test_siliconflow_nina.py' -v`
  e `python -m unittest discover -s tests -p 'test_nina_cinema2d.py' -v`.
- Validar um MP4 do piloto antes de ativar a variável de cobrança na
  produção. Não há limite rígido de custo no Python além de até dez cenas
  por episódio e zero tentativas repetidas por padrão.
