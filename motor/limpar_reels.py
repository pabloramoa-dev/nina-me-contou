#!/usr/bin/env python3
"""Remove mídia já consumida e impede o estoque de MP4 de crescer sem limite.

Os roteiros em episodios/ e o ledger conteudo/publicados.json nunca são apagados.
Mantemos até N episódios únicos completos e inéditos.
Os pares antigos são apenas histórico; a limpeza respeita a confirmação
de entrega do Telegram e nunca remove arquivos sem recibo válido.

Uso:
    python motor/limpar_reels.py --alvo 8
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
REELS = RAIZ / "reels"
PUBLICADOS = RAIZ / "conteudo" / "publicados.json"
RX = re.compile(r"^(ep\d{3,}(?:-p[12])?)(?=\.|-)")


def publicados() -> set[str]:
    if not PUBLICADOS.exists():
        return set()
    dados = json.loads(PUBLICADOS.read_text(encoding="utf-8"))
    return {
        str(x.get("id"))
        for x in dados
        if x.get("id") and not x.get("ensaio")
    }


def arquivos_por_id() -> dict[str, list[Path]]:
    grupos: dict[str, list[Path]] = {}
    if not REELS.exists():
        return grupos
    for p in REELS.iterdir():
        if not p.is_file():
            continue
        m = RX.match(p.name)
        if m:
            grupos.setdefault(m.group(1), []).append(p)
    return grupos


def _tem(grupos: dict[str, list[Path]], ep_id: str, sufixo: str) -> bool:
    return any(p.name == ep_id + sufixo for p in grupos.get(ep_id, []))


def selecionar_mantidos(alvo: int, feitos: set[str], grupos: dict[str, list[Path]]) -> set[str]:
    """Só os futuros epNNN entram no estoque. Preserva o registro histórico."""
    disponiveis = sorted(ep_id for ep_id in grupos
                         if re.fullmatch(r"ep\d{3,}", ep_id)
                         and all(x not in feitos for x in
                                 (ep_id, ep_id + "-p1", ep_id + "-p2"))
                         and _tem(grupos, ep_id, ".mp4")
                         and _tem(grupos, ep_id, "-capa.jpg"))
    return set(disponiveis[:alvo])


def limpar(alvo: int = 8, simular: bool = False) -> dict:
    feitos = publicados()
    grupos = arquivos_por_id()
    manter = selecionar_mantidos(alvo, feitos, grupos)

    recibos_path = RAIZ / "conteudo" / "telegram_entregues.json"
    recibos = json.loads(recibos_path.read_text(encoding="utf-8")) if recibos_path.exists() else {}
    remover: list[Path] = []
    for ep_id, arquivos in grupos.items():
        video = REELS / f"{ep_id}.mp4"
        recibo = recibos.get(ep_id, {})
        completo = recibo.get("status") == "complete" or ("status" not in recibo and recibo.get("telegram_message_id"))
        if not completo or not video.exists():
            manter.add(ep_id)
            continue
        with video.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        if recibo.get("hash") != digest:
            manter.add(ep_id)
            continue
        if ep_id in feitos or ep_id not in manter:
            remover.extend(arquivos)

    bytes_total = sum(p.stat().st_size for p in remover if p.exists())
    if not simular:
        for p in remover:
            p.unlink(missing_ok=True)

    return {
        "removidos": len(remover),
        "bytes": bytes_total,
        "gb": round(bytes_total / 1_000_000_000, 3),
        "mantidos": sorted(manter),
        "simular": simular,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--alvo", type=int, default=8)
    ap.add_argument("--simular", action="store_true")
    a = ap.parse_args()
    print(json.dumps(limpar(max(1, a.alvo), a.simular), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

