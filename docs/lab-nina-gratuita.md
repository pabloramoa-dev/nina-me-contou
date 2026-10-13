# Laboratório: Nina com direção e gestos gratuitos

Branch experimental: lab/nina-direcao-gratuita-v1. **Nada publica no Instagram**.
A branch main continua como estava; o vídeo de teste é gerado por GitHub Actions.

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

Durante esse teste a geração paga de imagens fica desligada:
NINA_AUTO_VISUAL_IMAGES=0 e NINA_FOTOS=0; continuam os elementos locais de
arte. A voz principal permanece Thalita, com fallback Kokoro se indisponível.

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
