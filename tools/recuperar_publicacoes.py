#!/usr/bin/env python3
"""Recupera horarios perdidos: meta de quatro Reels por dia em Brasilia.

O agendamento chama este script varias vezes. Antes das 21h publica no maximo
um Reel por tentativa, para espacamento natural. A partir das 21h tenta todos
os que faltarem, assim um render atrasado nao perde os horarios do dia.
Stories acompanham a 1a e a 4a publicacoes, sem duplicar episodios.
"""
from __future__ import annotations

import json
import re
import sys
import time
from datetime import date, datetime
from pathlib import Path

# Permite executar como "python tools/recuperar_publicacoes.py" no Actions.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import config, fila
from src.publicar import main as publicar_reel

META_DIARIA = 4
HORARIOS = tuple(config.HORARIOS)
PADRAO_REEL = re.compile(r"^ep\d{3}-p[12]$")


def publicados_no_dia(dia: date) -> set[str]:
    """Conta apenas Reels de verdade, nao Stories nem ensaios; usa BRT."""
    ids: set[str] = set()
    for registro in fila.ler_publicados():
        ep_id = str(registro.get("id", ""))
        if registro.get("ensaio") or not PADRAO_REEL.fullmatch(ep_id):
            continue
        quando = registro.get("quando")
        if not quando:
            continue
        try:
            instante = datetime.fromisoformat(quando)
        except (TypeError, ValueError):
            continue
        if instante.tzinfo is None:
            instante = instante.replace(tzinfo=fila.BRT)
        if instante.astimezone(fila.BRT).date() == dia:
            ids.add(ep_id)
    return ids


def executar() -> int:
    agora = datetime.now(fila.BRT)
    dia = agora.date()
    feitos = publicados_no_dia(dia)
    if len(feitos) >= META_DIARIA:
        print(json.dumps({"ok": True, "dia": str(dia), "reels": len(feitos),
                          "motivo": "Meta diaria ja cumprida"}, ensure_ascii=False))
        return 0

    if not config._flag("PUBLICAR_ATIVO") or config._flag("DRY_RUN"):
        print(json.dumps({"ok": True, "dia": str(dia), "reels": len(feitos),
                          "motivo": "Publicacao desativada ou ensaio"}, ensure_ascii=False))
        return 0

    # Prioriza a distribuicao ao longo do dia, mas recupera atrasos a noite.
    limite = 1 if agora.hour < 21 else META_DIARIA - len(feitos)
    for tentativa in range(limite):
        if datetime.now(fila.BRT).date() != dia:
            print("Virada do dia: a proxima execucao recontara a meta.")
            break
        antes = publicados_no_dia(dia)
        if len(antes) >= META_DIARIA:
            break
        horario = HORARIOS[len(antes)]
        argumentos = sys.argv
        try:
            sys.argv = ["src.publicar", "--horario", horario]
            status = publicar_reel()
        finally:
            sys.argv = argumentos
        if status:
            return status
        depois = publicados_no_dia(dia)
        if len(depois) <= len(antes):
            print(json.dumps({"ok": True, "dia": str(dia),
                              "reels": len(depois), "faltam": META_DIARIA - len(depois),
                              "motivo": "Nenhum episodio completo pronto; tentaremos novamente"},
                             ensure_ascii=False))
            break
        if tentativa + 1 < limite and len(depois) < META_DIARIA:
            time.sleep(60)

    feitos = publicados_no_dia(dia)
    print(json.dumps({"ok": True, "dia": str(dia), "reels": len(feitos),
                      "faltam": max(0, META_DIARIA - len(feitos))}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(executar())
