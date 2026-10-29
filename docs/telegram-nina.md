# Entrega automática dos MP4s da Nina

O Instagram mantém seu fluxo existente. Nenhum vídeo é publicado automaticamente no TikTok.

## Configuração

Crie o bot no @BotFather oficial, envie /start para o bot e cadastre os secrets
TELEGRAM_BOT_TOKEN_NINA e TELEGRAM_CHAT_ID_NINA nas configurações de Actions.
Nunca coloque o token em conversa, código, URL compartilhada ou logs.
O chat deve ser a conversa privada do próprio usuário, verificada pelo /start.

## Entrega e recuperação

O workflow `Entregar MP4 Nina no Telegram` roda após `Produzir episódios` terminar
(inclusive quando algumas partes falharem) e a cada hora para recuperar pendentes.
Lê a main atual, valida áudio/vídeo/duração com FFprobe e envia o arquivo por
sendDocument. Envia depois a descrição TikTok com hashtags e identificação.
Arquivos acima de 49 MB recebem uma cópia comprimida; o original é preservado.
Todas as execuções de entrega usam a mesma trava de concorrência.

Cada etapa grava e envia um checkpoint ao Git antes de avançar. O recibo distingue
vídeo e descrição. Rejeições explícitas do Telegram podem ser repetidas na próxima
execução. Quando ocorre timeout ou interrupção sem resposta, o estado permanece
`sending_video` ou `sending_description`: exige conferência manual antes de repetir,
pois a API não oferece uma chave de idempotência para garantir envio exatamente uma vez.
Nunca redefina esses estados sem conferir a conversa do destinatário.

A limpeza só remove o conjunto de mídia quando existe um recibo completo cujo
SHA-256 corresponde ao MP4 atual. Renders novos ou entregas pendentes ficam protegidos.
O estúdio tenta repor o estoque quatro vezes por dia e não cancela um render em curso.
A publicação mantém a meta existente de quatro Reels por dia em Brasília e suas
retentativas; quantidade efetiva depende de renders e API do Instagram disponíveis.

## Testes

`Validar entrega Telegram Nina (sem envio)` usa MP4 sintético e API simulada.
Testa sucesso, repetição, vídeo inválido, secrets ausentes, falha na descrição e limpeza.
Não constitui prova de entrega real.

Para teste real, execute `Entregar MP4 Nina no Telegram` com limite 1. Confira o
recibo completo, abra o MP4 recebido e verifique reprodução e download no Telegram.
Sem os dois secrets o envio falha explicitamente; nenhum sucesso fictício é registrado.
