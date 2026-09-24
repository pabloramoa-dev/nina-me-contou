"""Foto de perfil 1080x1080: rosto centralizado, folga para o corte circular."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from manim import *
import numpy as np
import nina_lib as NL, dvh_vox_papel as V
config.frame_width = 8.0; config.frame_height = 8.0
config.pixel_width = 1080; config.pixel_height = 1080
class Perfil(Scene):
    def construct(self):
        V.estilo("papel")
        cen = NL.varanda("tarde")["grupo"]
        cen.scale(1.0).move_to([0, -1.2, 0])
        self.add(cen)
        p = NL.nina("ironica", "tarde")
        p["grupo"].scale(1.95)
        p["grupo"].shift(-p["cab"].get_center() + np.array([0, 0.15, 0]))
        V.colar(self, p, espessura=24)
