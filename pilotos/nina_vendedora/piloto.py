"""A Vendedora — personagem vetorial original da Nina com cabelo preto.

Piloto Manim em cenário CLARO de telejornal automotivo; usa o motor facial
e o lip sync original da Nina, sem fotografias de pessoas.
Todas as características exibidas neste exemplo são fictícias.
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

config.frame_width = 8
config.frame_height = 14.222
config.pixel_width = 720
config.pixel_height = 1280
config.frame_rate = 24

# A personagem Nina original não é modificada no projeto. Este piloto altera
# somente cores do mesmo desenho vetorial no processo de renderização isolado.
NL.RUIVO = "#161923"       # preto natural, levemente azulado
NL.RUIVO_ESC = "#333a48"   # detalhes dos fios e sobrancelhas
NL.RUIVO_CL = "#424958"    # volume da franja, sem ficar cinza
NL.BLUSA = "#ca374e"       # blazer/blusa de apresentadora

MARINHO = "#173153"
MARINHO_ESCURO = "#102641"
AZUL_MEDIO = "#315b86"
AZUL_CLARO = "#edf3f9"
BRANCO = "#ffffff"
TINTA = "#19304a"
OURO = "#f5c94b"
CARMIM = "#c7374b"

V = json.loads((Path(__file__).parent / "veiculo_demo.json").read_text(encoding="utf-8"))
P = Path(os.environ.get("PASTA_VENDEDORA", str(Path(__file__).parent / "saida")))
SEGS = json.loads((P / "segs.json").read_text(encoding="utf-8"))
LIP = json.loads((P / "lip.json").read_text(encoding="utf-8"))


def texto(s, tamanho=28, cor=TINTA):
    return Text(str(s), font="DejaVu Sans", weight=BOLD,
                font_size=tamanho, color=cor)


def tarjeta(s, largura=6.9, altura=.75, fundo=MARINHO, tam=25,
            cor=BRANCO, borda=None):
    bg = RoundedRectangle(
        width=largura, height=altura, corner_radius=.14,
        stroke_color=borda or fundo, stroke_width=1.5,
        fill_color=fundo, fill_opacity=1,
    )
    t = texto(s, tam, cor)
    if t.width > largura - .34:
        t.scale_to_fit_width(largura - .34)
    return VGroup(bg, t.move_to(bg))


def automovel_vetorial():
    """Desenho próprio mais detalhado, SOMENTE para o carro de demonstração.

    Em anúncios verdadeiros usa a foto do veículo anunciado, sem inventar
    imagens nem itens da ficha técnica.
    """
    sombra = Ellipse(width=5.5, height=.27, stroke_width=0,
                     fill_color="#9aaebe", fill_opacity=.48).move_to([0,-.81,0])
    base = Polygon(
        [-2.54, -.36, 0], [-2.48, .04, 0], [-2.15, .39, 0],
        [-1.43, .43, 0], [-.80, 1.13, 0], [.80, 1.13, 0],
        [1.58, .45, 0], [2.32, .36, 0], [2.53, .06, 0],
        [2.46, -.47, 0], [2.13, -.62, 0], [-2.30, -.62, 0],
        fill_color="#8cbbd5", fill_opacity=1,
        stroke_color="#4e789b", stroke_width=3,
    )
    vidro_esq = Polygon(
        [-1.25,.48,0],[-.62,1.00,0],[.12,1.00,0],[.12,.48,0],
        fill_color="#2e5878",fill_opacity=1,stroke_width=1,
        stroke_color="#c9e4f1",
    )
    vidro_dir = Polygon(
        [.23,.48,0],[.23,1.00,0],[.72,1.00,0],[1.26,.48,0],
        fill_color="#2e5878",fill_opacity=1,stroke_width=1,
        stroke_color="#c9e4f1",
    )
    linha_porta=Line([.19,.39,0],[.19,-.45,0],stroke_width=3,stroke_color="#47789d")
    puxadores=VGroup(
        Line([-.24,.13,0],[-.02,.13,0],stroke_width=4,stroke_color="#eef7fb"),
        Line([.54,.13,0],[.77,.13,0],stroke_width=4,stroke_color="#eef7fb"),
    )
    detalhe=Line([-2.31,-.10,0],[2.30,-.10,0],stroke_width=3,
                  stroke_color="#dff4fc",stroke_opacity=.7)
    farol=RoundedRectangle(width=.37,height=.16,corner_radius=.06,
                            stroke_width=0,fill_color="#fff0ad",
                            fill_opacity=1).move_to([2.18,.07,0])
    lanterna=RoundedRectangle(width=.24,height=.19,corner_radius=.04,
                               stroke_width=0,fill_color="#d43c4f",
                               fill_opacity=1).move_to([-2.35,.08,0])
    rodas=VGroup()
    for x in (-1.53,1.56):
        roda=Circle(radius=.41,fill_color="#232b36",fill_opacity=1,
                    stroke_color="#222b39",stroke_width=3).move_to([x,-.54,0])
        aro=Circle(radius=.235,fill_color="#c6d1da",fill_opacity=1,
                   stroke_color="#718a9c",stroke_width=3).move_to(roda)
        miolo=Circle(radius=.055,fill_color="#fafcff",fill_opacity=1,
                     stroke_width=0).move_to(roda)
        rodas.add(roda,aro,miolo)
    return VGroup(sombra,base,vidro_esq,vidro_dir,linha_porta,
                  puxadores,detalhe,farol,lanterna,rodas)


def imagem_ou_ilustracao():
    """Aceita foto real em V['foto'] quando o cadastro do carro a tiver."""
    path = V.get("foto")
    if path:
        f = (ROOT / path).resolve()
        if f.is_file() and f.suffix.lower() in (".jpg", ".jpeg", ".png"):
            img=ImageMobject(str(f))
            if img.width > 6.25: img.scale_to_fit_width(6.25)
            if img.height > 2.70: img.scale_to_fit_height(2.70)
            return img
        raise FileNotFoundError(f"Foto anunciada não encontrada: {f}")
    return automovel_vetorial().scale(1.13)


def legenda(fala):
    linhas=[]
    atual=""
    for palavra in fala.split():
        if len(atual)+len(palavra)+1 > 37 and atual:
            linhas.append(atual)
            atual=palavra
        else:
            atual=(atual+" "+palavra).strip()
    if atual:linhas.append(atual)
    # Evita que texto de legenda invada a personagem e o painel.
    t=VGroup(*(texto(l,20,BRANCO) for l in linhas[:4])).arrange(DOWN,buff=.065)
    if t.width>6.95:t.scale_to_fit_width(6.95)
    fundo=RoundedRectangle(width=7.40,height=1.35,corner_radius=.15,
                           fill_color=MARINHO_ESCURO,fill_opacity=.97,
                           stroke_color="#70859b",stroke_width=1.5)
    return VGroup(fundo,t.move_to(fundo)).move_to([0,-6.24,0])


class VendedoraCarros(Scene):
    def construct(self):
        self.camera.background_color=AZUL_CLARO

        # Estúdio claro: fundo é distinto do cabelo PRETO da Vendedora.
        palco=Rectangle(width=8.5,height=6.65,stroke_width=0,
                        fill_color="#dceaf3",fill_opacity=1).move_to([0,-2.24,0])
        faixa=Polygon([-4,-.20,0],[-1.3,-.20,0],[1.9,-5.63,0],[-4,-5.63,0],
                      fill_color="#f4f8fc",fill_opacity=.64,stroke_width=0)
        halo=Ellipse(width=4.6,height=5.9,stroke_width=0,
                     fill_color="#fffdf3",fill_opacity=.90).move_to([-1.95,-2.28,0])
        self.add(palco,faixa,halo)

        # Faixa de telejornal com hierarquia simples.
        header=Rectangle(width=8.25,height=1.02,stroke_width=0,
                         fill_color=MARINHO_ESCURO,fill_opacity=1).move_to([0,6.59,0])
        self.add(header)
        self.add(texto("PLANTÃO DOS SEMINOVOS",30,BRANCO).move_to([0,6.60,0]))
        self.add(texto("A VENDEDORA APRESENTA",21,MARINHO).move_to([0,5.77,0]))

        # Painel em branco estilo showroom, sem bloco azul-escuro.
        sombra_painel=RoundedRectangle(width=7.42,height=3.91,corner_radius=.20,
                                       fill_color="#adbfce",fill_opacity=.24,
                                       stroke_width=0).move_to([.07,3.45,0])
        painel=RoundedRectangle(width=7.42,height=3.91,corner_radius=.20,
                                 fill_color=BRANCO,fill_opacity=1,
                                 stroke_color="#c4d3e2",stroke_width=2).move_to([0,3.51,0])
        self.add(sombra_painel,painel)
        self.add(texto("VEÍCULO EM DESTAQUE",23,MARINHO).move_to([0,5.05,0]))
        auto=imagem_ou_ilustracao().move_to([0,3.50,0])
        self.play(FadeIn(auto,shift=RIGHT*.18),run_time=.28)
        self.add(texto(V["modelo"],28,MARINHO).move_to([0,1.86,0]))
        self.add(texto("ILUSTRAÇÃO E PREÇO FICTÍCIOS",16,CARMIM).move_to([0,1.40,0]))

        # Personagem é o MESMO vetor da Nina original, não foto com boca mexendo.
        p=NL.nina("neutra","tarde")
        p["grupo"].remove(p["copo"])
        p=NL.posicionar(p,escala=1.26,pos=np.array([-1.65,-2.49,0]))
        self.add(p["grupo"])
        NL.animar_nina(self,p,LIP)

        # Painel das especificações com menos informações simultâneas.
        self.add(tarjeta("FICHA DO VEÍCULO",largura=3.55,altura=.59,
                         fundo=MARINHO,tam=19).move_to([1.89,.45,0]))
        ano=tarjeta("ANO • MOTOR",largura=3.55,altura=.70,
                    fundo=BRANCO,cor=TINTA,borda="#b6ccda",tam=22).move_to([1.89,-.42,0])
        km=tarjeta("QUILOMETRAGEM",largura=3.55,altura=.70,
                   fundo=BRANCO,cor=TINTA,borda="#b6ccda",tam=20).move_to([1.89,-1.29,0])
        preco=tarjeta("VALOR DE EXEMPLO",largura=3.55,altura=1.02,
                      fundo=OURO,cor=MARINHO_ESCURO,tam=22).move_to([1.89,-2.52,0])
        self.add(ano,km,preco)

        # Identificação discreta, sem tarja atravessando o corpo.
        self.add(tarjeta("A VENDEDORA",largura=2.55,altura=.57,
                         fundo=CARMIM,tam=22).move_to([-2.05,-4.88,0]))

        atual=None
        expressao={0:"ironica",1:"neutra",2:"desconfiada",3:"chocada",
                   4:"neutra",5:"ironica"}
        for s in SEGS:
            i=int(s["i"])
            nova=legenda(s["texto"])
            if atual is not None:self.remove(atual)
            self.add(nova)
            atual=nova
            if i in expressao:
                NL.trocar_expressao(self,p,expressao[i],dur=.14)
            if i == 1:
                self.play(Transform(ano,tarjeta(
                    f'{V["ano"]} • {V["motor"]}',largura=3.55,altura=.70,
                    fundo=BRANCO,cor=TINTA,borda="#b6ccda",tam=22
                ).move_to(ano)),run_time=.22)
            if i == 2:
                self.play(Transform(km,tarjeta(
                    f'{V["km"]} KM',largura=3.55,altura=.70,
                    fundo=BRANCO,cor=TINTA,borda="#b6ccda",tam=24
                ).move_to(km)),run_time=.22)
            if i == 3:
                self.play(Transform(preco,tarjeta(
                    V["preco"],largura=3.55,altura=1.02,
                    fundo=OURO,cor=MARINHO_ESCURO,tam=31
                ).move_to(preco)),run_time=.24)
            if i in (0,2,4):
                br=p["braco_esq"]
                self.play(Rotate(VGroup(br,p["mao_esq"]),
                                 angle=(-.16 if i != 2 else .23),
                                 about_point=br.get_start(),
                                 run_time=.24))
            resto=float(s["fim"])-self.renderer.time
            if resto > .015:self.wait(resto)

        if atual is not None:self.remove(atual)
        self.play(FadeIn(tarjeta("FALE COM O VENDEDOR DA LOJA",
                                largura=7.15,altura=.84,fundo=CARMIM,
                                tam=27).move_to([0,-6.2,0])),run_time=.3)
        self.wait(1)
