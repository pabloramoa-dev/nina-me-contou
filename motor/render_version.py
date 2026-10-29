"""Versão visual/voz usada pelo estúdio e pela fila; não carrega o renderizador."""
import os,json,hashlib
from pathlib import Path
HYPERFRAMES_VERSION = 'nina-hyperframes-9-cinema2d-remotion'
def versao():
    motor = os.environ.get('NINA_MOTOR', 'hyperframes')
    if motor not in ('hyperframes', 'manim'):
        raise ValueError('NINA_MOTOR deve ser hyperframes ou manim')
    if motor != 'hyperframes':
        return 'nina-manim-legacy'
    estilo = os.environ.get("NINA_STORY_STYLE", "cinematic_2d").strip().lower()
    if estilo not in ("classic", "cinematic_2d"):
        raise ValueError("NINA_STORY_STYLE deve ser cinematic_2d ou classic")
    extra = "-story-" + estilo
    extra += '-sem-direcao' if os.environ.get('NINA_DIRECAO','1') in ('0','false','False') else ''
    if os.environ.get('NINA_VISUAL', 'v4') != 'v4':
        extra += '-visual-v3'
    if os.environ.get('NINA_LIP', 'rhubarb') != 'rhubarb':
        extra += '-amplitude'
    cfg=json.loads(Path(__file__).with_name("visual_images.json").read_text())
    for key in tuple(cfg):
        if "NINA_"+key.upper() in os.environ:
            cfg[key]=os.environ["NINA_"+key.upper()]
    fingerprint=hashlib.sha256(json.dumps(cfg,sort_keys=True).encode()).hexdigest()[:10]
    import sys
    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from tools.channel_ops import engine_signature
    engine = engine_signature(Path(__file__).resolve().parents[1])[:12]
    # Inclui TS/TSX do Remotion e a escolha de voz; mudança visual renova apenas
    # vídeos ainda não publicados (src/fila.py mantém o histórico intacto).
    compositor = os.environ.get("NINA_FINAL_COMPOSITOR", "remotion")
    voz = os.environ.get("NINA_VOICE_ENGINE", "kokoro")
    speed = os.environ.get("NINA_KOKORO_SPEED", "1.02")
    voice_name = os.environ.get("NINA_KOKORO_VOICE", "pf_dora")
    visual = hashlib.sha256()
    prod = root / "video" / "remotion"
    for suffix in ("*.ts", "*.tsx", "package.json"):
        for path in sorted(prod.rglob(suffix)) if prod.exists() else []:
            if "node_modules" in path.parts:
                continue
            visual.update(str(path.relative_to(root)).encode())
            visual.update(path.read_bytes())
    identidade = f"-final-{compositor}-{visual.hexdigest()[:10]}-voz-{voz}-{voice_name}-{speed}"
    return HYPERFRAMES_VERSION + extra + "-images-" + fingerprint + '-engine-' + engine + identidade
