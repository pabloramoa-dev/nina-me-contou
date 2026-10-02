"""Vídeo avulso: CTA próprio no final e sem 'PARTE' na composição."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "motor"))
from cta import garantir_cta, CTA_AVULSO


def test_cta_avulso_no_final():
    ep = {"id": "x", "avulso": True, "batidas": [
        {"fala": "Me segue que essa é boa."}, {"fala": "Era um recibo."}]}
    e = garantir_cta(ep)
    assert [b["fala"] for b in e["batidas"]] == ["Era um recibo.", CTA_AVULSO]


def test_serie_continua_igual():
    ep = {"id": "x", "parte": 1, "batidas": [{"fala": "Era um recibo."}]}
    assert "parte dois" in garantir_cta(ep)["batidas"][-1]["fala"]
