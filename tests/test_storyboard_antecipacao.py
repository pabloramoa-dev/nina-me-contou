"""Regras de antecipação e storyboard sem chamar nenhuma API de verdade."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from motor.antecipacao import antecipar, VERSAO as HOOK_VERSION
from motor import storyboard_prompts as S
from motor import visual_images as V
from motor.siliconflow_policy import validar_metadados, SiliconFlowObrigatoria


FALAS = [
    "Malu preparou uma festa surpresa para o namorado. ",
    "Às oito, chegaram duas mulheres com bolos diferentes na mesma mesa.",
    "Ela encontrou uma segunda reserva feita para a mesma noite.",
    "Renata entrou no restaurante carregando balões dourados e um presente.",
    "Malu pegou o celular e abriu uma foto do apartamento de Ícaro.",
    "As duas olharam para o sofá cinza e reconheceram o mesmo lugar.",
    "Ícaro entrou na sala e ficou parado diante das duas mulheres.",
    "Renata mostrou as mensagens antigas no celular e pediu explicações.",
    "Malu conversou com Renata longe dos convidados e tomou uma decisão.",
    "As duas dividiram o bolo na mesa e Ícaro foi embora sem apagar as velas.",
]


def episodio():
    return {"id": "ep991", "parte": "unica", "titulo": "Duas festas",
            "batidas": [{"fala": texto, "expr": "neutra"} for texto in FALAS]}


def cenas():
    return [{"scene": i, "text": fala, "beats": [i],
             "start": i * 6, "end": (i + 1) * 6} for i, fala in enumerate(FALAS)]


def plano_ok(ep, lista, model):
    return {
        "personagens": ("Malu: mulher adulta de cabelo preto cacheado e roupa azul. "
                       "Renata: mulher adulta de cabelo castanho curto e blusa coral. "
                       "Ícaro: homem adulto de camisa verde. O restaurante tem mesas de madeira."),
        "cenas": [
            {"index": s["scene"],
             "ancora": " ".join(s["text"].split()[:4]),
             "visual": ("Plano médio cinematográfico no restaurante, com expressão "
                        "emocional e ação concreta: " + " ".join(s["text"].split()[:4]) +
                        ". Roupas e cenário coerentes com a ficha de personagens.")}
            for s in lista
        ]
    }


class TestarAntecipacao(unittest.TestCase):
    def test_gera_pergunta_com_pista_real_antes_da_voz(self):
        ep = episodio()
        feito = antecipar(ep)
        self.assertEqual(feito["gancho_antecipacao_versao"], HOOK_VERSION)
        self.assertIn("segunda reserva", feito["batidas"][0]["fala"].lower())
        self.assertIn("?", feito["batidas"][0]["fala"])
        self.assertEqual(ep["batidas"][0]["fala"], FALAS[0])
        self.assertEqual([b["fala"] for b in feito["batidas"][1:]], FALAS[1:])
        self.assertEqual(antecipar(feito), feito)

    def test_ja_tem_virada_preserva_sem_revelar_final(self):
        ep = episodio()
        ep["batidas"][0]["fala"] = ("Malu planejou uma festa surpresa para o namorado. "
                                     "Mas quando uma segunda convidada entrou com outro bolo, "
                                     "ninguém compreendeu o que estava acontecendo.")
        feito = antecipar(ep)
        self.assertEqual(feito["batidas"][0]["fala"], ep["batidas"][0]["fala"])
        self.assertEqual(feito["gancho_antecipacao_modelo"], "antecipacao_existente_validada")

    def test_nao_altera_promo_ou_episodio_em_partes(self):
        ep = episodio()
        ep["titulo"] = "Promo da Nina"
        self.assertEqual(antecipar(ep), ep)
        ep = episodio()
        ep["parte"] = 2
        self.assertEqual(antecipar(ep), ep)


class TestarStoryboard(unittest.TestCase):
    def test_cta_nao_vira_a_decima_ilustracao(self):
        ep = episodio()
        ep["batidas"].append({"fala": "Me segue para ouvir mais histórias.",
                              "arte": ["seguir"]})
        segs = [{"ini":i*6,"fim":(i+1)*6} for i in range(11)]
        shots = V.planejar(ep, segs)
        self.assertEqual(len(shots), 10)
        self.assertEqual(shots[-1]["beats"], [9, 10])

    def test_chave_disponivel_nao_gera_custo_sem_optin(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {
            "OPENAI_API_KEY": "chave-ficticia",
            "NINA_REQUIRE_AI_STORYBOARD": "0",
            "NINA_USE_AI_STORYBOARD": "0",
        }):
            with patch.object(S.requests, "post",
                              side_effect=AssertionError("rede inesperada")) as request:
                _, report = S.preparar(episodio(), cenas(), Path(tmp),
                                       V.STYLE, strict=False)
                request.assert_not_called()
                self.assertEqual(report["modo"], "roteiro_local")

    def test_dez_prompts_compostos_antes_de_ilustrar(self):
        ep, scenes = episodio(), cenas()
        with tempfile.TemporaryDirectory() as tmp:
            planned, report = S.preparar(ep, scenes, Path(tmp), V.STYLE,
                                         planner=plano_ok, strict=True)
            self.assertEqual(report["modo"], "siliconflow_roteiro")
            self.assertEqual(report["cenas"], 10)
            self.assertTrue((Path(tmp) / "prompts_planejados.json").exists())
            for i, scene in enumerate(planned):
                self.assertIn("PERSONAGENS", scene["prompt"])
                self.assertIn("CENA ATUAL " + str(i + 1) + "/10", scene["prompt"])
                self.assertIn("".join(scene["text"].split()[:1]), scene["prompt"])

    def test_usa_cache_sem_nova_chamada_ao_modelo(self):
        ep = episodio()
        with tempfile.TemporaryDirectory() as tmp:
            S.preparar(ep, cenas(), Path(tmp), V.STYLE, planner=plano_ok, strict=True)
            def erro(*args):
                raise AssertionError("não deve chamar modelo de texto")
            planned, report = S.preparar(ep, cenas(), Path(tmp), V.STYLE,
                                         planner=erro, strict=True)
            self.assertEqual(len(planned), 10)
            self.assertEqual(report["modo"], "siliconflow_roteiro")

    def test_mesma_chave_siliconflow_gera_os_prompts_sem_openai(self):
        ep = episodio()
        approved = plano_ok(ep, cenas(), "Qwen/Qwen3-30B-A3B-Instruct-2507")

        class Retorno:
            status_code = 200

            def raise_for_status(self):
                return None

            def json(self):
                return {"choices": [{"message": {
                    "content": json.dumps(approved, ensure_ascii=False)
                }}]}

        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {
            "OPENAI_API_KEY": "",
            "SILICONFLOW_API_KEY": "chave-siliconflow-de-teste",
            "NINA_STORYBOARD_PROVIDER": "siliconflow",
            "NINA_REQUIRE_AI_STORYBOARD": "1",
            "NINA_STORYBOARD_MODEL": "Qwen/Qwen3-30B-A3B-Instruct-2507",
        }):
            with patch.object(S.requests, "post", return_value=Retorno()) as fake:
                scenes, report = S.preparar(ep, cenas(), Path(tmp), V.STYLE, strict=True)
                self.assertEqual(report["modo"], "siliconflow_roteiro")
                self.assertEqual(report["provedor"], "siliconflow")
                self.assertEqual(len(scenes), 10)
                self.assertEqual(fake.call_count, 1)
                args, kwargs = fake.call_args
                self.assertEqual(args[0], "https://api.siliconflow.com/v1/chat/completions")
                self.assertEqual(kwargs["json"]["response_format"], {"type": "json_object"})
                self.assertEqual(kwargs["json"]["model"], "Qwen/Qwen3-30B-A3B-Instruct-2507")

    def test_bloqueia_prompts_desconectados_antes_de_cobrar_siliconflow(self):
        def inventar(ep, scenes, model):
            plano = plano_ok(ep, scenes, model)
            plano["cenas"][4]["ancora"] = "segredo inventado em outro bairro"
            return plano
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(S.StoryboardError):
                S.preparar(episodio(), cenas(), Path(tmp), V.STYLE,
                           planner=inventar, strict=True)
            self.assertFalse((Path(tmp) / "prompts_planejados.json").exists())

    def test_ausencia_da_chave_abortada_sem_chamada_siliconflow(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(
            os.environ, {"OPENAI_API_KEY": "", "SILICONFLOW_API_KEY": "",
                         "NINA_STORYBOARD_PROVIDER": "siliconflow",
                         "NINA_REQUIRE_AI_STORYBOARD": "1",
                         "NINA_ALLOW_PAID_IMAGE_API": "1"}, clear=False
        ):
            with patch.object(V, "gerar", side_effect=AssertionError("SiliconFlow não pode ser chamada")) as generate:
                with self.assertRaises(S.StoryboardError):
                    V.preparar(episodio(), [{"ini":i*6,"fim":(i+1)*6}
                                            for i in range(10)],
                              Path(tmp)/"assets", Path(tmp))
                generate.assert_not_called()

    def test_antes_da_imagem_prepara_dez_prompts_validados(self):
        ep = episodio()
        seq = [{"ini": i * 6, "fim": (i+1)*6} for i in range(10)]
        with tempfile.TemporaryDirectory() as tmp, patch.dict(
            os.environ, {"NINA_REQUIRE_AI_STORYBOARD":"1"}, clear=False
        ):
            with patch.object(S, "_pedir_plano", side_effect=plano_ok) as plan:
                with patch.object(V, "gerar", side_effect=V.ImageFailure("paid_image_api_disabled")) as gen:
                    V.preparar(ep, seq, Path(tmp)/"assets", Path(tmp))
                    self.assertEqual(plan.call_count, 1)
                    self.assertEqual(gen.call_count, 10)
                    for args in gen.call_args_list:
                        self.assertIn("PERSONAGENS", args.args[0])

    def test_metadados_precisam_do_storyboard_e_gancho(self):
        meta = {"motor": "remotion", "visual_images_requested": 10,
                "visual_images_ready": 10, "visual_images_fallbacks": 0,
                "siliconflow_confirmado": True, "siliconflow_provedor": "siliconflow",
                "siliconflow_ilustracoes": 10, "siliconflow_quadros": 20,
                "siliconflow_quadros_locais": 0}
        with self.assertRaises(SiliconFlowObrigatoria):
            validar_metadados(meta)
        meta.update(storyboard_mode="siliconflow_roteiro", storyboard_scenes=10,
                    gancho_antecipacao_versao=HOOK_VERSION)
        validar_metadados(meta)


if __name__ == "__main__":
    unittest.main()
