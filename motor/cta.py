"""Regra fixa do canal: o CTA de seguir vai SÓ no final do vídeo.

garantir_cta(ep) devolve uma cópia do episódio em que:
  - qualquer batida "me segue" fora do final é retirada;
  - a última batida é sempre o convite pra seguir e não perder a continuação.

O produzir.py aplica isso antes de gerar voz e vídeo, então vale para todo
roteiro, mesmo que o JSON venha com o CTA no começo ou sem CTA nenhum.
"""
from __future__ import annotations

import copy
import re

RX_SEGUE = re.compile(r"\bme\s+segue\b|\bsegue\s+a\s+nina\b|\bsiga\s+a\s+nina\b", re.I)

CTA = {
    1: "Me segue pra não perder a continuação. A parte dois sai daqui a pouco.",
    2: "Me segue pra não perder a continuação. Daqui a pouco tem história nova.",
}
PLACA = {1: "SEGUE PRA VER A PARTE 2", 2: "SEGUE PRA NÃO PERDER A PRÓXIMA"}


def eh_cta(b: dict) -> bool:
    return bool(RX_SEGUE.search(b.get("fala", ""))) or (b.get("arte") or [None])[0] == "seguir"


def garantir_cta(ep: dict) -> dict:
    ep = copy.deepcopy(ep)
    bats = [b for b in ep["batidas"] if not eh_cta(b)]
    parte = 2 if ep.get("parte") == 2 else 1
    bats.append({"fala": CTA[parte], "expr": "ironica", "arte": ["seguir", PLACA[parte]],
                 "destaque": ["segue", "continuação."]})
    ep["batidas"] = bats
    return ep
