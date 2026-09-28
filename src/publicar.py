"""Publica o Reel do horário (e o Story, às 8h e às 20h).

    python -m src.publicar --horario manha      # 08h: Reel + Story
    python -m src.publicar --horario almoco     # 12h: Reel
    python -m src.publicar --horario tarde      # 16h: Reel
    python -m src.publicar --horario noite      # 20h: Reel + Story

A ordem é sempre a da fila (parte 1 → parte 2 → próximo episódio).
Com DRY_RUN=true ou PUBLICAR_ATIVO=false, faz tudo menos publicar.
"""
from __future__ import annotations

import argparse
import json
import sys

from src import config, fila
from src.instagram import Publicador


def publicar_story(pub: Publicador, cfg, ep_id: str) -> str:
    arq = f"{ep_id}-story.mp4" if (config.REELS / f"{ep_id}-story.mp4").exists() else f"{ep_id}.mp4"
    container = pub.criar_container_story(f"{cfg.raw_base_url}/reels/{arq}")
    pub.aguardar_pronto(container)
    return pub.publicar(container)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--horario", choices=list(config.HORARIOS), required=True)
    a = ap.parse_args()
    com_story = a.horario in config.COM_STORY

    cfg = config.carregar(exigir_credenciais=not config._flag("DRY_RUN", "true"))
    ep_id = fila.proximo(a.horario)
    if ep_id is None:
        print(json.dumps({"ok": True, "publicado": None,
                          "motivo": f"nada pronto para o horário {config.HORARIOS[a.horario]}"},
                         ensure_ascii=False))
        return 0

    ep = fila.carregar_ep(ep_id)
    video = f"{cfg.raw_base_url}/reels/{ep_id}.mp4"
    capa = f"{cfg.raw_base_url}/reels/{ep_id}-capa.jpg"
    legenda = ep["legenda_post"]
    rel = {"horario": config.HORARIOS[a.horario], "id": ep_id, "titulo": ep["titulo"],
           "parte": ep["parte"], "video": video, "capa": capa, "story": com_story,
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

    if com_story:
        # falha no Story não derruba o Reel, que já saiu e já está no histórico
        try:
            sid = publicar_story(pub, cfg, ep_id)
            fila.gravar_publicado(f"{ep_id}-story", sid, dry=False)
            rel["story_id"] = sid
        except Exception as e:  # noqa: BLE001
            rel["story_erro"] = str(e)[:300]
            print(f"::warning::Story de {ep_id} não saiu: {str(e)[:200]}")

    print(json.dumps(rel, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
