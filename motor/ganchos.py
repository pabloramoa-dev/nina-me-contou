"""Aberturas da Nina baseadas apenas em fatos já presentes no roteiro."""
from __future__ import annotations

import copy
import re

VERSAO = "gancho-descoberta-20261026-v1"


def _fala(batidas: list, pos: int) -> str:
    if pos >= len(batidas):
        return ""
    return str(batidas[pos].get("fala", "")).strip()


def _destaques(fala: str) -> list[str]:
    ignorar = {"encontrou", "disse", "estava", "ainda", "quando", "aquele",
               "aquela", "porque", "dentro", "nenhuma", "alguma", "precisava",
               "conhecia", "lugar", "pista", "levava", "nome", "depois"}
    palavras = re.findall(r"[\wÀ-ÿ]{5,}", fala, flags=re.UNICODE)
    return [p for p in palavras if p.lower() not in ignorar][:2]


def _gancho_automatico(ep: dict) -> str | None:
    bats = ep["batidas"]
    if ep.get("parte") == 1:
        evento = re.search(r"\b([A-ZÀ-Ý][\wÀ-ÿ-]+) encontrou (.+?)\.", _fala(bats, 2))
        bairro = re.search(r"\ba pista apontava para (.+?)\.", _fala(bats, 4), re.I)
        negacao = re.search(r"perguntou de forma casual se (.+?) conhecia aquele lugar", _fala(bats, 5))
        if evento and bairro and negacao:
            nome, objeto = evento.groups()
            return (f"{nome} encontrou {objeto}. A pista levava a {bairro.group(1)}, "
                    f"mas {negacao.group(1)} negou conhecer o lugar.")
    if ep.get("parte") == 2:
        nome = re.match(r"([A-ZÀ-Ý][\wÀ-ÿ-]+) esperou", _fala(bats, 1))
        descoberto = re.search(r"reconheceu o nome de (.+?) numa caixa de correspondência", _fala(bats, 3))
        outro = re.search(r"ficou claro que (.+?) (?:tinha|estava|mantinha|guardava|usava|frequentava|planejava|ajudava|escondia)", _fala(bats, 5))
        if nome and descoberto:
            complemento = (f" E {outro.group(1)} ainda precisava explicar aquela pista." if outro else " A pista finalmente tinha um nome.")
            return f"{nome.group(1)} encontrou o nome de {descoberto.group(1)} na caixa de correspondência.{complemento}"
    return None


def _generica(fala: str) -> bool:
    return bool(re.match(
        r"^(?:Se você (?:caiu|chegou)|Se chegou|Pra quem (?:caiu|chegou)|"
        r"Antes de (?:eu )?continuar|Hoje eu (?:vou|quero) contar|"
        r"Vou te contar|Essa história (?:começa|chegou)|E aí, gente[,!])\b",
        fala, flags=re.I))


def _nao_e_historia(ep: dict) -> bool:
    bats = ep.get("batidas")
    if not isinstance(bats, list) or len(bats) < 5:
        return True
    if not isinstance(bats[0], dict) or not _fala(bats, 0):
        return True
    if re.search(r"quiz|promo|publicidade|anúncio|apresentação", str(ep.get("temporada", "")), re.I):
        return True
    if re.search(r"\b(?:promo|crossover|teste de voz)\b", str(ep.get("titulo", "")), re.I):
        return True
    return bool(re.match(r"^(?:eu sou a Nina|quero ver quem tem olho bom|olha bem essa sala)",
                         _fala(bats, 0), re.I))


def aplicar_gancho(ep: dict) -> dict:
    """Evita invenções, repetições e alterações no desfecho."""
    out = copy.deepcopy(ep)
    if _nao_e_historia(out) or out.get("gancho_versao") == VERSAO:
        return out
    bats = out["batidas"]
    antigo = _fala(bats, 0)
    modelo = "abertura_direta_existente"
    novo = _gancho_automatico(out) if out.get("gerado_automaticamente") else None
    if novo:
        bats[0]["fala"] = novo
        bats[0]["expr"] = "desconfiada"
        bats[0]["destaque"] = _destaques(novo)
        bats[0].pop("tela", None)
        modelo = "descoberta_e_contradicao" if out.get("parte") == 1 else "descoberta_na_continuacao"
    elif _generica(antigo) and len(bats) > 1 and _fala(bats, 1):
        bats.pop(0)
        modelo = "entrada_direta_na_cena"
    elif antigo.lower().startswith("tudo começou com um detalhe pequeno:"):
        resumo = antigo.split(":", 1)[1].strip()
        if resumo:
            bats[0]["fala"] = resumo[:1].upper() + resumo[1:]
            bats[0]["destaque"] = _destaques(bats[0]["fala"])
            bats[0].pop("tela", None)
            modelo = "detalhe_sem_introducao"
    out["gancho_versao"] = VERSAO
    out["gancho_modelo"] = modelo
    if out.get("gerado_automaticamente") and out.get("parte") == 1 and novo:
        legenda = str(out.get("legenda_post", ""))
        if "\n\n" in legenda:
            out["legenda_post"] = novo + "\n\n" + legenda.split("\n\n", 1)[1]
    return out
