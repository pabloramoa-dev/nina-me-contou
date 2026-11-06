"""Testes locais da migração para histórias únicas (sem API ou vídeo)."""
import json
import tempfile
import unittest
from pathlib import Path

from motor.episodio_unico import consolidar, converter_pendentes, RX_PARTE


def roteiro(n, parte, falas):
    return {
        "id": f"ep{n:03d}-p{parte}", "ep": n, "parte": parte,
        "titulo": "A CARTA SURPRESA", "temporada": "Ficção",
        "cenario": "tarde",
        "batidas": [{"fala": fala, "expr": "neutra", "arte": ["foto"]}
                   for fala in falas],
    }


class EpisodioUnicoTest(unittest.TestCase):
    def setUp(self):
        self.p1 = roteiro(112, 1, [
            "Uma carta apareceu na casa de Ana num domingo de manhã.",
            "Ana encontrou um endereço e resolveu perguntar de onde tinha vindo.",
            "A irmã contou que reconhecia a letra e pediu um dia para explicar.",
            "Na parte dois eu conto toda a explicação.",
        ])
        self.p2 = roteiro(112, 2, [
            "Na primeira parte Ana encontrou uma pista que não fazia sentido.",
            "Ana voltou a falar com a irmã e escutou o que tinha acontecido.",
            "A carta fora escrita pela avó antes de uma viagem e estava guardada por engano.",
            "Ana decidiu guardar a carta no álbum, e as duas finalmente esclareceram o mal-entendido.",
            "Você teria feito a mesma escolha? Conta nos comentários.",
        ])

    def test_historia_unica_com_final(self):
        ep = consolidar(self.p1, self.p2, alvo_palavras=100)
        self.assertEqual(ep["id"], "ep112")
        self.assertEqual(ep["parte"], "unica")
        self.assertEqual(ep["fim"], "HISTÓRIA COMPLETA")
        narracao = " ".join(b["fala"] for b in ep["batidas"])
        self.assertFalse(RX_PARTE.search(narracao))
        self.assertIn("guardada por engano", narracao)
        self.assertIn("esclareceram o mal-entendido", narracao)
        self.assertNotIn("parte 2", ep["legenda_post"].lower())

    def test_nao_republica_pares_antigos(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "ep112-p1.json").write_text(json.dumps(self.p1), encoding="utf-8")
            (base / "ep112-p2.json").write_text(json.dumps(self.p2), encoding="utf-8")
            self.assertEqual(converter_pendentes(base, {"ep112-p1"}), [])
            self.assertFalse((base / "ep112.json").exists())

    def test_converte_pares_ineditos_sem_apagar_fonte(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            for nome, ep in (("ep112-p1.json", self.p1), ("ep112-p2.json", self.p2)):
                (base / nome).write_text(json.dumps(ep), encoding="utf-8")
            self.assertEqual(converter_pendentes(base, set()), ["ep112"])
            self.assertTrue((base / "ep112-p1.json").exists())
            self.assertTrue((base / "ep112-p2.json").exists())
            self.assertEqual(converter_pendentes(base, set()), [])
            ep = json.loads((base / "ep112.json").read_text(encoding="utf-8"))
            self.assertEqual(ep["parte"], "unica")

    def test_roteiro_curto_nao_ganha_enchimento_generico(self):
        ep = consolidar(self.p1, self.p2)
        narracao = " ".join(b["fala"] for b in ep["batidas"])
        self.assertNotIn("O curioso é como os detalhes", narracao)
        self.assertIn("guardada por engano", narracao)
        self.assertIn("esclareceram o mal-entendido", narracao)


if __name__ == "__main__":
    unittest.main()
