"""Regra de publicação: todo Reel da Nina para Instagram usa imagens SiliconFlow.

A produção falha se o provedor pago estiver indisponível. A fila nunca aceita
um MP4 sem prova de procedência, mesmo que o arquivo de vídeo exista.
Não registra chaves, prompts privados ou URLs efêmeras nos metadados.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

PROVEDOR = "siliconflow"
FONTES_PAGAS = {"generated", "cache"}


class SiliconFlowObrigatoria(RuntimeError):
    """Não enviar material local/sem origem confirmada para o Instagram."""


def obrigatoria() -> bool:
    return os.getenv("NINA_REQUIRE_SILICONFLOW", "0").strip().lower() in (
        "1", "true", "yes", "sim"
    )


def validar_configuracao(cfg: dict, episodio: dict | None = None) -> None:
    """Checagem antecipada, antes de cobrar/renderizar um episódio de produção."""
    if not obrigatoria():
        return
    if cfg.get("image_provider") != PROVEDOR:
        raise SiliconFlowObrigatoria("Instagram exige image_provider=siliconflow")
    if cfg.get("auto_visual_images") is not True:
        raise SiliconFlowObrigatoria("Geração de imagens desativada")
    if int(cfg.get("target_images", 0)) != 10 or int(cfg.get("max_images", 0)) != 10:
        raise SiliconFlowObrigatoria("Instagram exige exatamente 10 imagens SiliconFlow")
    if os.getenv("NINA_ALLOW_PAID_IMAGE_API", "0").lower() not in ("1", "true", "sim"):
        raise SiliconFlowObrigatoria("API paga não autorizada para produção")
    if not os.getenv("SILICONFLOW_API_KEY", "").strip():
        raise SiliconFlowObrigatoria("SILICONFLOW_API_KEY ausente: produção interrompida")
    if (episodio or {}).get("approved_visual_assets"):
        raise SiliconFlowObrigatoria("Assets locais/aprovados não substituem imagens SiliconFlow")
    if os.getenv("NINA_MOTOR", "hyperframes") != "hyperframes":
        raise SiliconFlowObrigatoria("Pipeline Instagram exige HyperFrames")
    if os.getenv("NINA_FINAL_COMPOSITOR", "remotion") != "remotion":
        raise SiliconFlowObrigatoria("Pipeline Instagram exige Remotion")
    if (episodio or {}).get("visual_style", os.getenv("NINA_STORY_STYLE", "cinematic_2d")) != "cinematic_2d":
        raise SiliconFlowObrigatoria("Painel de imagens SiliconFlow requer cinematic_2d")


def validar_relatorio(report: dict) -> int:
    """O número 'ready' inclui fallback local e nunca é prova suficiente."""
    cfg = report.get("config") or {}
    if cfg.get("image_provider") != PROVEDOR:
        raise SiliconFlowObrigatoria("Relatório não usa provedor SiliconFlow")
    scenes = report.get("scenes", [])
    if not isinstance(scenes, list) or len(scenes) != 10 or report.get("requested") != 10:
        raise SiliconFlowObrigatoria("Relatório incompleto: são exigidas 10 imagens")
    if report.get("fallbacks", 0) or report.get("ready") != 10:
        raise SiliconFlowObrigatoria("Há imagens de reserva/falhas no relatório")
    for i, scene in enumerate(scenes):
        if scene.get("status") not in FONTES_PAGAS:
            raise SiliconFlowObrigatoria(f"Cena {i} não foi produzida pela SiliconFlow")
        if scene.get("image_provider") != PROVEDOR:
            raise SiliconFlowObrigatoria(f"Cena {i} sem origem SiliconFlow comprovada")
        if not str(scene.get("asset", "")).startswith("visual-scene-"):
            raise SiliconFlowObrigatoria(f"Cena {i} sem arquivo de imagem")
    return len(scenes)


def validar_quadros(frames: list[dict]) -> int:
    if not frames:
        raise SiliconFlowObrigatoria("Remotion sem quadros de imagem SiliconFlow")
    for i, frame in enumerate(frames):
        if frame.get("origin") not in FONTES_PAGAS:
            raise SiliconFlowObrigatoria(f"Quadro Remotion {i} usa imagem local")
    return len(frames)


def validar_metadados(meta: dict) -> None:
    """Portão de segurança antes de o arquivo entrar na fila do Instagram."""
    if (meta.get("siliconflow_confirmado") is not True
            or meta.get("siliconflow_provedor") != PROVEDOR
            or meta.get("siliconflow_ilustracoes") != 10
            or not isinstance(meta.get("siliconflow_quadros"), int)
            or meta.get("siliconflow_quadros") <= 0
            or meta.get("siliconflow_quadros_locais") != 0
            or meta.get("motor") != "remotion"
            or meta.get("visual_images_requested") != 10
            or meta.get("visual_images_ready") != 10
            or meta.get("visual_images_fallbacks") != 0
            or meta.get("storyboard_mode") not in ("openai_roteiro", "siliconflow_roteiro")
            or meta.get("storyboard_scenes") != 10
            or meta.get("gancho_antecipacao_versao") != "nina-antecipacao-20261102-v2"):
        raise SiliconFlowObrigatoria("Vídeo sem confirmação de 10 imagens SiliconFlow")


def validar_arquivo_publicacao(reels: Path, ep_id: str) -> bool:
    caminho = Path(reels) / f"{ep_id}-render.json"
    try:
        validar_metadados(json.loads(caminho.read_text(encoding="utf-8")))
        return True
    except (OSError, ValueError, TypeError, SiliconFlowObrigatoria):
        return False
