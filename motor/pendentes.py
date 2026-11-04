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


def produzivel(arq: Path) -> bool:
    """Mesma checagem que o produzir.py faz antes da voz: gancho + banco de prompts.

    Um roteiro sem os 10 prompts cadastrados falharia no render e ocuparia uma
    vaga da matriz a cada rodada; aqui ele é pulado e avisado no log.
    """
    import json, os
    motor = str(RAIZ / "motor")
    if motor not in sys.path:
        sys.path.insert(0, motor)
    try:
        from antecipacao import antecipar
        from cta import garantir_cta
        from visual_images import preparar_roteiro
        ep = preparar_roteiro(garantir_cta(antecipar(json.loads(arq.read_text(encoding="utf-8")))))
        if os.getenv("NINA_REQUIRE_STORED_PROMPTS", "1") == "1":
            from prompts_banco import carregar
            carregar(ep)
        return True
    except Exception as exc:  # noqa: BLE001 - só registra e pula
        print(f"::warning::{arq.name} pulado: {exc}", file=sys.stderr)
        return False


def selecionar(alvo_prontos: int = 8, limite: int = 8) -> list[Path]:
    feitos = fila.ids_publicados()
    prontos = fila.completos_prontos()
    faltam = max(0, alvo_prontos - len(prontos))
    escolhidos: list[Path] = []
    # Pedidos manuais inéditos entram primeiro; preserva a ordem normal dos demais.
    ordem = sorted(fila.episodios(), key=lambda n: (
        not fila.carregar_ep(f"ep{n:03d}").get("producao_prioritaria", False), n
    ))
    for n in ordem:
        if not faltam or len(escolhidos) >= limite:
            break
        ep_id = f"ep{n:03d}"
        if fila.ja_publicado(ep_id, feitos) or n in prontos:
            continue
        arq = RAIZ / "episodios" / f"{ep_id}.json"
        if arq.exists() and fila.desatualizado(ep_id) and produzivel(arq):
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
