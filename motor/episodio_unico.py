#!/usr/bin/env python3
"""Consolida roteiros legados p1/p2 em UMA história completa por vídeo.

Os arquivos p1/p2 ficam como arquivo histórico. Apenas epNNN.json entra
na fila nova. Nunca transforma nem republica uma história já publicada em partes.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EPISODIOS = ROOT / "episodios"
PUBLICADOS = ROOT / "conteudo" / "publicados.json"
RX_PARTE = re.compile(
    r"\b(?:parte\s*(?:1|2|um|dois)|primeira\s+parte|segunda\s+parte|"
    r"continua(?:ção)?\s+(?:na|no|em)\s+parte)\b", re.I
)
RX_CTA = re.compile(r"\bme\s+segue\b|\bsiga\s+a\s+nina\b|\bsegue\s+a\s+nina\b", re.I)

# Passagens de transição sem novos fatos inventados sobre os personagens.
# Servem para dar ritmo à narração; não substituem as cenas e o desfecho.
PONTES = [
    "O curioso é como os detalhes se encaixam depois que alguém resolve perguntar, em vez de simplesmente adivinhar. Uma palavra fora do lugar pode mudar toda a interpretação.",
    "Até aquele momento, cada pessoa enxergava só um pedaço do que aconteceu. A diferença começou quando as versões foram colocadas lado a lado, sem atalhos.",
    "A Nina conta isso porque uma pista isolada pode parecer definitiva. Mas, quando a conversa avança, até o detalhe que parecia mais óbvio ganha outro sentido.",
    "E tinha uma coisa importante naquela história: não era possível voltar no tempo e apagar o que já tinha sido dito. Restava descobrir o que fazer com a verdade.",
    "Ninguém precisava transformar a situação num espetáculo. O que faltava era ouvir a explicação inteira e separar o que alguém imaginou daquilo que realmente aconteceu.",
    "O silêncio também estava pesando. Não por revelar uma resposta, mas porque deixou cada dúvida crescer até parecer maior que os próprios acontecimentos.",
    "A cada pergunta, surgia um novo ângulo da mesma situação. E o que parecia apenas uma coincidência começou a exigir uma conversa de verdade.",
    "Antes de tomar uma decisão, era preciso entender a ordem das coisas. Um detalhe contado fora de contexto pode fazer uma história parecer completamente diferente.",
    "O mais difícil não era encontrar outro indício. Era aceitar que os fatos pediam calma, mesmo com tanta coisa parecendo urgente naquela hora.",
    "Quem acompanha uma história assim sabe que nem toda surpresa é uma confirmação. É preciso esperar os detalhes se revelarem antes de escolher um lado.",
    "Só que nenhuma explicação resolve tudo automaticamente. Depois da descoberta ainda vêm as conversas, as escolhas e as consequências para quem estava envolvido.",
    "E enquanto a história avançava, uma pergunta ficava no ar: o que mudou de fato? A resposta dependia menos do susto inicial e mais das atitudes seguintes.",
]

def _texto(batida: dict) -> str:
    return str(batida.get("fala", "")).strip()

def _ignorar(batida: dict) -> bool:
    fala = _texto(batida)
    return not fala or bool(RX_PARTE.search(fala)) or bool(RX_CTA.search(fala)) or (
        isinstance(batida.get("arte"), list) and batida["arte"][:1] == ["seguir"]
    )

def _normalizar(texto: str) -> str:
    return " ".join(re.findall(r"[\wÀ-ÿ]+", texto.lower()))

def _repeticao(batida: dict, anteriores: list[dict]) -> bool:
    texto = _normalizar(_texto(batida))
    if not texto:
        return True
    return any(
        SequenceMatcher(None, texto, _normalizar(_texto(outro))).ratio() > 0.70
        or (len(_normalizar(_texto(outro))) > 38 and
            _normalizar(_texto(outro)) in texto)
        for outro in anteriores
    )

def _ponte(numero: int, pos: int) -> dict:
    fala = PONTES[(numero * 7 + pos * 5) % len(PONTES)]
    return {"fala": fala, "expr": "neutra",
            "arte": ["conversa"], "destaque": []}

def _palavras(batidas: list[dict]) -> int:
    return sum(len(_texto(b).split()) for b in batidas)

def consolidar(p1: dict, p2: dict, alvo_palavras: int = 385) -> dict:
    """Conecta abertura, desenvolvimento, revelação e encerramento.

    A duração exata depende da voz do sintetizador, mas ~385 palavras, mais
    pausas e CTA, corresponde a aproximadamente três minutos.
    """
    if p1.get("ep") != p2.get("ep"):
        raise ValueError("Partes pertencem a episódios diferentes")
    n = int(p1["ep"])
    inicio = [copy.deepcopy(b) for b in p1.get("batidas", []) if not _ignorar(b)]
    fim = []
    for b in p2.get("batidas", []):
        if not _ignorar(b) and not _repeticao(b, inicio + fim):
            fim.append(copy.deepcopy(b))
    if len(inicio) < 3 or len(fim) < 3:
        raise ValueError(f"ep{n:03d}: roteiro incompleto, não vai para a fila")

    # A primeira cena termina em suspense interno, mas o mesmo vídeo já entrega
    # a descoberta e um desfecho. Os ganchos 'volte na parte 1/2' são descartados.
    batidas = inicio + fim
    usadas: set[str] = set()
    i = 0
    while _palavras(batidas) < alvo_palavras and i < len(PONTES):
        ponte = _ponte(n, i)
        i += 1
        if ponte["fala"] in usadas:
            continue
        usadas.add(ponte["fala"])
        # Passagens distribuídas ao longo da história, nunca depois do final.
        lugar = min(max(2, len(batidas) // 2), len(batidas) - 2)
        if i % 2 == 0:
            lugar = min(lugar + 2, len(batidas) - 2)
        batidas.insert(lugar, ponte)

    # Fecha a história antes do convite final (incluído pelo motor/cta.py).
    if not any(k in " ".join(_texto(b).lower() for b in fim)
               for k in ("decidiu", "descobriu", "resolveu", "aconteceu", "terminou",
                         "conseguiu", "encontrou", "admitiu", "voltou", "escolheu")):
        batidas.append({
            "fala": "No fim, a conversa trouxe consequências reais. As pessoas envolvidas "
                    "precisaram assumir suas escolhas e decidir como seguir, sem deixar "
                    "perguntas essenciais sem resposta.",
            "expr": "neutra", "arte": ["manchete_v", "O DESFECHO"],
            "destaque": ["escolhas"],
        })
    titulo = str(p1.get("titulo") or p2.get("titulo") or f"Episódio {n}")
    gancho = _texto(inicio[0])
    legenda = (
        f"{titulo}\n\n{gancho}\n\nA história tem começo, reviravolta e desfecho "
        "neste vídeo. Qual seria sua decisão?\n\n"
        "História de ficção. Personagens e acontecimentos fictícios.\n\n"
        "#storytime #historias #fofoca #reviravolta #ninamecontou"
    )
    return {
        "id": f"ep{n:03d}", "ep": n, "parte": "unica",
        "titulo": titulo, "temporada": p1.get("temporada", ""),
        "cenario": p1.get("cenario", "tarde"),
        "batidas": batidas, "fim": "HISTÓRIA COMPLETA",
        "legenda_post": legenda, "legenda_tiktok": legenda,
        "gerado_automaticamente": bool(p1.get("gerado_automaticamente")),
        "origem_roteiros": [p1["id"], p2["id"]],
        "formato": "historia_unica_3min",
    }

def publicados() -> set[str]:
    if not PUBLICADOS.exists():
        return set()
    return {str(x.get("id")) for x in json.loads(PUBLICADOS.read_text("utf-8"))
            if x.get("id") and not x.get("ensaio")}

def converter_pendentes(base: Path = EPISODIOS, feitos: set[str] | None = None) -> list[str]:
    """Materializa roteiros únicos inéditos; preserva todos os pares históricos."""
    feitos = publicados() if feitos is None else feitos
    gerados = []
    for arq1 in sorted(base.glob("ep*-p1.json")):
        num = re.fullmatch(r"ep(\d{3})-p1", arq1.stem)
        if not num:
            continue
        prefixo = f"ep{num.group(1)}"
        arq2 = base / f"{prefixo}-p2.json"
        destino = base / f"{prefixo}.json"
        if destino.exists() or not arq2.exists():
            continue
        if any(id_ in feitos for id_ in (prefixo, prefixo + "-p1", prefixo + "-p2")):
            continue
        ep = consolidar(json.loads(arq1.read_text("utf-8")),
                         json.loads(arq2.read_text("utf-8")))
        destino.write_text(json.dumps(ep, ensure_ascii=False, indent=1) + "\n",
                           encoding="utf-8")
        gerados.append(prefixo)
    return gerados

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--alvo-palavras", type=int, default=385)
    args = ap.parse_args()
    convertidos = converter_pendentes()
    print(json.dumps({"episodios_unicos_criados": len(convertidos),
                      "ids": convertidos, "alvo_palavras": args.alvo_palavras},
                     ensure_ascii=False))

if __name__ == "__main__":
    main()
