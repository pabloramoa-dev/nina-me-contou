"""Testes do estilo cinema 2D: custos, contexto, temporizacao e assets aprovados."""
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from motor import cinematic_story_art as C
from motor.remotion_final import montar_props
from motor import visual_images as V


class NinaCinema2D(unittest.TestCase):
    def setUp(self):
        self.ep={
            "id":"nina-cinema-unit", "titulo":"O SEGREDO DA FOTO",
            "batidas":[
                {"fala":"Uma mulher encontrou uma foto antiga no celular."},
                {"fala":"Ela viu um bilhete escondido na bolsa do marido."},
                {"fala":"No jantar os dois conversaram sobre o segredo."},
            ],
        }
        self.segs=[
            {"i":0,"ini":0,"fim":8,"fim_fala":7.8},
            {"i":1,"ini":8,"fim":15,"fim_fala":14.8},
            {"i":2,"ini":15,"fim":23,"fim_fala":22.8},
        ]

    def test_arte_e_motivacao_dependem_da_fala(self):
        self.assertEqual(C.tema({"text":"Ela ampliou a FOTO no celular"},self.ep),"photo")
        self.assertEqual(C.tema({"text":"Chegou uma carta"},self.ep),"letter")
        self.assertEqual(C.tema({"text":"Ela pegou uma aliança"},self.ep),"ring")
        self.assertEqual(C.tema({"text":"Uma conversa difícil"}, {"titulo":"Segredos"}),"people")
        sample=C.render({"scene":0,"text":"Uma foto reveladora"},self.ep)
        im=Image.open(io.BytesIO(sample))
        self.assertEqual(im.size,(1440,900))
        self.assertEqual(im.format,"PNG")

    def test_quadros_de_sete_em_sete(self):
        frames=C.planejar_quadros(self.ep,self.segs,23)
        self.assertEqual([f["start"] for f in frames],[0,7,14,21])
        self.assertEqual(frames[-1]["end"],23)
        self.assertEqual([f["beat"] for f in frames],[0,0,1,2])
        with tempfile.TemporaryDirectory() as folder:
            vis=C.preparar_quadros(self.ep,self.segs,23,folder)
            self.assertEqual(len(vis),4)
            self.assertEqual(vis[0]["src"],"nina-cinema/frame-000.png")
            self.assertTrue((Path(folder)/vis[0]["src"]).is_file())
            self.assertNotEqual((Path(folder)/vis[0]["src"]).read_bytes(),
                                (Path(folder)/vis[1]["src"]).read_bytes())
            props=montar_props(self.ep,self.segs,23,visual_frames=vis)
            self.assertEqual(props["durationFrames"],690)
            self.assertEqual(len(props["visuals"]),4)

    def test_arte_explicitamente_aprovada_tem_prioridade(self):
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder)/"assets"
            base.mkdir()
            image=Image.new("RGB",(500,300),"orange")
            image.save(base/"visual-scene-00.png")
            manifest={"scenes":[{"status":"approved_asset","start":0,"end":15,
                                  "asset":"visual-scene-00.png"}]}
            out=C.preparar_quadros(self.ep,self.segs,23,Path(folder)/"public",
                                   base_assets=base,visual_report=manifest)
            self.assertEqual(out[0]["origin"],"approved")
            self.assertEqual(out[1]["origin"],"approved")
            self.assertEqual(out[2]["origin"],"approved")
            self.assertEqual(out[3]["origin"],"cinematic_cpu")

    def test_imagens_api_substituem_quadros_cpu_no_painel_superior(self):
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder)/"assets"
            base.mkdir()
            Image.new("RGB",(768,512),"orange").save(base/"visual-scene-00.png")
            Image.new("RGB",(768,512),"skyblue").save(base/"visual-scene-01.png")
            manifest={"scenes":[
                {"status":"generated","start":0,"end":15,"asset":"visual-scene-00.png"},
                {"status":"cache","start":15,"end":23,"asset":"visual-scene-01.png"},
            ]}
            out=C.preparar_quadros(self.ep,self.segs,23,Path(folder)/"public",
                                   base_assets=base,visual_report=manifest)
            self.assertEqual([x["origin"] for x in out], ["generated","generated","generated","cache"])
            self.assertEqual(Image.open(Path(folder)/"public"/out[0]["src"]).getpixel((50,50)),
                             (255,165,0))
            self.assertEqual(Image.open(Path(folder)/"public"/out[3]["src"]).getpixel((50,50)),
                             (135,206,235))

    def test_fallback_grafico_gratuito_sem_rede(self):
        import os
        with tempfile.TemporaryDirectory() as folder:
            with patch.dict(os.environ, {"NINA_STORY_STYLE":"cinematic_2d",
                                          "NINA_ALLOW_PAID_IMAGE_API":"0"}):
                with patch.object(V.requests,"post",side_effect=AssertionError("rede proibida")) as req:
                    images,report=V.preparar(self.ep,self.segs,Path(folder)/"assets",Path(folder)/"out")
                    req.assert_not_called()
                self.assertEqual(report["ready"],3)
                self.assertTrue(all(s.get("image_origin")=="cinematic_2d_cpu"
                                    for s in report["scenes"]))
                self.assertEqual(len(images),3)

    def test_estilo_antigo_e_conservado(self):
        import os
        scene={"scene":0,"text":"Um bilhete"}
        with patch.dict(os.environ,{"NINA_STORY_STYLE":"classic","NINA_ALLOW_PAID_IMAGE_API":"0"}):
            with tempfile.TemporaryDirectory() as folder:
                ep={"titulo":"Um bilhete","batidas":[{"fala":"uma carta"}]*4}
                seg=[{"ini":i*2,"fim":i*2+2} for i in range(4)]
                images,report=V.preparar(ep,seg,Path(folder)/"assets",Path(folder)/"out")
                self.assertEqual(report["ready"],4)
                self.assertTrue(all(s.get("image_origin")=="pillow_illustration"
                                    for s in report["scenes"]))


if __name__=="__main__":
    unittest.main()
