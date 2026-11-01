"""Reserva de produção: somente episódios únicos ainda não publicados.

Uso: python motor/pendentes.py --rel --alvo-prontos 8 --limite 8
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from src import fila  # noqa: E402


def selecionar(alvo_prontos: int = 8, limite: int = 8) -> list[Path]:
    feitos = fila.ids_publicados()
    prontos = fila.completos_prontos()
    faltam = max(0, alvo_prontos - len(prontos))
    escolhidos: list[Path] = []
    for n in fila.episodios():
        if not faltam or len(escolhidos) >= limite:
            break
        ep_id = f"ep{n:03d}"
        if fila.ja_publicado(ep_id, feitos) or n in prontos:
            continue
        arq = RAIZ / "episodios" / f"{ep_id}.json"
        if arq.exists() and fila.desatualizado(ep_id):
            escolhidos.append(arq)
            faltam -= 1
    return escolhidos


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rel", action="store_true")
    ap.add_argument("--alvo-prontos", type=int, default=8)
    ap.add_argument("--limite", type=int, default=8)
    args = ap.parse_args()
    for p in selecionar(max(1, args.alvo_prontos), max(1, args.limite)):
        print(p.relative_to(RAIZ) if args.rel else p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
