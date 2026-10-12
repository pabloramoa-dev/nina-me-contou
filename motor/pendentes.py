"""Seleciona apenas o estoque de vídeos que precisa estar renderizado.

A reserva anual vive em episodios/ como JSON. O Git não precisa carregar um ano
inteiro de MP4. Mantemos poucos dias prontos e produzimos os próximos à medida
que a fila é consumida.

Prioridades:
1. parte 2 de uma história cuja parte 1 já foi publicada;
2. completar o menor episódio ainda não publicado;
3. parar quando houver ALVO histórias completas prontas.

Uso:
    python motor/pendentes.py --rel --alvo-prontos 8 --limite 8
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src import fila  # noqa: E402


def _path(ep_id: str) -> Path:
    return RAIZ / "episodios" / f"{ep_id}.json"


def selecionar(alvo_prontos: int = 8, limite: int = 8) -> list[Path]:
    feitos = fila.ids_publicados()
    escolhidos: list[Path] = []

    def adicionar(ep_id: str) -> bool:
        """Adiciona se precisa render e ainda cabe no limite."""
        if ep_id in feitos or not fila.desatualizado(ep_id):
            return True
        p = _path(ep_id)
        if not p.exists():
            return True
        if len(escolhidos) >= limite:
            return False
        escolhidos.append(p)
        return True

    # Continuação é prioridade absoluta. Se p1 já saiu, p2 não pode ficar
    # esperando um episódio novo.
    for n in fila.episodios():
        p1, p2 = f"ep{n:03d}-p1", f"ep{n:03d}-p2"
        if p1 in feitos and p2 not in feitos and fila.desatualizado(p2):
            if not adicionar(p2):
                return escolhidos

    # Quantas histórias completas já estão prontas para começar.
    prontos = [
        n for n in fila.completos_prontos()
        if f"ep{n:03d}-p1" not in feitos
    ]
    faltam = max(0, alvo_prontos - len(prontos))
    if faltam == 0:
        return escolhidos

    # Materializa somente o necessário para repor o buffer. Um episódio entra
    # por inteiro: nunca gastamos o último slot deixando só a parte 1 pronta.
    for n in fila.episodios():
        if faltam <= 0:
            break
        p1, p2 = f"ep{n:03d}-p1", f"ep{n:03d}-p2"
        if p1 in feitos or p2 in feitos:
            continue
        if n in prontos:
            continue

        faltantes = [
            ep_id for ep_id in (p1, p2)
            if fila.desatualizado(ep_id) and _path(ep_id).exists()
        ]
        if not faltantes:
            continue
        if len(escolhidos) + len(faltantes) > limite:
            break
        for ep_id in faltantes:
            adicionar(ep_id)
        faltam -= 1

    return escolhidos


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rel", action="store_true")
    ap.add_argument("--alvo-prontos", type=int, default=8)
    ap.add_argument("--limite", type=int, default=8)
    a = ap.parse_args()

    for p in selecionar(max(1, a.alvo_prontos), max(1, a.limite)):
        print(p.relative_to(RAIZ) if a.rel else p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
