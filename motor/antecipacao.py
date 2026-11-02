"""Gancho de antecipação na abertura, antes da voz e dos visuais.

Usa fatos do roteiro, sem inventar personagens, esconder o final ou abrir
parte 2. O corpo e o desfecho permanecem intactos.
"""
from __future__ import annotations

import copy
import re

VERSAO = "nina-antecipacao-20261102-v2"
FATO = re.compile(r"\b(?:segund[ao]|outr[ao]s?|duas|dois|foto|recibo|mensagem|bilhete|"
                  r"chave|áudio|video|vídeo|reserva|bolo|casamento|documento)\b", re.I)
SUSPENSE = re.compile(r"\b(?:mas|só que|quando|até que|sem imaginar|sem saber|"
                      r"porém|ninguém|então|antes que|inesperad[ao])\b", re.I)
GENERICA = re.compile(r"^(?:hoje vou|vou te contar|essa história começa|"
                      r"o que aconteceu depois|a protagonista desta|"
                      r"e aqui começa|se você chegou)", re.I)
FIM = re.compile(r"\b(?:no fim|no final|acabou|terminou|resolveram|"
                 r"decidiram encerrar|desfecho|me segue)\b", re.I)
RX_SENTENCA = re.compile(r"(?<=[.!?])\s+")


def _frase(fala: str) -> str:
    return RX_SENTENCA.split(fala.strip(), maxsplit=1)[0].strip()


def antecipar(ep: dict) -> dict:
    out = copy.deepcopy(ep)
    bats = out.get("batidas")
    if (not isinstance(bats, list) or len(bats) < 5 or
        not (out.get("parte") == "unica" or out.get("avulso")) or
        re.search(r"promo|quiz|teste de voz", str(out.get("titulo", "")), re.I)):
        return out
    if out.get("gancho_antecipacao_versao") == VERSAO:
        return out
    abertura = str(bats[0].get("fala", "")).strip()
    inicio = _frase(abertura)
    if not inicio or len(inicio.split()) < 5:
        raise ValueError("História sem fato concreto para gancho de antecipação")
    # Aberturas já concretas e com virada explícita não precisam ser reescritas.
    if (len(abertura.split()) >= 14 and SUSPENSE.search(abertura)
            and FATO.search(abertura) and not FIM.search(abertura)
            and not GENERICA.search(abertura)):
        modelo = "antecipacao_existente_validada"
    else:
        if GENERICA.search(inicio):
            concreto = next((_frase(str(b.get("fala", ""))) for b in bats[1:5]
                             if FATO.search(str(b.get("fala", "")))), "")
            if concreto:
                inicio = concreto
        # Busca uma pista concreta descrita antes do desfecho, nunca cria eventos.
        trecho = " ".join(str(b.get("fala", "")) for b in bats[1:max(5, len(bats)//2)])
        pista = re.search(r"\b(?:uma?|o|a)\s+(?:segund[ao]|outr[ao])\s+"
                          r"(?:[\wÀ-ÿ]+)(?:\s+[\wÀ-ÿ]+)?", trecho, re.I)
        if pista:
            ancora = pista.group(0).rstrip(".,;:")
            pergunta = f"Mas por que apareceu {ancora}?"
            modelo = "antecipacao_pista_concreta"
        else:
            nome = FATO.search(trecho)
            if not nome:
                raise ValueError("História sem pista específica para criar antecipação")
            pergunta = f"Mas o que {nome.group(0).lower()} tinha a ver com isso?"
            modelo = "antecipacao_pergunta_concreta"
        novo = inicio.rstrip(".!?") + ". " + pergunta
        if len(novo.split()) > 43:
            raise ValueError("Gancho de antecipação longo demais")
        bats[0]["fala"] = novo
        bats[0]["expr"] = "desconfiada"
        bats[0]["destaque"] = [p for p in re.findall(r"[\wÀ-ÿ]{5,}", novo)[:3]]
        bats[0].pop("tela", None)
    out["gancho_antecipacao_versao"] = VERSAO
    out["gancho_antecipacao_modelo"] = modelo
    return out
