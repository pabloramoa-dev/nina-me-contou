"""Testes da direção gratuita: sem Manim, rede ou geração de imagens."""
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "motor"))

import direcao_nina as D
import qualidade_nina as Q
from gerar_roteiros import gancho_situacional


def exemplo():
    ep = {"id": "lab", "titulo": "UMA CHAVE", "batidas": [
        {"fala": "Eu encontrei a chave.", "expr": "neutra"},
        {"fala": "Mas quem deixou esse bilhete?", "expr": "desconfiada"},
        {"fala": "A verdade apareceu!", "expr": "chocada"},
        {"fala": "Você faria o mesmo?", "expr": "ironica"},
    ]}
    segs = [{"i": i, "ini": i * 3., "fim": (i+1)*3., "fim_fala": (i+1)*3.-.2} for i in range(4)]
    return ep, segs


def test_plano_determinista_e_emocoes():
    ep, segs = exemplo()
    plano = D.planejar(ep, segs)
    assert plano == D.planejar(ep, segs)
    assert [p["gesto"] for p in plano] == ["contar", "perguntar", "surpresa", "perguntar"]
    assert plano[2]["camera"] == "aproximar"
    assert all(p["inicio"] < p["fim"] for p in plano)
    assert len({p["gesto"] for p in plano}) >= 3


def test_gesto_expresso_e_timeline_invalidos():
    ep, segs = exemplo()
    ep["batidas"][0]["gesto"] = "acolher"
    assert D.planejar(ep, segs)[0]["gesto"] == "acolher"
    ep["batidas"][0]["gesto"] = "<script>"
    assert D.planejar(ep, segs)[0]["gesto"] in D.GESTOS
    try:
        D.planejar(ep, segs[:-1])
        assert False, "deveria rejeitar plano incompleto"
    except ValueError:
        pass


def test_gesticulacao_suave_e_sem_salto():
    a = D.deslocamento("surpresa", 1.5, 0, 3)
    assert a[0] < 0 and a[1] > 0
    assert D.deslocamento("surpresa", 0, 0, 3) == (0, 0)
    assert D.deslocamento("surpresa", 3, 0, 3) == (0, 0)
    for t in [0.1, .9, 1.5, 2.8]:
        xy = D.deslocamento("alertar", t, 0, 3)
        assert all(math.isfinite(v) for v in xy)


def test_camera_suave_e_limites():
    ep, segs = exemplo()
    for x in D.planejar(ep, segs):
        z, offset = D.camera_destino(x)
        assert 1 <= z <= 1.1 and abs(offset) <= 12


def test_gancho_relacionado_ao_objeto():
    chave = "uma chave que não abria a porta"
    for i in range(24):
        g = gancho_situacional(i, chave)
        assert chave in g and len(g.split()) <= 24
    assert len({gancho_situacional(i, chave) for i in range(24)}) >= 6


def test_quality_checks_caption_and_inner_text(tmp_path):
    ep, segs = exemplo()
    plano = D.planejar(ep, segs)
    html = '<div id="base"></div><div id="voice"></div><div class="pill"></div>'
    html += '<section id="p0" class="story_frame_image"><h1>CASO</h1><img src="x.png"></section>'
    html += ''.join(f'<section id="p{i}"><h1>CASO</h1></section>' for i in range(1, 4))
    p = tmp_path / "index.html"
    p.write_text(html)
    report = Q.analisar(ep, segs, plano, p, {"ready": 1}, {"streams": [{"codec_type": "video"}]})
    assert report["aprovado_tecnicamente"]
    p.write_text(html.replace('<img src="x.png">', '<div class="note">ERRADO</div><img src="x.png">'))
    report = Q.analisar(ep, segs, plano, p, {"ready": 1}, {"streams": [{"codec_type": "video"}]})
    assert not report["aprovado_tecnicamente"]
    assert any("legenda interna" in e for e in report["erros"])
    Q.gravar(report, tmp_path/"qualidade.json")
    assert json.loads((tmp_path/"qualidade.json").read_text())["erros"]
