"""Regressao: imagens locais da Nina sem API paga nem GPU."""
from pathlib import Path
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "motor"))
from motor import visual_images as V

class NinaImagensGratis(unittest.TestCase):
    def test_api_paga_bloqueada_por_padrao(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "NINA_ALLOW_PAID_IMAGE_API": "0"}):
            with patch.object(V.requests, "post", side_effect=AssertionError("chamada proibida")) as post:
                with self.assertRaisesRegex(V.ImageFailure, "paid_image_api_disabled"):
                    V.gerar("um desenho", V.config())
                post.assert_not_called()

    def test_quatro_imagens_sem_rede_no_episodio_normal(self):
        ep = {
            "id": "CPU_TESTE", "titulo": "Uma carta inesperada",
            "batidas": [
                {"fala": "Uma carta apareceu na porta sem assinatura."},
                {"fala": "O relogio estava parado quando ela chegou."},
                {"fala": "O carro nao estava onde deveria."},
                {"fala": "A familia descobriu uma pista importante."},
            ],
        }
        segmentos = [{"ini": 4*i, "fim": 4*(i+1)} for i in range(4)]
        with tempfile.TemporaryDirectory() as temp:
            with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "NINA_ALLOW_PAID_IMAGE_API": "0"}):
                with patch.object(V.requests, "post", side_effect=AssertionError("rede proibida")) as post:
                    mapping, report = V.preparar(ep, segmentos, Path(temp)/"imagens", Path(temp)/"render")
                    post.assert_not_called()
            self.assertEqual(len(mapping), 4)
            self.assertEqual(report["fallbacks"], 0)
            self.assertEqual(report["ready"], 4)
            self.assertTrue(all(s["status"] == "local_fallback" for s in report["scenes"]))
            for path in mapping.values():
                self.assertTrue((Path(temp)/"imagens"/path).exists())

if __name__ == "__main__":
    unittest.main()
