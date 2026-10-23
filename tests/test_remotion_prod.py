"""Checagens baratas do acabamento da Nina (sem requerer GPU/navegador)."""
import unittest
from motor.remotion_final import montar_props

class RemotionNinaTest(unittest.TestCase):
    def test_segmentos_reais_e_cta(self):
        ep={"batidas":[
            {"fala":"Uma descoberta surpreendente.","tela":"A DESCOBERTA","expr":"chocada"},
            {"fala":"Segue a Nina.","arte":["seguir","SIGA A NINA"]}
        ]}
        segs=[{"i":0,"ini":0,"fim":4.0},{"i":1,"ini":4.0,"fim":6.0}]
        result=montar_props(ep,segs,8.2)
        self.assertEqual(result["durationFrames"],246)
        self.assertEqual(result["scenes"][0]["start"],0)
        self.assertEqual(result["scenes"][1]["title"],"SIGA A NINA")
    def test_divergencia_bloqueia_publicacao(self):
        with self.assertRaises(ValueError):
            montar_props({"batidas":[{"fala":"A"}]},[],3)
if __name__=="__main__":
    unittest.main()
