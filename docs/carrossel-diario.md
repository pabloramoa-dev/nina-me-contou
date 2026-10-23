# Carrossel diário — Nina Me Contou

Fluxo independente de `Publicar Reel` e `Produzir episódios`, sem mexer em horários, vídeos, Stories, voz Thalita ou HyperFrames.

- Workflow: `.github/workflows/carrossel-diario.yml`.
- Agendamento: **todos os dias às 10h37 de Brasília** (cron 13h37 UTC; o GitHub pode atrasar a execução).
- Formato: **7 imagens JPEG 1080 × 1350 (4:5)**, mais legenda e aviso de ficção.
- Personagem: retrato da **Nina original**, gerado com `motor/perfil_nina.py` (Manim). As cenas auxiliares são ilustrações locais de `motor/local_story_art.py`.
- Custo de geração: CPU com Manim + Pillow; não requer API de imagens, GPU ou serviços pagos.
- Primeiro carrossel: história da suspeita do marido e sua aula secreta de confeitaria; nos dias seguintes gera histórias inéditas por data a partir do motor anual de roteiros sem consumir a fila de Reels.
- Publicação: reutiliza `src/instagram.py` com 7 containers filhos e um container pai, apenas depois do commit dos JPEGs em `main` (RAW_BASE_URL público).
- Evita repetição por data: `conteudo/carrosseis_publicados.json` e `conteudo/send_receipts.json`. O recibo pendente é persistido **antes** da chamada final de publicação. Um envio de estado incerto é bloqueado para análise/reconciliação e não repetido cegamente.
- Confere `username == ninamecontou` antes de enviar.

## Configuração existente reutilizada

Exige GitHub Secrets `IG_USER_ID_NINA`, `IG_ACCESS_TOKEN_NINA` e variables `RAW_BASE_URL`, `GRAPH_API_VERSION`, `PUBLICAR_ATIVO=true`. Repositório público para a API da Meta buscar cada JPEG.

## Teste sem publicar

Acesse **Actions → Nina - Carrossel diário → Run workflow** e deixe **Publicar** desmarcado. O workflow gera um artefato `nina-carrossel-ensaio` com sete JPEGs e o `conteudo.json`. Para publicação de uma data específica, informe `AAAA-MM-DD` e marque **Publicar**. Não publique os mesmos slides manualmente no Instagram para evitar duplicidade fora do ledger.

## Diagnóstico

A execução automática falha visivelmente se a credencial estiver ausente, `PUBLICAR_ATIVO` estiver desativado, a conta não for @ninamecontou, o retrato original falhar ou alguma imagem pública não estiver acessível.

Obs.: O carrossel tem visual próprio de quadros ilustrados e texto; não usa as sete imagens geradas isoladamente na conversa anterior, que não foram adicionadas como arquivos binários ao GitHub. A Nina retratada é a original do repositório.
