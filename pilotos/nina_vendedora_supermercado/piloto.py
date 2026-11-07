"""Nina Vendedora: 10 ofertas ilustrativas de supermercado, desenhadas em Manim.

Personagem ORIGINAL do motor Nina, cabelo preto, voz feminina Kokoro
e gestos articulados. Todos os preços deste piloto são FICTÍCIOS.
"""
import json, os, sys
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

NL.RUIVO="#151c26"
NL.RUIVO_ESC="#414958"
NL.RUIVO_CL="#3d4c60"
NL.BLUSA="#c9344c"

ROOT_P=Path(__file__).resolve().parent
DATA=json.loads((ROOT_P/"itens.json").read_text(encoding="utf-8"))
OUT=Path(os.environ.get("PASTA_SUPERMERCADO","out"))
SEGS=json.loads((OUT/"segs.json").read_text(encoding="utf-8"))
LIP=json.loads((OUT/"lip.json").read_text(encoding="utf-8"))
assert len(DATA)==10 and len(SEGS)==12, "O piloto exige 10 itens e 12 falas"
CREME="#fff7e9"
VERMELHO="#c72d41"
MARINHO="#243347"
AMARELO="#ffda4e"
BRANCO="#ffffff"
TINTA="#1a3045"
CINZA="#d8e2eb"

def t(s,size=24,color=TINTA):
    return Text(str(s), font="DejaVu Sans", font_size=size, weight=BOLD, color=color)

def cartao(s,w=3.5,h=.76,color=BRANCO,ink=TINTA,border="#cbd8e3",fontsize=23):
    bg=RoundedRectangle(width=w,height=h,corner_radius=.16,
                        fill_color=color,fill_opacity=1,
                        stroke_color=border,stroke_width=2)
    label=t(s,fontsize,ink)
    if label.width>w-.24:label.scale_to_fit_width(w-.24)
    return VGroup(bg,label.move_to(bg))

def produto_arte(d):
    """Embalagens genéricas totalmente vetoriais, sem marcas comerciais."""
    kind=d["tipo"];cor=d["cor"]
    g=VGroup()
    if kind in ("saco","macarrao"):
        body=RoundedRectangle(width=2.65,height=3.24,corner_radius=.19,
                  fill_color=cor,fill_opacity=1,stroke_color="#2e4153",stroke_width=4)
        top=Rectangle(width=2.31,height=.16,stroke_width=0,
                      fill_color="#f1f4ef",fill_opacity=.74).move_to(body.get_top()+DOWN*.19)
        stripe=RoundedRectangle(width=2.25,height=.90,corner_radius=.08,
                       fill_color=BRANCO,fill_opacity=.92,stroke_width=0).move_to([0,.22,0])
        unit=t(d["unidade"].split()[-2]+" "+d["unidade"].split()[-1],15,MARINHO).move_to([0,-1.10,0])
        g.add(body,top,stripe,unit)
        if kind=="macarrao":
            for j in range(9):
                x=-.76+j*.19
                g.add(Line([x,-.80,0],[x+.09,.77,0],stroke_color="#f9ce72",stroke_width=5))
            g.add(stripe.copy())
        else:
            beads=VGroup(*[Ellipse(width=.14,height=.10,stroke_width=0,
                       fill_color=BRANCO,fill_opacity=.66).move_to([-.60+(j%5)*.30,-.62+(j//5)*.18,0])
                            for j in range(10)])
            g.add(beads)
    elif kind=="caixa":
        body=RoundedRectangle(width=2.30,height=3.15,corner_radius=.07,
              fill_color=cor,fill_opacity=1,stroke_color="#35506a",stroke_width=4)
        cap=Polygon([-1.15,1.53,0],[-.58,2.00,0],[.65,2.00,0],[1.15,1.53,0],
            fill_color="#e3eff7",fill_opacity=1,stroke_color="#35506a",stroke_width=3)
        label=RoundedRectangle(width=2.04,height=1.05,corner_radius=.11,
                  fill_color=BRANCO,fill_opacity=.92,stroke_width=0).move_to([0,.22,0])
        g.add(body,cap,label)
        for j in range(3):
            g.add(Circle(radius=.085,stroke_width=0,fill_color=BRANCO,fill_opacity=.7).move_to([-.5+j*.5,-.9,0]))
    elif kind=="garrafa":
        cap=RoundedRectangle(width=.87,height=.28,corner_radius=.05,
                     stroke_color="#435269",stroke_width=3,fill_color=cor,fill_opacity=1).move_to([0,1.78,0])
        neck=Rectangle(width=.78,height=.54,stroke_color="#435269",stroke_width=2,
                    fill_color=cor,fill_opacity=1).move_to([0,1.42,0])
        body=RoundedRectangle(width=1.93,height=2.82,corner_radius=.32,
                    stroke_color="#41596e",stroke_width=4,fill_color=cor,
                    fill_opacity=.85).move_to([0,-.18,0])
        label=RoundedRectangle(width=1.75,height=1.12,corner_radius=.10,
                    fill_color=BRANCO,fill_opacity=.95,stroke_width=0).move_to([0,-.17,0])
        shine=Line([-.69,-.92,0],[-.69,.91,0],stroke_color=BRANCO,stroke_width=6,stroke_opacity=.5)
        g.add(neck,body,cap,label,shine)
    else:  # 12 rolos de papel em embalagem ilustrativa
        cover=RoundedRectangle(width=2.98,height=3.14,corner_radius=.20,
                  fill_color=cor,fill_opacity=.35,stroke_color="#4f86b2",stroke_width=3)
        g.add(cover)
        for j in range(3):
            for k in range(3):
                c=Circle(radius=.39,fill_color=BRANCO,fill_opacity=1,
                           stroke_color="#a5bdcf",stroke_width=3).move_to([-.85+j*.85,-.89+k*.85,0])
                hole=Circle(radius=.11,fill_color="#c1a590",fill_opacity=1,stroke_width=0).move_to(c)
                g.add(c,hole)
    label=t(d["rotulo"],29,MARINHO)
    if label.width>2.0:label.scale_to_fit_width(2.0)
    label.move_to([0,.28,0])
    g.add(label)
    if g.height>3.70:g.scale_to_fit_height(3.70)
    return g.move_to([-1.65,2.32,0])

def legenda(fala):
    words=fala.split();lines=[];buf=""
    for w in words:
        if len(buf)+len(w)+1>41 and buf:
            lines.append(buf);buf=w
        else:buf=(buf+" "+w).strip()
    if buf:lines.append(buf)
    if len(lines)>4:
        lines=lines[:4]
        lines[-1]=lines[-1].rstrip(".!,")+"…"
    m=VGroup(*(t(line,18,BRANCO) for line in lines)).arrange(DOWN,buff=.075)
    if m.width>7.0:m.scale_to_fit_width(7.0)
    bg=RoundedRectangle(width=7.56,height=1.48,corner_radius=.16,
                   fill_color="#1c304c",fill_opacity=.985,stroke_width=0)
    return VGroup(bg,m.move_to(bg)).move_to([0,-6.13,0])

def alterar_braco(arm,hand,delta,secs=.32):
    x,y=delta
    pivot=arm.get_start().copy()
    tip=pivot+np.array([x,y,0])
    bend=pivot+np.array([x*.58,-.16+y*.42,0])
    path=VMobject()
    path.set_points_as_corners([pivot,bend,tip])
    path.set_stroke(NL.PT,width=15)
    return AnimationGroup(Transform(arm,path),hand.animate.move_to(tip),
                          lag_ratio=0,run_time=secs,rate_func=smooth)

class Supermercado(Scene):
    def construct(self):
        self.camera.background_color=CREME
        main=RoundedRectangle(width=7.55,height=5.32,corner_radius=.25,
                        stroke_color="#dbd2c0",stroke_width=2,
                        fill_color=BRANCO,fill_opacity=1).move_to([0,2.77,0])
        self.add(main)
        bar=Rectangle(width=8.15,height=1.05,fill_color=VERMELHO,
                      fill_opacity=1,stroke_width=0).move_to([0,6.54,0])
        self.add(bar,t("PLANTÃO DAS OFERTAS",33,BRANCO).move_to([0,6.56,0]))
        self.add(t("NINA VENDEDORA  •  SUPERMERCADO",20,VERMELHO).move_to([0,5.68,0]))
        self.add(cartao("10 ITENS EM PROMOÇÃO",w=6.8,h=.50,color="#ffeebd",
                         ink=MARINHO,fontsize=20,border="#ffeebd").move_to([0,5.15,0]))

        title=t("OFERTAS DA SEMANA",27,MARINHO).move_to([0,4.55,0])
        self.add(title)
        pkg=produto_arte(DATA[0])
        self.add(pkg)
        tag=cartao("PREÇO ILUSTRATIVO",w=3.55,h=.61,color=VERMELHO,
                     ink=BRANCO,border=VERMELHO,fontsize=17).move_to([1.82,3.95,0])
        price=cartao("R$ --,--",w=3.55,h=1.13,color=AMARELO,ink=MARINHO,
                     border="#e5ae2e",fontsize=33).move_to([1.82,2.90,0])
        unit=cartao("EMBALAGEM",w=3.55,h=.72,fontsize=19).move_to([1.82,1.95,0])
        count=t("ITEM 01/10",19,VERMELHO).move_to([1.82,1.37,0])
        self.add(tag,price,unit,count)
        self.add(t("PREÇOS FICTÍCIOS • APENAS DEMONSTRAÇÃO",14,VERMELHO).move_to([0,.40,0]))

        # A Nina continua sendo a personagem ORIGINAL desenhada em Manim.
        n=NL.nina("neutra","tarde")
        n["grupo"].remove(n["copo"])
        n=NL.posicionar(n,escala=1.24,pos=np.array([-1.70,-2.59,0]))
        self.add(n["grupo"])
        NL.animar_nina(self,n,LIP)
        handR=Dot(n["grupo"][10].get_end(),radius=.095,color=NL.PELE)
        n["grupo"].add(handR)
        left=n["braco_esq"]; right=n["grupo"][10]
        clock={"dy":0}
        def breathe(obj,dt):
            new=.014*np.sin(self.renderer.time*1.7)
            obj.shift(UP*(new-clock["dy"]))
            clock["dy"]=new
        n["grupo"].add_updater(breathe)
        self.add(cartao("NINA VENDEDORA",w=2.58,h=.58,color=VERMELHO,
                 ink=BRANCO,border=VERMELHO,fontsize=21).move_to([-2.0,-4.80,0]))
        self.add(cartao("10 OFERTAS",w=3.4,h=.63,color=MARINHO,
                ink=BRANCO,border=MARINHO,fontsize=19).move_to([1.86,-.38,0]))
        summary=cartao("VEJA O ENCARTE",w=3.50,h=.85,color=AMARELO,
                          ink=MARINHO,border=AMARELO,fontsize=22).move_to([1.84,-1.48,0])
        self.add(summary)
        self.add(cartao("VALORES DE EXEMPLO",w=3.50,h=.68,
                  fontsize=16).move_to([1.84,-2.48,0]))
        last_caption=None
        expressions=["ironica","neutra","chocada","neutra","ironica","neutra",
                     "desconfiada","neutra","ironica","neutra","chocada","ironica"]
        for seg in SEGS:
            i=int(seg["i"])
            if 1<=i<=10:
                d=DATA[i-1]
                nxt=produto_arte(d)
                nxt_title=t(d["nome"],27,MARINHO).move_to(title)
                if nxt_title.width>6.9:nxt_title.scale_to_fit_width(6.9)
                nxt_price=cartao(d["preco"],w=3.55,h=1.13,color=AMARELO,
                                ink=MARINHO,border="#e5ae2e",fontsize=35).move_to(price)
                nxt_unit=cartao(d["unidade"],w=3.55,h=.72,
                                fontsize=19).move_to(unit)
                nxt_count=t("ITEM "+str(i).zfill(2)+"/10",19,VERMELHO).move_to(count)
                self.play(Transform(title,nxt_title),Transform(price,nxt_price),
                     Transform(unit,nxt_unit),Transform(count,nxt_count),
                     FadeOut(pkg,shift=LEFT*.18),FadeIn(nxt,shift=RIGHT*.24),
                     run_time=.32)
                pkg=nxt
                self.play(Transform(summary,cartao(
                          "OFERTA "+str(i).zfill(2)+" DE 10",w=3.50,h=.85,
                          color=AMARELO,ink=MARINHO,border=AMARELO,
                          fontsize=22).move_to(summary)),run_time=.14)
            elif i==11:
                self.play(Transform(title,t("OFERTAS DE DEMONSTRAÇÃO",25,MARINHO).move_to(title)),
                          run_time=.22)
            NL.trocar_expressao(self,n,expressions[i],dur=.13)
            caps=legenda(seg["texto"])
            if last_caption:self.remove(last_caption)
            self.add(caps)
            last_caption=caps
            poseL=[(-.75,.35),(-.41,-.38),(-.80,.36),(-.45,-.32)][i%4]
            poseR=[(.95,.40),(1.10,.22),(.84,.65),(1.03,.30)][i%4]
            self.play(alterar_braco(left,n["mao_esq"],poseL),
                      alterar_braco(right,handR,poseR))
            elapsed=float(seg["fim"])-self.renderer.time
            if elapsed>1.9:
                self.wait(min(.9,elapsed*.36))
                self.play(alterar_braco(left,n["mao_esq"],(-.44,-.51),.28),
                          alterar_braco(right,handR,(.87,.05),.28))
            elapsed=float(seg["fim"])-self.renderer.time
            if elapsed>.01:self.wait(elapsed)
        if last_caption:self.remove(last_caption)
        self.play(FadeIn(cartao("MANDE UMA MENSAGEM",w=7.5,h=.90,
                               color=VERMELHO,ink=BRANCO,border=VERMELHO,
                               fontsize=28).move_to([0,-6.10,0])),run_time=.25)
        self.wait(.8)
