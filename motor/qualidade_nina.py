"""Verificações locais e relatório do MP4 da Nina, sem chamadas de IA.

Não afirma detectar colisão visual real: isso exige render/screenshot em navegador.
"""
from __future__ import annotations

import json
import re
from pathlib import Path


def analisar(episodio: dict, segmentos: list[dict], plano: list[dict],
            html_path: str | Path, visual_report: dict, mp4_probe: dict) -> dict:
    html = Path(html_path).read_text(encoding="utf-8")
    batidas = episodio.get("batidas", [])
    erros, alertas = [], []
    if not batidas or len(batidas) != len(segmentos) or len(plano) != len(batidas):
        erros.append("roteiro, narração e direção têm contagens diferentes")
    secoes = re.findall(r'<section id="p\d+"[^>]*>.*?</section>', html, flags=re.S)
    if len(secoes) != len(batidas):
        erros.append("quantidade de quadros diverge das falas")
    for i, secao in enumerate(secoes):
        if 'story_frame_image' in secao:
            if 'class="note"' in secao or 'class="bubble"' in secao:
                erros.append(f"quadro de imagem {i}: legenda interna indevida")
            if '<img' not in secao:
                erros.append(f"quadro de imagem {i}: sem imagem")
        if '<h1' not in secao:
            erros.append(f"quadro {i}: sem título")
    if 'id="voice"' not in html or 'id="base"' not in html:
        erros.append("áudio ou vídeo base ausente da composição")
    if 'class="caps"' not in html and 'class="pill"' not in html:
        erros.append("nenhuma camada de legenda encontrada")
    if not mp4_probe.get("streams"):
        erros.append("relatório do ffprobe sem streams")
    hook = str(batidas[0].get("fala", "")) if batidas else ""
    if len(hook.split()) > 24:
        alertas.append("gancho longo: avaliar os primeiros segundos")
    if visual_report.get("ready", 0) == 0:
        alertas.append("nenhuma imagem narrativa preparada; conferir fallback")
    if len({b.get("fala", "") for b in batidas}) < len(batidas):
        alertas.append("falas repetidas no mesmo episódio")
    if len({item["gesto"] for item in plano}) < 2 and len(plano) > 2:
        alertas.append("pouca variedade de gestos")
    return {"aprovado_tecnicamente": not erros,
            "checagens": ["alinhamento de cenas", "estrutura de legendas",
                          "ausência de texto interno sobre as imagens",
                          "títulos e trilhas na composição", "integridade dos streams via ffprobe"],
            "erros": erros, "alertas": alertas, "batidas": len(batidas),
            "gestos_distintos": sorted({x["gesto"] for x in plano}),
            "ilustracoes_prontas": visual_report.get("ready", 0),
            "observacao": "Enquadramento visual e legibilidade ainda requerem revisão dos quadros renderizados."}


def gravar(relatorio: dict, caminho: str | Path) -> None:
    Path(caminho).write_text(json.dumps(relatorio, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
