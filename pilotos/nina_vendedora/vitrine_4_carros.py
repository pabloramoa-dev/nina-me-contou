"""Plantão de 4 carros: A Vendedora, personagem Manim original com voz Kokoro.

Este vídeo-base usa um painel fotográfico que recebe localmente as quatro
imagens reais enviadas pelo anunciante após a renderização no GitHub.
Não usa fotos como personagem e não inventa preço nem quilometragem.
"""
import json
import os
import sys
from pathlib import Path
import numpy as np
from manim import *

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "motor"))
import nina_lib as NL

config.frame_width=8
config.frame_height=14.222
config.pixel_width=720
config.pixel_height=1280
config.frame_rate=24

NL.RUIVO="#161923"
NL.RUIVO_ESC="#333a48"
NL.RUIVO_CL="#424958"
NL.BLUSA="#ca374e"

CLARO="#edf4fa"
AZUL="#173153"
TINTA="#19304a"
AMARELO="#f5c94b"
CARMIM="#c7374b"
BRANCO="#ffffff"
P=Path(os.environ.get("PASTA_VENDEDORA","out"))
SEGS=json.loads((P/"segs.json").read_text(encoding="utf-8"))
LIP=json.loads((P/"lip.json").read_text(encoding="utf-8"))
NOMES=["REN. KWID BRANCO","REN. KWID BRANCO","JEEP COMPASS PRETO",
       "HONDA HR-V VINHO","CHEVROLET TRACKER","QUATRO CARROS • UMA VITRINE"]

def txt(s,size=25,color=TINTA):
    return Text(s,font="DejaVu Sans",weight=BOLD,font_size=size,color=color)

def selo(t,w=3.48,h=.68,cor=BRANCO,letra=TINTA,size=20,borda="#c2d1df"):
    r=RoundedRectangle(width=w,height=h,corner_radius=.13,stroke_color=borda,
                       stroke_width=2,fill_color=cor,fill_opacity=1)
    s=txt(t,size,letra)
    if s.width>w-.25:s.scale_to_fit_width(w-.25)
    return VGroup(r,s.move_to(r))

def legend(t):
    palavras=t.split();linhas=[];cur=""
    for p in palavras:
        if len(cur)+len(p)+1>38 and cur:
            linhas.append(cur);cur=p
        else:cur=(cur+" "+p).strip()
    if cur:linhas.append(cur)
    texto=VGroup(*[txt(q,20,BRANCO) for q in linhas[:4]]).arrange(DOWN,buff=.055)
    if texto.width>7.0:texto.scale_to_fit_width(7.0)
    fundo=RoundedRectangle(width=7.55,height=1.42,corner_radius=.17,
                            fill_color="#112742",fill_opacity=.98,stroke_width=0)
    return VGroup(fundo,texto.move_to(fundo)).move_to([0,-6.23,0])

class Vitrine4Carros(Scene):
    def construct(self):
        self.camera.background_color=CLARO
        palco=Rectangle(width=8.2,height=6.4,fill_color="#e3eff7",
                          fill_opacity=1,stroke_width=0).move_to([0,-2.12,0])
        halo=Ellipse(width=4.65,height=5.7,stroke_width=0,
                     fill_color="#fffdf7",fill_opacity=.91).move_to([-1.82,-2.20,0])
        self.add(palco,halo)
        head=Rectangle(width=8.2,height=.95,fill_color="#112a4a",
                       fill_opacity=1,stroke_width=0).move_to([0,6.62,0])
        self.add(head,txt("PLANTÃO DOS SEMINOVOS",30,BRANCO).move_to([0,6.64,0]))
        self.add(txt("A VENDEDORA APRESENTA",21,AZUL).move_to([0,5.83,0]))
        tela=RoundedRectangle(width=7.42,height=4.16,corner_radius=.22,
                              fill_color=BRANCO,fill_opacity=1,
                              stroke_color="#bdcfdd",stroke_width=3).move_to([0,3.45,0])
        self.add(tela)
        # REGIÃO FOTOGRÁFICA: pixel x=48..672, y=175..506 em 720×1280.
        slot=Rectangle(width=6.94,height=3.68,fill_color="#d2e0eb",
                       fill_opacity=1,stroke_width=0).move_to([0,3.55,0])
        self.add(slot,txt("FOTOS REAIS DOS CARROS",21,AZUL).move_to(slot))
        nome=txt(NOMES[0],29,AZUL).move_to([0,1.04,0])
        self.add(nome)
        self.add(txt("INFORMAÇÕES CONFIRMADAS DIRETAMENTE COM A LOJA",
                     14,CARMIM).move_to([0,.57,0]))

        p=NL.nina("neutra","tarde")
        p["grupo"].remove(p["copo"])
        p=NL.posicionar(p,escala=1.28,pos=np.array([-1.67,-2.47,0]))
        self.add(p["grupo"])
        NL.animar_nina(self,p,LIP)

        titulo=selo("INFORMAÇÕES",cor=AZUL,letra=BRANCO,borda=AZUL,size=21).move_to([1.91,.06,0])
        self.add(titulo)
        modelo=selo("MODELO: CONSULTE",size=19).move_to([1.91,-.80,0])
        preco=selo("PREÇO: CONSULTE",size=20,cor=AMARELO,borda=AMARELO).move_to([1.91,-1.70,0])
        contato=selo("PEÇA A FICHA",size=21).move_to([1.91,-2.60,0])
        self.add(modelo,preco,contato)
        self.add(selo("A VENDEDORA",w=2.5,h=.53,cor=CARMIM,letra=BRANCO,borda=CARMIM,size=21).move_to([-2.05,-4.92,0]))

        anterior=None
        expresses=["ironica","neutra","chocada","ironica","neutra","ironica"]
        for seg in SEGS:
            i=int(seg["i"])
            if i>0:
                titulo_novo=txt(NOMES[i],29,AZUL).move_to(nome)
                self.play(Transform(nome,titulo_novo),run_time=.20)
                if i>=2 and i<=4:
                    self.play(Transform(modelo,selo(NOMES[i],size=19).move_to(modelo)),run_time=.19)
            NL.trocar_expressao(self,p,expresses[i],dur=.14)
            l=legend(seg["texto"])
            if anterior is not None:self.remove(anterior)
            self.add(l);anterior=l
            if i in (0,2,4):
                b=p["braco_esq"]
                self.play(Rotate(VGroup(b,p["mao_esq"]),angle=(-.17 if i!=2 else .19),
                                 about_point=b.get_start(),run_time=.22))
            remaining=float(seg["fim"])-self.renderer.time
            if remaining>.01:self.wait(remaining)
        if anterior is not None:self.remove(anterior)
        self.play(FadeIn(selo("FALE COM A LOJA PARA VALORES",w=7.42,h=.85,
                              cor=CARMIM,letra=BRANCO,borda=CARMIM,size=24).move_to([0,-6.20,0])),run_time=.20)
        self.wait(.8)
