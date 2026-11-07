"""Piloto Manim: Nina original com cabelo preto como apresentadora de carros.

Executado no pipeline de teste, sem publicar. Dados e preço: demonstração.
"""
import json
import os
import sys
from pathlib import Path

import numpy as np
from manim import *

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/"motor"))
import nina_lib as NL

config.frame_width=8
config.frame_height=14.222
config.pixel_width=720
config.pixel_height=1280
config.frame_rate=24

# A mesma Nina do motor oficial, apenas cabelo e roupa recoloridos neste processo.
NL.RUIVO="#161820"
NL.RUIVO_ESC="#06080d"
NL.RUIVO_CL="#3c414c"
NL.BLUSA="#ab2346"

AZUL="#0c1d40"
AMARELO="#ffda50"
BRANCO="#fffdf8"
V={**json.loads((Path(__file__).parent/"veiculo_demo.json").read_text(encoding="utf-8"))}
P=Path(os.environ.get("PASTA_VENDEDORA", str(Path(__file__).parent/"saida")))
SEGS=json.loads((P/"segs.json").read_text(encoding="utf-8"))
LIP=json.loads((P/"lip.json").read_text(encoding="utf-8"))

def texto(s, tamanho=29, cor=BRANCO):
    return Text(str(s), font="DejaVu Sans", font_size=tamanho, weight=BOLD, color=cor)

def card(s, largura=6.9, altura=.76, fundo="#1c4179", tam=27, cor=BRANCO):
    bg=RoundedRectangle(corner_radius=.12,width=largura,height=altura,
                       stroke_color="#6c91ce",stroke_width=2,
                       fill_color=fundo,fill_opacity=1)
    tx=texto(s,tam,cor)
    if tx.width>largura-.3:
        tx.scale_to_fit_width(largura-.3)
    return VGroup(bg,tx.move_to(bg))

def carro():
    # Veículo vetorial de demonstração; no uso real, usar foto do automóvel anunciado.
    sombra=Ellipse(width=4.7,height=.28,fill_color="#070d23",fill_opacity=.8,stroke_width=0).shift(DOWN*.80)
    capota=Polygon([-1.38,.32,0],[-.75,1.13,0],[.88,1.13,0],[1.65,.32,0],
                  fill_color="#c6d6e8",fill_opacity=1,stroke_color=WHITE,stroke_width=3)
    base=RoundedRectangle(width=4.9,height=1.05,corner_radius=.22,
                          fill_color="#b6cbe3",fill_opacity=1,stroke_color=WHITE,stroke_width=3).shift(DOWN*.16)
    vidro=Polygon([-.99,.34,0],[-.55,.95,0],[.68,.95,0],[1.26,.34,0],
                  fill_color="#24466a",fill_opacity=1,stroke_width=0)
    rodas=VGroup(*[Circle(radius=.4,fill_color="#141a25",fill_opacity=1,
                          stroke_color="#d5d9e7",stroke_width=5).move_to([x,-.70,0]) for x in (-1.45,1.45)])
    return VGroup(sombra,capota,base,vidro,rodas)

def legenda(fala):
    linhas=[]; atual=""
    for palavra in fala.split():
        if len(atual)+len(palavra)+1>35 and atual:
            linhas.append(atual);atual=palavra
        else:
            atual=(atual+" "+palavra).strip()
    if atual:linhas.append(atual)
    frases=VGroup(*(texto(l,21) for l in linhas[:4])).arrange(DOWN,buff=.08)
    if frases.width>6.8:frases.scale_to_fit_width(6.8)
    fundo=RoundedRectangle(corner_radius=.15,width=7.2,height=1.56,
                           fill_color="#09162d",fill_opacity=.98,stroke_width=0)
    return VGroup(fundo,frases.move_to(fundo)).move_to([0,-6.02,0])

class VendedoraCarros(Scene):
    def construct(self):
        self.camera.background_color=AZUL
        self.add(card("PLANTÃO DOS SEMINOVOS",altura=.91,fundo="#cc2543",tam=32).move_to([0,6.49,0]))
        self.add(texto("NINA APRESENTA • SIMULAÇÃO",21,AMARELO).move_to([0,5.84,0]))
        fundo=RoundedRectangle(corner_radius=.24,width=7.24,height=4.18,
                               fill_color="#19396f",fill_opacity=1,
                               stroke_color="#6280b2",stroke_width=3).move_to([0,3.54,0])
        self.add(fundo)
        auto=carro().move_to([0,3.53,0])
        self.play(FadeIn(auto,shift=RIGHT*.35),run_time=.3)
        self.add(card(V["modelo"],altura=.67,tam=30).move_to([0,1.60,0]))
        self.add(texto("OFERTA FICTÍCIA • PILOTO",19,AMARELO).move_to([0,1.05,0]))

        # Figura é 100% vetor Manim do motor da Nina, NÃO foto animada.
        p=NL.nina("neutra","tarde")
        p["grupo"].remove(p["copo"])  # sem água de coco no estúdio de vendas
        p=NL.posicionar(p,escala=1.31,pos=np.array([-1.58,-2.20,0]))
        self.add(p["grupo"])
        NL.animar_nina(self,p,LIP)  # piscadas e sincronização da boca com Kokoro

        info=card("ANO • MOTOR • KM",largura=3.6,tam=23).move_to([1.92,-.53,0])
        preco=card("PREÇO EM DESTAQUE",largura=3.6,altura=.91,fundo=AMARELO,cor=AZUL,tam=23).move_to([1.92,-1.51,0])
        self.add(info,preco)
        self.add(card("NINA • VENDEDORA DE CARROS",altura=.63,fundo="#cc2543",tam=22).move_to([0,-4.80,0]))
        atual=None
        for s in SEGS:
            i=int(s["i"])
            leg=legenda(s["texto"])
            if atual is not None:self.remove(atual)
            self.add(leg);atual=leg
            if i==1:
                novo=card(f'{V["ano"]} • {V["motor"]}',largura=3.6,tam=22).move_to(info)
                self.play(Transform(info,novo),run_time=.24)
            if i==2:
                novo=card(V["km"]+" KM",largura=3.6,tam=25).move_to(info)
                self.play(Transform(info,novo),run_time=.24)
            if i==3:
                novo=card(V["preco"],largura=3.6,altura=.91,fundo=AMARELO,cor=AZUL,tam=30).move_to(preco)
                self.play(Transform(preco,novo),run_time=.25)
            # Braço se move como vetor articulado da personagem original.
            if i in (0,2,4):
                br=p["braco_esq"]
                self.play(Rotate(VGroup(br,p["mao_esq"]),angle=(-.15 if i%4==0 else .15),
                                 about_point=br.get_start(),run_time=.25))
            resto=float(s["fim"])-self.renderer.time
            if resto>.01:self.wait(resto)
        if atual is not None:self.remove(atual)
        self.play(FadeIn(card("PEÇA A FICHA REAL NA LOJA",tam=27,fundo="#cc2543").move_to([0,-6.0,0])),run_time=.23)
        self.wait(.7)
