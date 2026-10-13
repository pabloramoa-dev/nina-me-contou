"""Direção e atuação determinísticas da Nina, sem chamadas de IA e sem APIs pagas.

Cada batida recebe um gesto (braço livre), ritmo e enquadramento.
O mesmo roteiro sempre gera o mesmo plano e pode ser inspecionado em direcao.json.
"""
from __future__ import annotations

import math
import re

GESTOS = ("neutro", "contar", "perguntar", "alertar", "surpresa", "ponderar", "acolher")
# Deslocamento relativo da mão esquerda, em unidades da personagem ANTES da escala.
DESLOCAMENTOS = {
    "neutro": (0.0, 0.0),
    "contar": (-0.22, 0.23),
    "perguntar": (-0.48, 0.43),
    "alertar": (-0.30, 0.63),
    "surpresa": (-0.55, 0.58),
    "ponderar": (-0.16, 0.34),
    "acolher": (-0.32, 0.18),
}
EXPRESSOES = {"neutra", "desconfiada", "chocada", "ironica", "triste", "brava"}


def gesto_da_batida(batida: dict, indice: int) -> str:
    """Regras transparentes; gesto explícito é respeitado quando conhecido."""
    definido = str(batida.get("gesto") or "").strip().lower()
    if definido in GESTOS:
        return definido
    fala = str(batida.get("fala") or "")
    expr = batida.get("expr", "neutra")
    if expr == "chocada":
        return "surpresa"
    if expr == "brava" or re.search(r"\b(cuidado|atenção|nunca|mentira|verdade)\b", fala, re.I):
        return "alertar"
    if "?" in fala or re.search(r"\b(pergunta|conta aí|comenta aí)\b", fala, re.I):
        return "perguntar"
    if expr == "triste":
        return "acolher"
    if expr == "desconfiada":
        return "ponderar"
    # Evita ficar repetindo o mesmo movimento quando o roteiro é neutro.
    return ("contar", "neutro", "ponderar")[indice % 3]


def planejar(episodio: dict, segmentos: list[dict]) -> list[dict]:
    batidas = episodio.get("batidas", [])
    if len(batidas) != len(segmentos) or not batidas:
        raise ValueError("A direção exige uma batida para cada segmento de voz")
    plano = []
    fim_anterior = 0.0
    for i, (b, s) in enumerate(zip(batidas, segmentos)):
        inicio, fim = float(s["ini"]), float(s["fim"])
        if not all(math.isfinite(v) for v in (inicio, fim)) or inicio < fim_anterior - .001 or fim <= inicio:
            raise ValueError("Timeline inválida no planejamento de direção")
        gesto = gesto_da_batida(b, i)
        expr = b.get("expr", "neutra")
        cam = ("aproximar" if b.get("zoom") or expr == "chocada" else
               "abrir" if i and i % 4 == 0 else
               "aproximar_suave" if gesto in ("alertar", "perguntar") else "manter")
        plano.append({"i": i, "inicio": round(inicio, 3), "fim": round(fim, 3),
                      "gesto": gesto, "expressao": expr if expr in EXPRESSOES else "neutra",
                      "camera": cam,
                      "energia": 1.0 if gesto in ("surpresa", "alertar") else .8,
                      "motivo": "gesto explícito" if b.get("gesto") in GESTOS else "fala e expressão"})
        fim_anterior = fim
    return plano


def deslocamento(gesto: str, tempo: float, inicio: float, fim: float, energia: float = 1.0) -> tuple[float, float]:
    """Entrada/saída suaves, sem teletransporte de braço entre cenas."""
    if gesto not in DESLOCAMENTOS or fim <= inicio or tempo < inicio or tempo >= fim:
        return (0.0, 0.0)
    rampa = min(.34, (fim - inicio) / 3)
    if rampa <= 0:
        return (0.0, 0.0)
    entrada = max(0.0, min(1.0, (tempo - inicio) / rampa))
    saida = max(0.0, min(1.0, (fim - tempo) / rampa))
    peso = min(entrada, saida)
    peso = peso * peso * (3 - 2 * peso)
    # Pequena gesticulação enquanto sustenta a fala.
    pulso = 1 + .06 * math.sin(tempo * 4.0)
    dx, dy = DESLOCAMENTOS[gesto]
    return (dx * peso * energia * pulso, dy * peso * energia * pulso)


def camera_destino(item: dict) -> tuple[float, int]:
    """Retorna zoom leve e deslocamento horizontal sem mudar a área de legendas."""
    camera = item.get("camera")
    if camera == "aproximar":
        return (1.10, 0)
    if camera == "aproximar_suave":
        return (1.055, -8 if item["i"] % 2 else 8)
    if camera == "abrir":
        return (1.0, 0)
    return (1.025, -8 if item["i"] % 2 else 8)
