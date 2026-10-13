# Direção gratuita da Nina — estilo aprovado

Implementação aprovada em 13/10/2026 e preparada para a branch principal.
O vídeo de teste foi renderizado sem publicação automática. A produção diária volta
a usar os workflows originais; nenhuma postagem é disparada por este documento.

## Modificações implementadas
- motor/direcao_nina.py: gestos por batida (contar, perguntar, alertar, surpresa, ponderar, acolher), plano de câmera e transições suaves, com saída saida/<id>/direcao.json.
- motor/nina_lib.py + motor/cena_hyperframes.py: mão esquerda articulada sem mudar a identidade da Nina, cenário, taça, voz, sincronização da boca nem legendas.
- motor/hyperframes.py: planos de câmera ajustados por emoção e gesto; o compositor original e os templates das imagens permanecem.
- motor/gerar_roteiros.py: novos ganchos mencionam a pista real do episódio. Apenas histórias geradas depois do ajuste recebem esses ganchos; roteiros existentes são preservados.
- motor/qualidade_nina.py: relatório de integridade da timeline, quadros e legendas. O MP4 continua validado com ffprobe e resolução vertical.
- video/validate-layout.mjs: ferramenta de inspeção por navegador já existente; acionada no CI do laboratório.

## Testar
GitHub Actions > Validar Nina HyperFrames > branch lab/nina-direcao-gratuita-v1.
A execução dispara ao enviar alterações desta branch. Veja artifact
nina-hyperframes-integracao-thalita para MP4, Story, capa, direcao.json,
qualidade.json e render.json.

O workflow de validação usa NINA_AUTO_VISUAL_IMAGES=0 e NINA_FOTOS=0
somente para não gastar com geração de imagens durante testes. Isso não
desativa as ilustrações de reforço nem o fallback de fotos nos workflows
normais de publicação. A voz principal permanece Thalita, com fallback Kokoro.

Para desativar os novos gestos/enquadramentos: NINA_DIRECAO=0.
A versão de render inclui essa opção, evitando confusão entre vídeos antigos e novos.

## Limites
A verificação automática estrutural não comprova que todos os quadros são
visualmente perfeitos; a inspeção por navegador detecta sobreposições geométricas
de imagens e legendas. É importante assistir ao vídeo antes de incorporar ao
motor de publicação. Não há geração de imagens inéditas por IA gratuita neste
laboratório: a opção depende da API já prevista no pipeline.

Código inspirado em técnicas de direção de cena e animação 2D dos projetos
Synctoon e Avatar Skills; não foram copiados módulos GPL do Synctoon.

## Produção

A direção de gestos e enquadramentos vem **ativa por padrão** quando
NINA_MOTOR=hyperframes. A publicação normal permanece controlada pelos
workflows existentes. A geração de imagens segue os controles originais
de visual_images.json. Não forçar OPENAI_API_KEY vazio na produção.

A cada render ficam disponíveis direcao.json, qualidade.json e render.json.
O relatório de QA bloqueia saída que falhe em checagens estruturais; não é
uma avaliação artística ou de retenção. É importante observar os primeiros
vídeos para conferir gestos naturais e evitar cenas repetitivas.
