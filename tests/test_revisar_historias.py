"""Testes de clareza para o banco de histórias da Nina."""
import copy
import unittest
from motor.revisar_historias import VERSAO, revisar

class RevisarHistoriasTest(unittest.TestCase):
    def test_remove_enchimento_e_preserva_desfecho(self):
        fatos = [
            "Ana recebeu uma foto do marido em outra cidade. Mas ele disse que estava trabalhando perto de casa.",
            "Ana conhecia Paulo havia seis anos. Os dois moravam juntos.",
            "A protagonista desta história é Ana. E o que aconteceu depois não tem nada de conto de fadas.",
            "A foto foi tirada na praça central.",
            "O detalhe parecia pequeno à primeira vista. Só que a explicação mudou.",
            "Ela perguntou a Paulo sobre a viagem.",
            "Ele disse que nunca saiu da cidade.",
            "Até aquele momento, cada pessoa enxergava só um pedaço do que aconteceu.",
            "Ana mostrou a ele a fotografia.",
            "Paulo admitiu que tinha viajado sem avisar.",
            "Ana pediu um tempo para pensar.",
            "O casal conversou com calma.",
            "Ana decidiu se separar.",
            "No fim, a conversa trouxe consequências reais. As pessoas precisaram assumir suas escolhas.",
            "Se fosse com você, teria reagido como Ana ou feito diferente? Me conta nos comentários.",
        ]
        ep = {"id": "ep124", "parte": "unica", "batidas": [
            {"fala": f, "arte": ["foto"]} for f in fatos]}
        original = copy.deepcopy(ep)
        revisado, rel = revisar(ep)
        self.assertEqual(rel["status"], "revisado")
        textos = [b["fala"] for b in revisado["batidas"]]
        self.assertEqual(ep, original)
        self.assertGreaterEqual(len(textos), 10)
        self.assertIn("Ana decidiu se separar.", textos)
        self.assertFalse(any(x.startswith("No fim, a conversa trouxe") for x in textos))
        self.assertTrue(textos[-1].startswith("E você"))
        self.assertEqual(revisado["revisao_clareza"], VERSAO)
        self.assertEqual(revisar(revisado)[0], revisado)

    def test_preserva_boa_historia(self):
        ep = {"id": "ep186", "parte": "unica", "batidas": [
            {"fala": "Cena concreta " + str(i)} for i in range(10)]}
        novo, status = revisar(ep)
        self.assertEqual(ep, novo)
        self.assertEqual(status["status"], "sem_mudancas")

    def test_preserva_historico_em_partes(self):
        ep = {"id": "ep081-p1", "parte": 1, "batidas": []}
        self.assertEqual(revisar(ep)[0], ep)

    def test_bloqueia_corte_sem_dez_cenas(self):
        ep = {"id": "ep181", "parte": "unica", "batidas": [
            {"fala": "A protagonista desta história é Maria."} for _ in range(15)]}
        novo, status = revisar(ep)
        self.assertEqual(status["status"], "revisao_manual")
        self.assertEqual(ep, novo)
if __name__ == "__main__":
    unittest.main()
