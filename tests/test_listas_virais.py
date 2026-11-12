"""Testes sem rede para listas rápidas (não publicam e não renderizam)."""
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from motor.listas_virais import FORMATO, TEMAS, roteiro, abastecer


class ListasViraisTest(unittest.TestCase):
    def test_slots_tem_ids_distintos_e_tres_sinais(self):
        d = date(2026, 11, 12)
        a, b = roteiro(d, 12), roteiro(d, 15)
        self.assertNotEqual(a["id"], b["id"])
        self.assertEqual(a["formato"], FORMATO)
        self.assertEqual(b["formato"], FORMATO)
        for ep in (a, b):
            self.assertEqual(len(ep["batidas"]), 10)
            self.assertEqual(ep["parte"], "unica")
            self.assertTrue(ep["batidas"][0]["fala"].startswith("Três sinais"))
            self.assertIn("não provas", ep["legenda_post"])
            palavras = sum(len(b["fala"].split()) for b in ep["batidas"])
            self.assertGreater(palavras, 25)
            self.assertLess(palavras, 95)

    def test_temas_nao_repetem_no_periodo_de_reserva(self):
        inicio = date(2026, 11, 12)
        titulos = [roteiro(inicio + timedelta(days=i), hora)["titulo"]
                   for i in range(10) for hora in (12, 15)]
        self.assertGreaterEqual(len(TEMAS), 30)
        self.assertEqual(len(set(titulos)), len(titulos))

    def test_abastecer_idempotente_sem_sobrescrever(self):
        with tempfile.TemporaryDirectory() as temp:
            pasta = Path(temp)
            hoje = date(2026, 11, 12)
            ids = abastecer(2, hoje=hoje, pasta=pasta)
            self.assertEqual(len(ids), 4)
            arq = pasta / (ids[0] + ".json")
            conteudo = arq.read_text(encoding="utf-8")
            self.assertEqual(abastecer(2, hoje=hoje, pasta=pasta), [])
            self.assertEqual(arq.read_text(encoding="utf-8"), conteudo)

    def test_slot_invalido_nao_e_permitido(self):
        with self.assertRaises(ValueError):
            roteiro(date(2026, 11, 12), 9)


if __name__ == "__main__":
    unittest.main()
