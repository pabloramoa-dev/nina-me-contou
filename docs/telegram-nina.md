# Nina Me Contou — receber MP4 + descrição para TikTok no Telegram

Este fluxo **não publica no TikTok**: manda o arquivo MP4 para baixar no seu Telegram e, logo depois, uma mensagem com a descrição pronta para copiar.

## Ativar uma única vez

1. No Telegram, procure o bot oficial **@BotFather** (conta verificada) e envie `/newbot`. Escolha um nome e um nome de usuário para o seu bot. O BotFather fornece um token secreto. **Não mande esse token no ChatGPT, em mensagens públicas, em commits nem nos logs do GitHub.**
2. Abra a conversa privada com o bot recém-criado e toque em **Iniciar** ou envie `/start`. Bots não podem iniciar conversas privadas antes de você fazer isso.
3. Obtenha o seu `chat_id` privado usando o método `getUpdates` da API oficial do Telegram, com o token **somente em um ambiente privado** (ex.: uma sessão segura no Work). Na resposta, encontre `message.chat.id` referente à mensagem `/start` que você enviou. Não use IDs de outras conversas.
4. No repositório `pabloramoa-dev/nina-me-contou`, abra **Settings → Secrets and variables → Actions → New repository secret**. Cadastre:
   - `TELEGRAM_BOT_TOKEN_NINA`: token obtido no BotFather;
   - `TELEGRAM_CHAT_ID_NINA`: número do chat privado.
5. Para verificar sem enviar mensagens, execute **Actions → Validar entrega Telegram Nina (sem envio) → Run workflow**. Esse teste cria apenas um MP4 sintético, valida imagem e áudio e monta uma legenda.
6. Depois, a próxima execução que efetivamente renderizar um episódio em **Actions → Produzir episódios** enviará, ao terminar, o MP4 correspondente e a descrição para o TikTok.

## Como funciona

- `motor/produzir.py` renderiza cada parte (vídeo e áudio).
- Só quando o artefato MP4 da parte já foi produzido e salvo no GitHub Actions é que `gravar` o baixa para `entrega_nina/`.
- `tools/telegram_nina.py` verifica o vídeo com FFprobe, incluindo áudio, imagem e duração. Se não estiver pronto, **não envia**.
- Quando o arquivo tem menos de aproximadamente 49 MB, envia o MP4 original como documento baixável no Telegram. Se for maior, cria uma cópia comprimida apenas para envio, mantendo o original no pipeline.
- Em seguida envia uma **mensagem separada** contendo título, indicação da parte 1 ou 2, o texto `legenda_post` do roteiro e hashtags. Você pode copiar e colar diretamente no TikTok.
- Um registro por vídeo e assinatura evita envios repetidos do mesmo arquivo.
- Falhas de conexão, limite do Telegram e erros de renderização ficam nos logs do workflow. Arquivos não são declarados entregues se o Telegram não tiver aceitado ambas as mensagens.

## Importante

Sem os dois GitHub Secrets acima, o workflow registra um aviso e **não envia vídeos**. Configuração salva no repositório **não é prova de entrega**; confirme que recebeu um MP4 e seu texto no Telegram. Mantenha o bot privado e não compartilhe o token.
