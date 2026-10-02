"""Fotos de banco de imagens: plano determinístico e fallback sem rede."""
import json, os, sys
from pathlib import Path
RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "motor"))
import banco_imagens as B


def _ep():
    return {"id": "t", "batidas": [
        {"fala": "a", "arte": ["titulo"]},
        {"fala": "b", "arte": ["alianca", "DATA"]},
        {"fala": "c", "arte": ["alianca"]},
        {"fala": "d", "arte": None, "foto": ["glove compartment car", "PORTA-LUVAS"]},
        {"fala": "e", "arte": ["carro"], "foto": False},
        {"fala": "f", "arte": ["conversa", "oi"]},
    ]}


def test_plano():
    p = B.plano(_ep())
    assert set(p) == {1, 2, 3}
    assert p[1] == ("wedding rings", "DATA", 0)
    assert p[2] == ("wedding rings", None, 1)          # repetido -> outra foto
    assert p[3] == ("glove compartment car", "PORTA-LUVAS", 0)


def test_desligado(monkeypatch):
    monkeypatch.setenv("NINA_FOTOS", "0")
    assert B.plano(_ep()) == {}


def test_falha_mantem_ilustracao(tmp_path, monkeypatch):
    monkeypatch.setattr(B, "CACHE", tmp_path / "cache")
    def sem_rede(*a, **k):
        raise OSError("sem rede")
    monkeypatch.setattr(B, "_get", sem_rede)
    assert B.preparar_episodio(_ep(), tmp_path, tmp_path) == {}


def test_polaroid_legenda_longa(tmp_path):
    from PIL import Image
    f = tmp_path / "x.jpg"
    Image.new("RGB", (800, 500), "#336").save(f)
    im = B.polaroid(f, "UMA LEGENDA MUITO MUITO MUITO MUITO MUITO LONGA MESMO")
    assert im.mode == "RGBA" and im.width > 600
