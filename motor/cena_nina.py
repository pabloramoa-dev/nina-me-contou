"""Episódio da Nina v2.
Uso (feito pelo produzir.py):
  EPISODIO=episodios/ep001-p1.json PASTA=saida/ep001-p1 manim --fps 24 cena_nina.py Episodio
  EPISODIO=...  manim -s cena_nina.py Capa        (capa 1080x1920 do Reel)
"""
import os, sys, json
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from manim import *
import numpy as np
import dvh_vox_papel as V
import nina_lib as NL
import objetos as O

config.frame_width = 8.0
config.frame_height = 14.222
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_rate = 24

EP = json.load(open(os.environ.get("EPISODIO", os.path.join(AQUI, "..", "episodios", "ep001-p1.json")),
                    encoding="utf-8"))
PASTA = os.environ.get("PASTA", os.path.join(AQUI, "..", "saida", EP["id"]))

Y_ARTE = 4.0
Y_LEG = -5.55
AMARELO = "#ffd24a"


# ----------------------------------------------------------------------------- legenda
def _linhas(txt, larg=27):
    out, at = [], ""
    for w in txt.split():
        if len(at) + len(w) + 1 > larg and at:
            out.append(at); at = w
        else:
            at = (at + " " + w).strip()
    if at:
        out.append(at)
    if len(out) > 3:
        return _linhas(txt, larg + 6)
    return out


def legenda(txt, destaque=()):
    marcas = {}
    for d in destaque or ():
        if d and d in txt:
            marcas[d] = AMARELO
    linhas = VGroup(*[Text(l, font=V.FONTE, weight=BOLD, font_size=36, color=WHITE,
                           t2c={k: v for k, v in marcas.items() if k in l})
                      for l in _linhas(txt)]).arrange(DOWN, buff=0.12)
    if linhas.width > 7.0:
        linhas.scale(7.0 / linhas.width)
    band = Polygon(*V._contorno_rasgado(linhas.width + 0.7, linhas.height + 0.5, dente=0.03, semente=2),
                   fill_color=BLACK, fill_opacity=0.8, stroke_width=0)
    return VGroup(band, linhas.move_to(band)).move_to([0, Y_LEG, 0])


def selo_topo():
    t = Text(f"NINA CONTA · EP {EP['ep']:02d} · PARTE {EP['parte']}", font=V.FONTE, weight=BOLD,
             font_size=40, color="#111111").scale(0.62)
    fb = V.recorte(t.width + 0.4, t.height + 0.26, cor="recorte", semente=17, girar=-0.02)
    return VGroup(fb, t.move_to(fb)).move_to([0, 6.55, 0])


def montar_arte(arte):
    if not arte:
        return None
    tipo, arg = arte[0], (arte[1] if len(arte) > 1 else None)
    if tipo == "titulo":
        m = O.titulo(arg or EP["titulo"], None, EP["parte"])
    else:
        m = O.arte(tipo, arg)
    if m.width > 6.8:
        m.scale(6.8 / m.width)
    if m.height > 3.2:
        m.scale(3.2 / m.height)
    return m.move_to([0, Y_ARTE, 0])


# ----------------------------------------------------------------------------- cena
class Episodio(MovingCameraScene):
    def construct(self):
        V.estilo("papel")
        segs = json.load(open(os.path.join(PASTA, "segs.json"), encoding="utf-8"))
        cues = json.load(open(os.path.join(PASTA, "lip.json"), encoding="utf-8"))
        bat = EP["batidas"]

        self.add(NL.varanda(EP["cenario"])["grupo"])
        p = NL.posicionar(NL.nina(bat[0].get("expr", "neutra"), EP["cenario"]))
        V.colar(self, p, espessura=22)
        NL.animar_nina(self, p, cues)
        V.fixar_legenda(self, topo := selo_topo())
        self.add(topo)

        fr = self.camera.frame
        normal = fr.copy()
        zoom_on = False
        arte_at = leg_at = None

        for s in segs:
            b = bat[s["i"]]
            fim = s["fim"]
            # 1. expressão
            NL.trocar_expressao(self, p, b.get("expr", p["expr"]))
            # 2. câmera (punch-in no rosto nas revelações)
            quer_zoom = bool(b.get("zoom"))
            if quer_zoom != zoom_on:
                if quer_zoom:
                    alvo = fr.copy().set(width=config.frame_width / 1.45).move_to(
                        p["cab"].get_center() + DOWN * 0.9)
                else:
                    alvo = normal
                self.play(fr.animate.become(alvo), run_time=0.35,
                          rate_func=V.degraus(smooth, 12, 0.35))
                zoom_on = quer_zoom
            # 3. legenda
            nova_leg = V.fixar_legenda(self, legenda(b.get("tela", b["fala"]), b.get("destaque")))
            if leg_at is not None:
                self.remove(leg_at)
            self.add(nova_leg)
            leg_at = nova_leg
            # 4. arte do topo
            nova = None if zoom_on else montar_arte(b.get("arte"))
            if arte_at is not None and nova is not None or (arte_at is not None and zoom_on):
                self.play(FadeOut(arte_at, run_time=0.15))
                arte_at = None
            if nova is not None:
                V.colar_entrada(self, nova, girar=0.16, dur=0.4)
                arte_at = nova
            # 5. espera até o fim da fala
            resto = fim - self.renderer.time
            if resto > 0.02:
                self.wait(resto)

        # fecho: cartão final por 1.6s (áudio é completado com silêncio no mux)
        if zoom_on:
            self.play(fr.animate.become(normal), run_time=0.3)
        if arte_at is not None:
            self.play(FadeOut(arte_at, run_time=0.15))
        if leg_at is not None:
            self.remove(leg_at)
        fim_txt = EP.get("fim", "SEGUE A NINA")
        cor = "vermelho" if EP["parte"] == 1 else "amarelo"
        card = V.manchete(fim_txt, cor_papel=cor, cor_texto="#fbf8f0" if cor == "vermelho" else None, tam=52)
        if card.width > 7.2:
            card.scale(7.2 / card.width)
        card.move_to([0, Y_ARTE, 0])
        NL.trocar_expressao(self, p, "ironica")
        V.colar_entrada(self, card, girar=0.2, dur=0.45)
        self.wait(1.4)


class Capa(Scene):
    """Capa do Reel: o que o Instagram mostra na grade é o QUADRADO DO MEIO,
    por isso título e selo ficam no centro vertical."""
    def construct(self):
        V.estilo("papel")
        self.add(NL.varanda(EP["cenario"])["grupo"])
        expr = "desconfiada" if EP["parte"] == 1 else "chocada"
        p = NL.posicionar(NL.nina(expr, EP["cenario"]), escala=1.9, pos=np.array([0.1, -3.6, 0]))
        V.colar(self, p, espessura=22)
        sel = O.titulo(EP["titulo"], EP["ep"], EP["parte"])
        if sel.width > 7.3:
            sel.scale(7.3 / sel.width)
        self.add(sel.move_to([0, 2.2, 0]))
