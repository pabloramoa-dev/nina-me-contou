"""Publica o Reel do horário.

    python -m src.publicar --horario almoco     # 12h: parte 1
    python -m src.publicar --horario noite      # 20h: parte 2

Com DRY_RUN=true ou PUBLICAR_ATIVO=false, faz tudo menos publicar.
"""
from __future__ import annotations

import argparse
import json
import sys

from src import config, fila
from src.instagram import Publicador


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--horario", choices=["almoco", "noite"], required=True)
    a = ap.parse_args()

    cfg = config.carregar(exigir_credenciais=not config._flag("DRY_RUN", "true"))
    ep_id = fila.proximo(a.horario)
    if ep_id is None:
        print(json.dumps({"ok": True, "publicado": None,
                          "motivo": f"nada pendente para o horário {a.horario}"}, ensure_ascii=False))
        return 0

    ep = fila.carregar_ep(ep_id)
    video = f"{cfg.raw_base_url}/reels/{ep_id}.mp4"
    capa = f"{cfg.raw_base_url}/reels/{ep_id}-capa.jpg"
    legenda = ep["legenda_post"]
    rel = {"id": ep_id, "titulo": ep["titulo"], "parte": ep["parte"], "video": video, "capa": capa,
           "duracao": round(fila.duracao(config.REELS / f"{ep_id}.mp4"), 1)}

    if cfg.dry_run or not cfg.publicar_ativo:
        rel.update(ok=True, ensaio=True,
                   motivo="DRY_RUN ligado" if cfg.dry_run else "PUBLICAR_ATIVO desligado")
        print(json.dumps(rel, ensure_ascii=False, indent=1))
        return 0

    pub = Publicador(cfg)
    container = pub.criar_container(video, legenda, capa)
    pub.aguardar_pronto(container)
    try:
        media_id = pub.publicar(container)
    except Exception:
        media_id = pub.reconciliar(container)
        if not media_id:
            raise
    fila.gravar_publicado(ep_id, media_id, dry=False)
    rel.update(ok=True, media_id=media_id)
    print(json.dumps(rel, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
