"""Fila da Nina: cada epNNN.json é UM vídeo, com início, meio e fim.

Os pares p1/p2 antigos permanecem apenas como histórico. Episódios que
já tiveram qualquer parte publicada nunca são publicados de novo.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone, timedelta

from src import config
from motor.render_version import versao

BRT = timezone(timedelta(hours=-3))
RX = re.compile(r"^ep(\d{3})$")


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


def ja_publicado(ep_id: str, feitos: set[str] | None = None) -> bool:
    feitos = ids_publicados() if feitos is None else feitos
    return any(id_ in feitos for id_ in (ep_id, ep_id + "-p1", ep_id + "-p2"))


def carregar_ep(ep_id: str) -> dict:
    return json.loads((config.EPISODIOS / f"{ep_id}.json").read_text(encoding="utf-8"))


def assinatura(ep_id: str) -> str:
    ep = carregar_ep(ep_id)
    bruto = json.dumps({"roteiro": ep, "render": versao()}, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha1(bruto).hexdigest()[:16]


def desatualizado(ep_id: str) -> bool:
    if not (config.REELS / f"{ep_id}.mp4").exists():
        return True
    h = config.REELS / f"{ep_id}.hash"
    if h.exists():
        return h.read_text().strip() != assinatura(ep_id)
    return ep_id not in ids_publicados()


def pronto(ep_id: str) -> bool:
    return (config.REELS / f"{ep_id}-capa.jpg").exists() and not desatualizado(ep_id)


def episodios() -> list[int]:
    return sorted(int(m.group(1)) for f in config.EPISODIOS.glob("ep*.json")
                  if (m := RX.fullmatch(f.stem)))


def completos_prontos() -> list[int]:
    feitos = ids_publicados()
    return [n for n in episodios()
            if not ja_publicado(f"ep{n:03d}", feitos) and pronto(f"ep{n:03d}")]


def proximo(horario: str | None = None) -> str | None:
    """Um único vídeo completo por horário; não existe mais continuação."""
    prontos = completos_prontos()
    return f"ep{prontos[0]:03d}" if prontos else None


def duracao(caminho) -> float:
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                   "-of", "csv=p=0", str(caminho)])
    return float(out.strip())


def lint() -> dict:
    problemas = []
    for n in episodios():
        ep_id = f"ep{n:03d}"
        ep = carregar_ep(ep_id)
        if ep.get("parte") != "unica":
            problemas.append(f"{ep_id}: episódio não está marcado como parte única")
        if "História de ficção" not in ep.get("legenda_post", ""):
            problemas.append(f"{ep_id}: legenda sem o aviso de ficção")
        if len(ep.get("legenda_post", "")) > 2200:
            problemas.append(f"{ep_id}: legenda passa de 2200 caracteres")
        if re.search(r"\b(?:parte\s*(?:1|2|um|dois)|continua na parte)\b",
                     " ".join(str(b.get("fala", "")) for b in ep.get("batidas", [])), re.I):
            problemas.append(f"{ep_id}: referências a partes no roteiro")
        mp4 = config.REELS / f"{ep_id}.mp4"
        if mp4.exists():
            d = duracao(mp4)
            if not config.DURACAO_MIN_S <= d <= config.DURACAO_MAX_S:
                problemas.append(f"{ep_id}: duração {d:.1f}s fora do alvo de ~3 min")
    prontos = completos_prontos()
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
