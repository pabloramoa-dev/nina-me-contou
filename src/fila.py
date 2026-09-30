"""Fila de publicação da Nina.

Regras
- Episódio = par epNNN-p1 + epNNN-p2. Só entra na fila quando OS DOIS MP4 e as
  DUAS capas existem em reels/ (nunca publicar parte 1 sem a 2 pronta).
- 4 horários por dia (8h, 12h, 16h, 20h), sempre em sequência:
  se há uma parte 2 cuja parte 1 já saiu, ela vem primeiro; senão, sai a parte 1
  do menor episódio completo ainda não publicado. Na prática:
  8h = parte 1 · 12h = parte 2 · 16h = parte 1 · 20h = parte 2 (2 episódios/dia).
- Um vídeo só está "pronto" se foi renderizado a partir da versão ATUAL do roteiro
  (reels/<id>.hash). Roteiro editado = volta pro estúdio antes de publicar.
- Nunca publica o mesmo id duas vezes (ledger publicados.json).
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


def assinatura(ep_id: str) -> str:
    """Impressão digital do roteiro (JSON canônico) — muda a cada edição."""
    ep = carregar_ep(ep_id)
    bruto = json.dumps({"roteiro": ep, "render": versao()}, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha1(bruto).hexdigest()[:16]


def desatualizado(ep_id: str) -> bool:
    """True se o MP4 não existe ou foi feito com outra versão do roteiro.
    Vídeos antigos sem .hash só voltam pro estúdio se ainda não foram publicados."""
    if not (config.REELS / f"{ep_id}.mp4").exists():
        return True
    h = config.REELS / f"{ep_id}.hash"
    if h.exists():
        return h.read_text().strip() != assinatura(ep_id)
    return ep_id not in ids_publicados()


def pronto(ep_id: str) -> bool:
    return (config.REELS / f"{ep_id}-capa.jpg").exists() and not desatualizado(ep_id)


def episodios() -> list[int]:
    nums = set()
    for f in config.EPISODIOS.glob("ep*-p*.json"):
        m = RX.match(f.stem)
        if m:
            nums.add(int(m.group(1)))
    return sorted(nums)


def completos_prontos() -> list[int]:
    return [n for n in episodios() if pronto(f"ep{n:03d}-p1") and pronto(f"ep{n:03d}-p2")]


def proximo(horario: str | None = None) -> str | None:
    """Próximo vídeo da sequência (o horário não muda a ordem, só os Stories)."""
    feitos = ids_publicados()
    for n in episodios():
        p1, p2 = f"ep{n:03d}-p1", f"ep{n:03d}-p2"
        if p1 in feitos and p2 not in feitos:
            # continuação pendente: sai antes de qualquer episódio novo
            return p2 if pronto(p2) else None
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

