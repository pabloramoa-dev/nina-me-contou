import unittest
from motor.ganchos import aplicar_gancho, VERSAO


class TestarGanchos(unittest.TestCase):
    def test_auto_parte1_usa_pista_real(self):
        fala = ["Ela só queria pegar um carregador. Encontrou uma segunda vida.",
                "A história chegou pela Carolina. Gabriel fazia parte da rotina dela havia 2 anos.",
                "Naquela terça, Carolina encontrou um comprovante de reserva que ninguém reconhecia.",
                "No começo ela tentou ignorar, porque ninguém lembrava de ter ouvido aquele nome antes.",
                "Mas havia um detalhe: a pista apontava para um condomínio novo.",
                "Carolina perguntou de forma casual se Gabriel conhecia aquele lugar. A resposta foi não.",
                "Na mesma noite, outra pista apareceu: uma segunda pista estava no histórico de viagens.",
                "Foi aí que Carolina ligou os pontos. Gabriel tinha aberto uma empresa com outra pessoa."]
        ep = {"id": "ep070-p1", "parte": 1, "gerado_automaticamente": True,
              "batidas": [{"fala": s, "expr": "ironica"} for s in fala],
              "legenda_post": fala[0] + "\n\nAviso de ficção."}
        r = aplicar_gancho(ep)
        self.assertIn("comprovante de reserva", r["batidas"][0]["fala"])
        self.assertIn("Gabriel negou", r["batidas"][0]["fala"])
        self.assertNotIn("carregador", r["batidas"][0]["fala"])
        self.assertEqual(r["gancho_versao"], VERSAO)
        self.assertEqual(r, aplicar_gancho(r))
        self.assertEqual(ep["batidas"][0]["fala"], fala[0])

    def test_auto_parte2_nao_comeca_com_recado(self):
        fala = ["Se você caiu aqui agora, volta na parte um. A pista principal está lá.",
                "Carolina esperou até as 17 horas e foi até um condomínio novo.",
                "Ela levou só a foto de um comprovante de reserva que ninguém reconhecia.",
                "Quando chegou, reconheceu o nome de Gustavo numa caixa de correspondência.",
                "Gustavo abriu a porta e falou.",
                "Em poucos minutos ficou claro que Gabriel tinha aberto uma empresa."]
        ep = {"id": "ep070-p2", "parte": 2, "gerado_automaticamente": True,
              "batidas": [{"fala": s} for s in fala]}
        r = aplicar_gancho(ep)
        self.assertTrue(r["batidas"][0]["fala"].startswith("Carolina encontrou"))
        self.assertEqual(len(r["batidas"]), len(fala))

    def test_parte2_editorial_preserva_sequencia(self):
        ep = {"parte": 2, "batidas": [
            {"fala": "Se você chegou agora, volta na parte um."},
            {"fala": "Na cozinha havia uma aliança no chão."},
            {"fala": "O marido tinha deixado a porta aberta."},
            {"fala": "Ela não entendeu o que aconteceu."},
            {"fala": "Uma carta estava sobre a mesa."}]}
        r = aplicar_gancho(ep)
        self.assertEqual(len(r["batidas"]), 4)
        self.assertEqual(r["batidas"][0]["fala"], "Na cozinha havia uma aliança no chão.")

    def test_preserva_abertura_existente(self):
        ep = {"parte": 1, "batidas": [{"fala": "Ela encontrou uma aliança no carro do marido."}]*6}
        self.assertEqual(aplicar_gancho(ep)["batidas"][0]["fala"], ep["batidas"][0]["fala"])

    def test_preserva_promo(self):
        ep = {"titulo": "Promo da Nina", "batidas": [{"fala": "Eu sou a Nina."}]*6}
        self.assertEqual(aplicar_gancho(ep), ep)


if __name__ == "__main__":
    unittest.main()
