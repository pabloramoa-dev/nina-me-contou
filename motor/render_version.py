"""Versão visual/voz usada pelo estúdio e pela fila; não carrega o renderizador."""
import os,json,hashlib
from pathlib import Path
HYPERFRAMES_VERSION = 'nina-hyperframes-8-direcao-gratuita-qa'
def versao():
    motor = os.environ.get('NINA_MOTOR', 'hyperframes')
    if motor not in ('hyperframes', 'manim'):
        raise ValueError('NINA_MOTOR deve ser hyperframes ou manim')
    if motor != 'hyperframes':
        return 'nina-manim-legacy'
    extra = '-sem-direcao' if os.environ.get('NINA_DIRECAO','1') in ('0','false','False') else ''
    if os.environ.get('NINA_VISUAL', 'v4') != 'v4':
        extra += '-visual-v3'
    if os.environ.get('NINA_LIP', 'rhubarb') != 'rhubarb':
        extra += '-amplitude'
    cfg=json.loads(Path(__file__).with_name("visual_images.json").read_text())
    for key in tuple(cfg):
        if "NINA_"+key.upper() in os.environ:
            cfg[key]=os.environ["NINA_"+key.upper()]
    fingerprint=hashlib.sha256(json.dumps(cfg,sort_keys=True).encode()).hexdigest()[:10]
    from tools.channel_ops import engine_signature
    engine = engine_signature(Path(__file__).resolve().parents[1])[:12]
    return HYPERFRAMES_VERSION + extra + "-images-" + fingerprint + '-engine-' + engine
