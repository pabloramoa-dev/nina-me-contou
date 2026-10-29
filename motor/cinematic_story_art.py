"""Quadros cinematograficos 2D para Nina Me Contou: Pillow/CPU, zero API/GPU.

Ilustracoes de apoio sao personagens FICTICIOS do roteiro; nao substituem
a apresentadora Nina (que continua na camada base, com voz e lip-sync originais).
"""
from __future__ import annotations

import io
import math
import random
import re
import shutil
import unicodedata
from pathlib import Path

from PIL import Image, ImageDraw

WIDTH, HEIGHT = 1440, 900
INK = "#332b3d"
CREAM = "#ffeed4"
GOLD = "#f4bd67"
PINK = "#e5a1a4"
BLUE = "#8ac3c2"


def normalizar(text):
    text = unicodedata.normalize("NFKD", str(text).lower())
    return "".join(ch for ch in text if not unicodedata.combining(ch))


def tema(scene, ep):
    """A cena corrente ganha prioridade sobre o titulo e nao antecipa o final."""
    txt = normalizar(scene.get("text", ""))
    title = normalizar(ep.get("titulo", ""))
    grupos = [
        ("photo", ("foto", "selfie", "fotografia", "imagem", "reflexo", "galeria", "retrato")),
        ("phone", ("celular", "telefone", "mensagem", "direct", "whatsapp", "ligacao", "chamada", "senha")),
        ("ring", ("alianca", "anel", "casamento", "noivado", "noiva", "noivo")),
        ("letter", ("bilhete", "carta", "envelope", "comprovante", "documento", "papel", "recibo")),
        ("car", ("carro", "corrida", "uber", "motorista", "veiculo", "garagem")),
        ("dinner", ("jantar", "restaurante", "cozinha", "mesa", "cafe", "almoco")),
        ("house", ("casa", "predio", "apartamento", "porta", "quarto", "portaria")),
        ("clock", ("relogio", "hora extra", "madrugada", "horario")),
        ("gift", ("presente", "aniversario", "surpresa", "pacote")),
    ]
    for text in (txt, title):
        for key, words in grupos:
            if any(w in text for w in words):
                return key
    return "people"


def _rr(draw, xy, fill, radius=22, outline=None, width=6):
    draw.rounded_rectangle(tuple(int(x) for x in xy), radius=max(1, int(radius)),
                           fill=fill, outline=outline, width=width)


def _ellipse(draw, xy, fill, outline=None, width=5):
    draw.ellipse(tuple(int(x) for x in xy), fill=fill, outline=outline, width=width)


def _person(draw, x, y, s=1.0, coat=BLUE, hair="#3c3041", side=1):
    """Silhueta original com rosto simples; nao representa identidade real."""
    def b(x1,y1,x2,y2):
        return (x+x1*s,y+y1*s,x+x2*s,y+y2*s)
    _rr(draw,b(-115,135,122,455),coat,72*s,INK,7)
    _ellipse(draw,b(-95,-25,100,175),hair,INK,6)
    _ellipse(draw,b(-83,25,91,181),"#d9a27e",INK,5)
    _rr(draw,b(-77,5,85,66),hair,26*s)
    _ellipse(draw,b(-35+side*28,93,-23+side*28,107),INK)
    draw.arc(b(-18,108,35,148),10,160,fill=INK,width=max(3,int(4*s)))
    _rr(draw,b(-127,236,-66,375),coat,25*s,INK,5)


def _prop(draw, kind, x, y, s=1.0):
    def b(x1,y1,x2,y2):
        return (x+x1*s,y+y1*s,x+x2*s,y+y2*s)
    if kind in ("phone", "photo"):
        _rr(draw,b(-170,-285,170,290),"#e4b1a8",36*s,INK,10)
        _rr(draw,b(-140,-226,140,220),"#fff5df",19*s,INK,6)
        if kind=="phone":
            for k, color in enumerate((BLUE, PINK, GOLD)):
                _rr(draw,b(-106,-160+105*k,86,-107+105*k),color,18*s,INK,3)
            _ellipse(draw,b(-21,249,21,274),CREAM,INK,4)
        else:
            _rr(draw,b(-111,-152,110,158),"#96bfbe",18*s,INK,5)
            draw.polygon([(x-99*s,y+132*s),(x-21*s,y-25*s),(x+46*s,y+57*s),
                          (x+106*s,y-27*s),(x+107*s,y+143*s)],fill="#66939e")
            _ellipse(draw,b(42,-120,92,-70),GOLD)
    elif kind=="ring":
        _ellipse(draw,b(-192,-95,192,290),GOLD,INK,13)
        _ellipse(draw,b(-100,-5,100,189),CREAM,INK,9)
        draw.polygon([(x-110*s,y-94*s),(x,y-233*s),(x+110*s,y-94*s),
                      (x,y-4*s)],fill="#c1e2ed")
        draw.line([(x-110*s,y-94*s),(x,y-233*s),(x+110*s,y-94*s),(x,y-4*s),
                   (x-110*s,y-94*s)],fill=INK,width=8)
    elif kind=="letter":
        _rr(draw,b(-277,-135,278,236),CREAM,24*s,INK,9)
        draw.polygon([(x-267*s,y-116*s),(x,y+97*s),(x+268*s,y-116*s)],fill=PINK)
        draw.line([(x-267*s,y+221*s),(x,y+4*s),(x+268*s,y+221*s)],
                  fill=INK,width=max(3,int(8*s)))
    elif kind=="car":
        _rr(draw,b(-330,-92,333,163),BLUE,88*s,INK,9)
        draw.polygon([(x-184*s,y-90*s),(x-91*s,y-210*s),
                      (x+168*s,y-210*s),(x+265*s,y-90*s)],fill="#b3dfdd")
        draw.line([(x-184*s,y-90*s),(x-91*s,y-210*s),
                   (x+168*s,y-210*s),(x+265*s,y-90*s)],fill=INK,width=7)
        for off in (-219,219):
            _ellipse(draw,b(off-62,105,off+62,238),INK)
            _ellipse(draw,b(off-23,147,off+23,196),CREAM)
    elif kind=="house":
        draw.polygon([(x-300*s,y-70*s),(x,y-330*s),(x+301*s,y-70*s)],
                     fill="#a57c99")
        _rr(draw,b(-246,-60,253,277),"#edbeaa",9*s,INK,8)
        _rr(draw,b(-51,65,95,278),"#65516d",12*s,INK,7)
        _rr(draw,b(-178,22,-85,128),GOLD,10*s,INK,5)
        _rr(draw,b(135,22,226,128),GOLD,10*s,INK,5)
    elif kind=="clock":
        _ellipse(draw,b(-237,-235,237,239),CREAM,INK,10)
        _ellipse(draw,b(-198,-196,198,199),"#f8d2ae",INK,5)
        draw.line([(x,y),(x,y-135*s)],fill=INK,width=16)
        draw.line([(x,y),(x+89*s,y+69*s)],fill=INK,width=16)
        _ellipse(draw,b(-23,-23,23,23),PINK)
    elif kind=="gift":
        _rr(draw,b(-265,-119,265,215),PINK,32*s,INK,8)
        _rr(draw,b(-290,-157,290,-92),GOLD,20*s,INK,7)
        _rr(draw,b(-43,-157,43,215),CREAM,3*s)
        draw.arc(b(-135,-257,20,-122),190,355,fill=GOLD,width=15)
        draw.arc(b(-20,-257,135,-122),190,355,fill=GOLD,width=15)
    elif kind=="dinner":
        _ellipse(draw,b(-260,-115,268,196),CREAM,INK,9)
        _ellipse(draw,b(-192,-67,190,133),"#a3c4bb",INK,6)
        _ellipse(draw,b(-135,-38,133,100),"#dc946c",INK,5)
        for xx in (-215,212):
            draw.line([(x+xx*s,y-157*s),(x+xx*s,y+196*s)],fill=INK,width=12)
    else:
        _person(draw,x,y-150*s,s*.83,PINK)


def _background(stage):
    colors=[
        ("#293c55","#a37b8c"), ("#2b3755","#b98d95"), ("#364054","#b59177"),
        ("#3b314c","#b99a90"), ("#263c52","#8eafa7"),
    ]
    top, bottom=colors[stage%len(colors)]
    def parse(c): return [int(c[k:k+2],16) for k in (1,3,5)]
    a,b=parse(top),parse(bottom)
    img=Image.new("RGB",(WIDTH,HEIGHT))
    d=ImageDraw.Draw(img)
    for yy in range(HEIGHT):
        t=yy/(HEIGHT-1)
        tone=tuple(round(a[k]*(1-t)+b[k]*t) for k in range(3))
        d.line((0,yy,WIDTH,yy),fill=tone)
    # Shapes at distinct depths create an editorial interior/street panorama.
    for k in range(13):
        xx=55+k*122
        h=130+(k*67)%220
        d.rectangle((xx,HEIGHT-h,xx+91,HEIGHT),fill="#394058")
        if k%2:
            _rr(d,(xx+20,HEIGHT-h+32,xx+51,HEIGHT-h+85),"#f1c88e",7,None,0)
    d.rectangle((0,825,WIDTH,HEIGHT),fill="#3a344d")
    return img


def render(scene,ep):
    """Renderiza quadro horizontal compativel com camada superior do Remotion."""
    idx=int(scene.get("scene",0))
    kind=tema(scene,ep)
    img=_background(idx)
    draw=ImageDraw.Draw(img)
    # Foco narrativo em local ou pessoas; cambia angulo entre cada quadro.
    if kind=="people":
        _person(draw,452,257,1.08,PINK)
        _person(draw,977,275,1.01,BLUE,hair="#67495c",side=-1)
        draw.arc((527,338,926,669),200,352,fill=GOLD,width=10)
    elif kind in ("house","car"):
        _prop(draw,kind,840,529,1.14)
        _person(draw,324,345,.82,PINK)
    elif idx%3==0:
        _person(draw,338,300,.96,BLUE)
        _prop(draw,kind,939,492,.89)
    elif idx%3==1:
        _prop(draw,kind,680,508,1.23)
        _ellipse(draw,(1080,115,1164,199),GOLD)
    else:
        _person(draw,354,355,.83,PINK)
        _person(draw,615,366,.77,BLUE,hair="#635c5a",side=-1)
        _prop(draw,kind,1110,539,.66)
    # Subtle grain, deterministic for reproducible renders and cache.
    rnd=random.Random(629+idx)
    film=ImageDraw.Draw(img)
    for _ in range(170):
        px=rnd.randrange(WIDTH)
        py=rnd.randrange(HEIGHT)
        film.point((px,py),fill="#b7aaa2")
    output=io.BytesIO()
    img.save(output,format="PNG",optimize=True)
    return output.getvalue()


def planejar_quadros(ep,segs,dur,intervalo=7.0):
    if not 1 <= intervalo <= 30:
        raise ValueError("Intervalo invalido")
    if len(segs)!=len(ep["batidas"]) or not segs:
        raise ValueError("Falhas de sincronismo entre falas e timeline")
    frames=[]
    for idx in range(math.ceil(dur/intervalo)):
        start=idx*intervalo
        if start>=dur:
            break
        beat=next((i for i,s in enumerate(segs) if start < float(s["fim"])),
                  len(segs)-1)
        frames.append({"scene":idx,"start":round(start,5),"end":round(min(dur,start+intervalo),5),
                       "beat":beat,"text":ep["batidas"][beat]["fala"]})
    return frames


def preparar_quadros(ep,segs,dur,public,base_assets=None,visual_report=None,intervalo=7.0):
    """Grava imagens em public/nina-cinema; referencias aprovadas tem precedencia."""
    public=Path(public)
    destino=public/"nina-cinema"
    destino.mkdir(parents=True,exist_ok=True)
    # O diretório public pode sobreviver a renders no mesmo runner.
    for old in destino.glob("frame-*.png"):
        old.unlink()
    aprovadas=[]
    for scene in (visual_report or {}).get("scenes",[]):
        if scene.get("status")=="approved_asset":
            name=scene.get("asset","")
            if re.fullmatch(r"visual-scene-[0-9]+\.png",name):
                aprovadas.append((float(scene["start"]),float(scene["end"]),name))
    frames=planejar_quadros(ep,segs,dur,intervalo=intervalo)
    ready=[]
    for spec in frames:
        file=f"frame-{spec['scene']:03d}.png"
        dest=destino/file
        match=next((name for a,b,name in aprovadas if a<=spec["start"]<b),None)
        if match and base_assets and (Path(base_assets)/match).is_file():
            shutil.copyfile(Path(base_assets)/match,dest)
            origin="approved"
        else:
            dest.write_bytes(render(spec,ep))
            origin="cinematic_cpu"
        ready.append({"start":spec["start"],"end":spec["end"],
                      "src":f"nina-cinema/{file}","origin":origin})
    return ready
