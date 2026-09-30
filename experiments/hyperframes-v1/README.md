# Nina + HyperFrames — teste isolado

Vídeo fictício de exatamente 60 segundos, 1080×1920, 30 fps. Preserva o rig original `motor/nina_lib.py`, a varanda e a voz `pf_dora`. Não altera a produção, os agendamentos nem a fila de publicação.

Recursos demonstrados: composição HTML/CSS/SVG, animação GSAP, mensagens e waveform, relógio, carro, portão que sobe, luz, recortes com sombra e fita, textura de papel, câmera, transições, legendas com destaque, trilha/efeitos originais e confetes discretos.

Etapas: instalar `requirements-estudio.txt` e `npm ci` nesta pasta; executar `prepare.py` para extrair o áudio original de `ep005-p1` (O Portão da Garagem); renderizar `base_scene.py NinaBase` com Manim; transcodificar a camada base para `assets/base.mp4` com keyframes a cada segundo; executar `sound_design.py` e `build.py`; conferir com `hyperframes lint` e `hyperframes snapshot`; exportar com `hyperframes render`.

As legendas usam tempos proporcionais dentro das falas, enquanto o lip-sync é calculado pela amplitude real da voz. Os limites das falas foram conferidos nos silêncios da narração original. A trilha é sintetizada localmente. O roteiro está em `roteiro.txt`. O teste tem exatamente 60 segundos; preserva o áudio original sem acelerar a voz e completa apenas o silêncio final.
