#!/usr/bin/env python3
"""Recupera publicações de três horários da Nina em Brasília: 9h, 12h e 15h.

Antes das 21h só publica o formato devido no seu próprio horário. Após 21h,
recupera slots perdidos sem duplicá-los, respeitando o tipo de episódio.
"""
from __future__ import annotations

import json
import re
import sys
import time
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import config, fila
from src.publicar import main as publicar_reel

META_DIARIA = 3
HORARIOS = tuple(config.HORARIOS)
PADRAO_REEL = re.compile(r"^ep\d{3,}(?:-p[12])?$")


def horarios_no_dia(dia: date) -> dict[str, str]:
    """Lê o ledger e tolera publicações anteriores sem campo horario."""
    saida: dict[str, str] = {}
    for registro in fila.ler_publicados():
        ep_id = str(registro.get("id", ""))
        if registro.get("ensaio") or not PADRAO_REEL.fullmatch(ep_id):
            continue
        try:
            instante = datetime.fromisoformat(str(registro["quando"]))
        except (KeyError, ValueError, TypeError):
            continue
        if instante.tzinfo is None:
            instante = instante.replace(tzinfo=fila.BRT)
        instante = instante.astimezone(fila.BRT)
        if instante.date() != dia:
            continue
        slot = registro.get("horario")
        if slot not in HORARIOS:
            # Compatibilidade: registros antigos de 8h/12h/16h/20h.
            slot = ("manha" if instante.hour < 12 else
                    "almoco" if instante.hour < 15 else "tarde")
        saida.setdefault(slot, ep_id)
    return saida


def publicados_no_dia(dia: date) -> set[str]:
    return set(horarios_no_dia(dia).values())


def executar() -> int:
    agora = datetime.now(fila.BRT)
    dia = agora.date()
    feitos = horarios_no_dia(dia)
    if len(feitos) >= META_DIARIA:
        print(json.dumps({"ok": True, "dia": str(dia), "slots": feitos,
                          "motivo": "Meta diaria cumprida"}, ensure_ascii=False))
        return 0
    if not config._flag("PUBLICAR_ATIVO") or config._flag("DRY_RUN"):
        print(json.dumps({"ok": True, "dia": str(dia), "slots": feitos,
                          "motivo": "Publicacao desativada ou ensaio"}, ensure_ascii=False))
        return 0

    # Não antecipar listas: o roteiro do almoço só entra depois das 12h.
    if agora.hour < 9:
        devidos = ()
    elif agora.hour < 12:
        devidos = ("manha",)
    elif agora.hour < 15:
        devidos = ("almoco",)
    elif agora.hour < 21:
        devidos = ("tarde",)
    else:
        devidos = HORARIOS  # recuperar qualquer slot não entregue

    for i, horario in enumerate(devidos):
        if horario in feitos:
            continue
        if datetime.now(fila.BRT).date() != dia:
            break
        anterior = horarios_no_dia(dia)
        argv = sys.argv
        try:
            sys.argv = ["src.publicar", "--horario", horario]
            status = publicar_reel()
        finally:
            sys.argv = argv
        if status:
            return status
        feitos = horarios_no_dia(dia)
        if horario not in feitos:
            print(f"::warning::Sem reel pronto para {horario}; proxima tentativa programada.")
            break
        if i + 1 < len(devidos):
            time.sleep(15)

    feitos = horarios_no_dia(dia)
    faltam = [h for h in HORARIOS if h not in feitos]
    print(json.dumps({"ok": not faltam, "dia": str(dia),
                      "slots": feitos, "faltam": faltam}, ensure_ascii=False))
    if faltam and datetime.now(fila.BRT).hour >= 23:
        print(f"::error::Nina: faltam horarios do dia: {faltam}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(executar())
