"""Testes rápidos, CPU, sem Manim/Meta e sem publicação."""
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from tools import carrossel_diario as car


class TestCarrosselDiario(unittest.TestCase):
    def test_piloto_de_sete_paginas_com_reviravolta(self):
        paginas=car.historia(date(2026,10,23))
        self.assertEqual(len(paginas),7)
        self.assertIn("bolos",paginas[5]["texto"])
        self.assertEqual([p["numero"] for p in paginas],list(range(1,8)))

    def test_dias_seguidos_tem_texto_diferente(self):
        dia1=car.historia(date(2026,10,24))
        dia2=car.historia(date(2026,10,25))
        self.assertEqual(len(dia1),7)
        self.assertEqual(len(dia2),7)
        self.assertNotEqual([x["texto"] for x in dia1],[x["texto"] for x in dia2])

    def test_sete_imagens_sem_rede(self):
        with tempfile.TemporaryDirectory() as tmp:
            pasta=Path(tmp)
            avatar=pasta/"nina.png"
            Image.new("RGB",(400,400),"#e5c89b").save(avatar)
            with patch("motor.local_story_art.icon",return_value=Image.new("RGBA",(600,600),"#e77989")):
                car.preparar(date(2026,10,23),avatar,pasta/"cards")
            slides=sorted((pasta/"cards").glob("*.jpg"))
            self.assertEqual(len(slides),7)
            with Image.open(slides[0]) as im:self.assertEqual(im.size,(1080,1350))
            self.assertIn("História de ficção",(pasta/"cards"/"conteudo.json").read_text("utf-8"))


if __name__=="__main__":
    unittest.main()
