"""Fila de publicação da Nina.

Regras
- Episódio = par epNNN-p1 + epNNN-p2. Só entra na fila quando OS DOIS MP4 e as
  DUAS capas existem em reels/ (nunca publicar parte 1 sem a 2 pronta).
- Horário "almoco" (12h): publica a parte 1 do menor episódio ainda não publicado.
- Horário "noite" (20h): publica a parte 2 do episódio cuja parte 1 já saiu e a 2 não.
  Se não há parte 2 pendente, não publica nada (a noite é sempre a continuação).
- Nunca publica o mesmo id duas vezes (ledger publicados.json).
"""
from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone, timedelta

from src import config

BRT = timezone(timedelta(hours=-3))
RX = re.compile(r"^ep(\d{3})-p([12])$")


def ler_publicados() -> list[dict]:
    if config.PUBLICADOS_JSON.exists():
        return json.loads(config.PUBLICADOS_JSON.read_text(encoding="utf-8"))
    return []


def gravar_publicado(ep_id: str, media_id: str | None, dry: bool) -> None:
    pub = ler_publicados()
    pub.append({"id": ep_id, "media_id": media_id,
                "quando": datetime.now(BRT).isoformat(timespec="minutes"), "ensaio": dry})
    config.PUBLICADOS_JSON.write_text(json.dumps(pub, ensure_ascii=False, indent=1), encoding="utf-8")


def ids_publicados() -> set[str]:
    return {p["id"] for p in ler_publicados() if not p.get("ensaio")}


def carregar_ep(ep_id: str) -> dict:
    return json.loads((config.EPISODIOS / f"{ep_id}.json").read_text(encoding="utf-8"))


def pronto(ep_id: str) -> bool:
    return (config.REELS / f"{ep_id}.mp4").exists() and (config.REELS / f"{ep_id}-capa.jpg").exists()


def episodios() -> list[int]:
    nums = set()
    for f in config.EPISODIOS.glob("ep*-p*.json"):
        m = RX.match(f.stem)
        if m:
            nums.add(int(m.group(1)))
    return sorted(nums)


def completos_prontos() -> list[int]:
    return [n for n in episodios() if pronto(f"ep{n:03d}-p1") and pronto(f"ep{n:03d}-p2")]


def proximo(horario: str) -> str | None:
    feitos = ids_publicados()
    if horario == "noite":
        for n in episodios():
            p1, p2 = f"ep{n:03d}-p1", f"ep{n:03d}-p2"
            if p1 in feitos and p2 not in feitos and pronto(p2):
                return p2
        return None
    for n in completos_prontos():
        p1 = f"ep{n:03d}-p1"
        if p1 not in feitos:
            return p1
    return None


def duracao(caminho) -> float:
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                   "-of", "csv=p=0", str(caminho)])
    return float(out.strip())


def lint() -> dict:
    """Confere cada episódio: JSON válido, par completo, duração e legenda."""
    problemas, feitos = [], ids_publicados()
    for n in episodios():
        for parte in (1, 2):
            ep_id = f"ep{n:03d}-p{parte}"
            f = config.EPISODIOS / f"{ep_id}.json"
            if not f.exists():
                problemas.append(f"{ep_id}: JSON faltando (o par precisa das duas partes)")
                continue
            ep = carregar_ep(ep_id)
            if "História de ficção" not in ep.get("legenda_post", ""):
                problemas.append(f"{ep_id}: legenda sem o aviso de ficção")
            if len(ep.get("legenda_post", "")) > 2200:
                problemas.append(f"{ep_id}: legenda passa de 2200 caracteres")
            mp4 = config.REELS / f"{ep_id}.mp4"
            if mp4.exists():
                d = duracao(mp4)
                if not config.DURACAO_MIN_S <= d <= config.DURACAO_MAX_S:
                    problemas.append(f"{ep_id}: duração {d:.1f}s fora do limite")
    prontos = [n for n in completos_prontos() if f"ep{n:03d}-p1" not in feitos]
    return {"episodios": len(episodios()), "prontos_nao_publicados": len(prontos),
            "reserva_ok": len(prontos) >= config.RESERVA_MINIMA, "problemas": problemas}


if __name__ == "__main__":
    import sys
    r = lint()
    print(json.dumps(r, ensure_ascii=False, indent=1))
    if "--resumo" in sys.argv:
        print(f"prontos={r['prontos_nao_publicados']}")
        print(f"reserva_baixa={'false' if r['reserva_ok'] else 'true'}")
    sys.exit(1 if r["problemas"] else 0)
