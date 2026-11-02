"""Testes da regra obrigatória de imagens SiliconFlow no Instagram."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from motor.cinematic_story_art import preparar_quadros
from src import fila
from motor.siliconflow_policy import (
    SiliconFlowObrigatoria, validar_configuracao, validar_relatorio,
    validar_quadros, validar_metadados, validar_arquivo_publicacao,
)


def relatorio():
    return {
        "config": {"image_provider": "siliconflow",
                   "image_model": "black-forest-labs/FLUX.1-schnell"},
        "requested": 10, "ready": 10, "fallbacks": 0,
        "scenes": [
            {"scene": i, "start": i * 3.0, "end": (i + 1) * 3.0,
             "status": "generated", "image_provider": "siliconflow",
             "asset": f"visual-scene-{i:02d}.png"} for i in range(10)
        ],
    }


def metadados():
    return {
        "motor": "remotion", "visual_images_requested": 10,
        "visual_images_ready": 10, "visual_images_fallbacks": 0,
        "siliconflow_confirmado": True, "siliconflow_provedor": "siliconflow",
        "siliconflow_ilustracoes": 10, "siliconflow_quadros": 6,
        "siliconflow_quadros_locais": 0,
    }


class PoliticaInstagram(unittest.TestCase):
    def test_dez_imagens_api_aprovadas(self):
        self.assertEqual(validar_relatorio(relatorio()), 10)
        validar_metadados(metadados())

    def test_ready_nao_prova_que_imagem_e_paga(self):
        r = relatorio()
        r["scenes"][5]["status"] = "local_fallback"
        with self.assertRaises(SiliconFlowObrigatoria):
            validar_relatorio(r)

    def test_cache_de_outro_provedor_e_rejeitado(self):
        r = relatorio()
        r["scenes"][2]["status"] = "cache"
        r["scenes"][2]["image_provider"] = "openai"
        with self.assertRaises(SiliconFlowObrigatoria):
            validar_relatorio(r)

    def test_todos_os_quadros_tem_que_ser_siliconflow(self):
        with self.assertRaises(SiliconFlowObrigatoria):
            validar_quadros([{"origin": "generated"}, {"origin": "cinematic_cpu"}])
        self.assertEqual(validar_quadros([{"origin": "generated"}, {"origin": "cache"}]), 2)

    def test_produtor_interrompe_sem_chave(self):
        cfg = {"image_provider": "siliconflow", "auto_visual_images": True,
               "target_images": 10, "max_images": 10}
        with patch.dict(os.environ, {"NINA_REQUIRE_SILICONFLOW": "1",
                                     "NINA_ALLOW_PAID_IMAGE_API": "1",
                                     "SILICONFLOW_API_KEY": ""}):
            with self.assertRaises(SiliconFlowObrigatoria):
                validar_configuracao(cfg, {})

    def test_publicador_bloqueia_metadados_antigos_ou_locais(self):
        with tempfile.TemporaryDirectory() as tmp:
            reels = Path(tmp)
            self.assertFalse(validar_arquivo_publicacao(reels, "ep118"))
            arq = reels / "ep118-render.json"
            arq.write_text(json.dumps({"visual_images_ready": 10}), encoding="utf-8")
            self.assertFalse(validar_arquivo_publicacao(reels, "ep118"))
            meta = metadados()
            meta["siliconflow_quadros_locais"] = 1
            arq.write_text(json.dumps(meta), encoding="utf-8")
            self.assertFalse(validar_arquivo_publicacao(reels, "ep118"))
            meta["siliconflow_quadros_locais"] = 0
            arq.write_text(json.dumps(meta), encoding="utf-8")
            self.assertTrue(validar_arquivo_publicacao(reels, "ep118"))

    def test_remotion_reutiliza_so_imagens_pagas_nas_lacunas(self):
        r = relatorio()
        ep = {"titulo": "História completa", "batidas": [
            {"fala": f"Aconteceu algo na cena {i}"} for i in range(10)]}
        segs = [{"ini": i * 4.0, "fim": (i + 1) * 4.0} for i in range(10)]
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "assets"
            base.mkdir()
            for i in range(10):
                Image.new("RGB", (512, 512), (i * 20, 60, 100)).save(
                    base / f"visual-scene-{i:02d}.png")
            frames = preparar_quadros(ep, segs, 42, Path(tmp) / "public",
                                     base_assets=base, visual_report=r,
                                     strict_siliconflow=True)
            self.assertEqual(len(frames), 6)
            self.assertEqual(validar_quadros(frames), 6)
            self.assertTrue(all((Path(tmp) / "public" / f["src"]).is_file() for f in frames))

    def test_fila_nao_publica_reel_sem_validacao(self):
        meta = metadados()
        with tempfile.TemporaryDirectory() as tmp:
            reels = Path(tmp)
            (reels / "ep113.mp4").write_bytes(b"mp4 ficticio de teste")
            (reels / "ep113.hash").write_text("hash-valido", encoding="utf-8")
            (reels / "ep113-capa.jpg").write_bytes(b"capa teste")
            with patch.object(fila.config, "REELS", reels), patch.object(
                fila, "assinatura", return_value="hash-valido"
            ):
                self.assertFalse(fila.pronto("ep113"))
                (reels / "ep113-render.json").write_text(
                    json.dumps(meta), encoding="utf-8")
                self.assertTrue(fila.pronto("ep113"))
                meta["siliconflow_quadros_locais"] = 1
                (reels / "ep113-render.json").write_text(
                    json.dumps(meta), encoding="utf-8")
                self.assertFalse(fila.pronto("ep113"))

    def test_remotion_interrompe_se_faltar_imagem(self):
        r = relatorio()
        ep = {"titulo": "História completa", "batidas": [
            {"fala": f"Cena {i}"} for i in range(10)]}
        segs = [{"ini": i * 3.0, "fim": (i + 1) * 3.0} for i in range(10)]
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                preparar_quadros(ep, segs, 30, Path(tmp) / "public",
                                 base_assets=Path(tmp) / "assets", visual_report=r,
                                 strict_siliconflow=True)


if __name__ == "__main__":
    unittest.main()
