"""Versão visual/voz usada pelo estúdio e pela fila; não carrega o renderizador."""
import os
HYPERFRAMES_VERSION = 'nina-hyperframes-7-auto-visual-story-frames'
def versao():
    motor = os.environ.get('NINA_MOTOR', 'hyperframes')
    if motor not in ('hyperframes', 'manim'):
        raise ValueError('NINA_MOTOR deve ser hyperframes ou manim')
    if motor != 'hyperframes':
        return 'nina-manim-legacy'
    extra = ''
    if os.environ.get('NINA_VISUAL', 'v4') != 'v4':
        extra += '-visual-v3'
    if os.environ.get('NINA_LIP', 'rhubarb') != 'rhubarb':
        extra += '-amplitude'
    return HYPERFRAMES_VERSION + extra
