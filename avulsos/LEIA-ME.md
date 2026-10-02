# Vídeos avulsos da Nina

Roteiros de vídeos feitos **sob demanda**, fora da fila automática do Instagram.

- Um arquivo por vídeo: `avulsos/<id>.json` (o `"id"` dentro do JSON é igual ao nome do arquivo).
- Mesmo formato dos episódios, com `"avulso": true` (história completa, sem parte 1/parte 2).
- Ao salvar aqui, o workflow **Produzir vídeo avulso** gera em `avulsos_prontos/`:
  `<id>.mp4` (1080x1920), `<id>-720p.mp4` (prévia leve), `<id>-capa.jpg`, `<id>-story.mp4` e `<id>-legenda.txt`.
- Nada daqui é publicado sozinho. Para entrar na fila automática, use `episodios/` (par p1/p2).
- Duração: até 3 minutos (`NINA_MAX_DUR=180`). CTA de seguir só no final, automático.
