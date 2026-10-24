#!/usr/bin/env python3
"""Breno na Pauta — piloto independente da Nina, só para avaliação."""
import json
import math
import os
import pathlib
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "saida"
OUT.mkdir(exist_ok=True)
W, H, FPS = 540, 960, 18

NEWS = [
    {
        "tag": "APRESENTAÇÃO", "kind": "ABERTURA",
        "title": "BEM-VINDO AO BRENO NA PAUTA",
        "caption": "Política com energia e fatos na mesa",
        "fala": "Breno na Pauta! Fato é fato, opinião eu assino. Hoje tem economia, segurança e transparência nas redes. Vamos nessa!",
        "source": "EDIÇÃO PILOTO • 24 OUT 2026"
    },
    {
        "tag": "FATO", "kind": "DEBATE",
        "title": "O ÚLTIMO DEBATE",
        "caption": "Economia, educação e segurança no centro",
        "fala": "No debate presidencial de ontem, Lula e Flávio Bolsonaro discutiram custo de vida, educação, obras e segurança pública.",
        "source": "UOL • 24 OUT 2026"
    },
    {
        "tag": "FATO", "kind": "PROPOSTAS",
        "title": "CRÉDITO E INFRAESTRUTURA",
        "caption": "Promessas: crédito, rodovias e ferrovias",
        "fala": "Flávio prometeu crédito para empreendedores periféricos, concessões de rodovias e expansão de ferrovias. São propostas, ainda não resultados.",
        "source": "UOL • 24 OUT 2026"
    },
    {
        "tag": "OPINIÃO", "kind": "ANÁLISE",
        "title": "BRENO ANALISA",
        "caption": "Empreender importa. E a conta?",
        "fala": "Minha análise conservadora: ver empreendedorismo e infraestrutura em destaque me anima! Mas quero saber quanto custa, como será feito e quem fiscaliza.",
        "source": "COMENTÁRIO EDITORIAL"
    },
    {
        "tag": "FATO", "kind": "CONTRAPONTO",
        "title": "O QUE LULA PROPÔS",
        "caption": "Ensino integral e obras públicas",
        "fala": "Lula defendeu ampliar o ensino integral, iniciativas de apoio aos estudantes e obras do PAC. São outras prioridades que também merecem avaliação.",
        "source": "UOL • 24 OUT 2026"
    },
    {
        "tag": "OPINIÃO", "kind": "SEGURANÇA",
        "title": "SEGURANÇA SEM ATALHO",
        "caption": "Metas claras e resultados verificáveis",
        "fala": "Na segurança, os candidatos apresentaram caminhos diferentes. Antes de qualquer discurso inflamado, eu quero metas claras e dados públicos.",
        "source": "COMENTÁRIO EDITORIAL"
    },
    {
        "tag": "FATO", "kind": "REDES SOCIAIS",
        "title": "TSE COBRA INFORMAÇÕES",
        "caption": "Pedido de dados não é prova de favorecimento",
        "fala": "Nas redes, o TSE cobrou informações da Meta sobre a distribuição de publicações políticas. A solicitação não comprova favorecimento.",
        "source": "AGÊNCIA BRASIL • 19 OUT 2026"
    },
    {
        "tag": "OPINIÃO", "kind": "LIBERDADE",
        "title": "LIBERDADE E REGRAS",
        "caption": "Transparência deve valer para todos",
        "fala": "Na minha visão conservadora, liberdade de expressão e transparência andam juntas. Regra clara deve valer para todos, sem privilégios.",
        "source": "COMENTÁRIO EDITORIAL"
    },
    {
        "tag": "ENCERRAMENTO", "kind": "ATÉ A PRÓXIMA",
        "title": "FATO É FATO!",
        "caption": "Opinião, eu assino",
        "fala": "Eu sou o Breno. Política com energia, senso crítico e fonte na tela. Qual dessas propostas você gostaria de ver explicada em números?",
        "source": "PILOTO • NÃO PUBLICADO"
    }
]

def font(size, bold=False):
    opts = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    return ImageFont.truetype(next(p for p in opts if os.path.isfile(p)), size)

BOLD16 = font(16, True)
BOLD18 = font(18, True)
BOLD22 = font(22, True)
BOLD26 = font(26, True)
BOLD33 = font(33, True)
BOLD41 = font(41, True)
REG17 = font(17)
REG19 = font(19)

WHITE = (249, 250, 251)
GOLD = (247, 176, 61)
TEAL = (80, 222, 203)
NAVY = (10, 24, 43)

def rr(d, xy, rad, fill, outline=None, width=1):
    d.rounded_rectangle(tuple(map(int, xy)), radius=rad, fill=fill, outline=outline, width=width)

def center(d, y, s, f, color, maxwidth=505):
    while d.textbbox((0, 0), s, font=f)[2] > maxwidth and len(s) > 5:
        s = s[:-2] + "…"
    bw = d.textbbox((0, 0), s, font=f)[2]
    d.text(((W - bw) / 2, y), s, font=f, fill=color)

def lines(d, txt, f, max_width):
    words = txt.split()
    result, row = [], ""
    for word in words:
        trial = (row + " " + word).strip()
        if d.textbbox((0, 0), trial, font=f)[2] > max_width and row:
            result.append(row)
            row = word
        else:
            row = trial
    if row: result.append(row)
    return result

def base_frame(info, idx):
    im = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    for y in range(H):
        a = y / H
        d.line((0, y, W, y), fill=(int(9+9*a), int(25+14*a), int(47+24*a)))
    # Forma de estúdio de notícias em perspectiva
    d.polygon([(0, 170),(W, 225),(W, 640),(0, 570)], fill=(14, 39, 61))
    d.polygon([(0, 230),(140, 285),(140, 612),(0, 560)], fill=(17, 57, 75))
    d.polygon([(W, 260),(400, 305),(400, 600),(W, 575)], fill=(16, 58, 75))
    for i in range(5):
        y=300 + i*56
        d.line((0,y,142,y+22),fill=(22,79,91), width=2)
        d.line((400,y+18,W,y-16),fill=(22,79,91),width=2)
    d.rounded_rectangle((14, 16, W-14, 94), radius=19, fill=(8, 20, 36), outline=(37,95,106),width=2)
    rr(d, (26, 28, 77, 79), 12, GOLD)
    d.text((36, 35), "B",font=BOLD33,fill=NAVY)
    d.text((90, 28), "BRENO NA PAUTA", font=BOLD26, fill=WHITE)
    d.text((90, 61), "NOTÍCIAS • ANÁLISE • CONTEXTO",font=font(11,True),fill=TEAL)
    rr(d, (14, 110, W-14, 227), 17, (9, 29, 47), (55, 103, 111), 2)
    d.text((28, 119), "● NO RADAR  /  "+info["kind"],font=BOLD16,fill=GOLD)
    titles=lines(d,info["title"],BOLD26,480)
    for i,line in enumerate(titles[:2]):
        d.text((28,151+i*32), line,font=BOLD26,fill=WHITE)
    # barras luminosas atrás do personagem
    d.rectangle((20, 250, 28, 678),fill=(61,155,156))
    d.rectangle((W-28, 250, W-20, 678),fill=(221,148,55))
    rr(d,(70,255, W-70,300),12,(18,60,77))
    center(d,265,"ESTÚDIO • EDIÇÃO 01", BOLD16,TEAL)
    # bancada
    d.ellipse((-80, 718, W+80, 806),fill=(10,35,53))
    rr(d,(14,750,W-14,842),20,(19,56,75),(61,121,136),3)
    d.rectangle((14,762, W-14,775),fill=(30,91,104))
    # rodapé informação que não se sobrepõe ao rosto
    rr(d,(14,853,W-14,945),13,(5,18,31),(65,102,122),2)
    color=GOLD if info["tag"]=="OPINIÃO" else TEAL
    rr(d,(24,861,136,885),8,color)
    d.text((31,865),info["tag"],font=font(12,True),fill=NAVY)
    d.text((149,864),info["source"],font=font(11,True),fill=(174,199,204))
    cap=lines(d,info["caption"],BOLD18,480)
    for i,line in enumerate(cap[:2]):
        center(d,890+i*25,line,BOLD18,WHITE,490)
    return im

def character(d, t, idx, volume):
    bob=round(2.2*math.sin(2*math.pi*0.9*t))
    j=1 if idx in (0,3,7,8) else 0
    wavev=9*math.sin(t*5.0)*(1 if j else .3)
    x,y=270,478+bob
    # ombros e casaco
    d.polygon([(177,y+112),(215,y+94),(x,y+111),(330,y+96),(378,y+116),(403,758),(138,758)],fill=(11,35,70))
    # braço direito com gesto
    d.line([(346,y+137),(385+wavev,y+200),(399+wavev,y+232-16*j)], fill=(9,30,59), width=43)
    d.ellipse((381+wavev,y+213-16*j,411+wavev,y+245-16*j),fill=(224,172,135),outline=(65,38,35),width=2)
    # braço esquerdo 
    d.line([(194,y+141),(165-wavev,y+209),(162-wavev,y+230)],fill=(9,30,59),width=42)
    d.ellipse((146-wavev,y+217,176-wavev,y+245),fill=(224,172,135),outline=(65,38,35),width=2)
    # camisa gola
    d.polygon([(233,y+107),(270,y+124),(310,y+105),(300,y+201),(243,y+201)],fill=(237,242,240))
    d.polygon([(220,y+108),(270,y+125),(240,y+177)],fill=(25,75,101))
    d.polygon([(319,y+107),(270,y+125),(303,y+180)],fill=(25,75,101))
    d.line((271,y+164,271,y+229),fill=GOLD,width=5)
    # pescoço e orelhas 
    d.rounded_rectangle((251,y+58,291,y+128),radius=14,fill=(220,166,133),outline=(80,49,44),width=2)
    d.ellipse((194,y-34,221,y+14), fill=(216,158,127),outline=(79,45,36), width=3)
    d.ellipse((319,y-34,347,y+14), fill=(216,158,127),outline=(79,45,36), width=3)
    # cabelos atrás do rosto
    d.ellipse((194,y-126,348,y+96),fill=(35,29,34))
    # cabeça e barba
    d.ellipse((206,y-99,336,y+103), fill=(226,172,136),outline=(70,45,39),width=4)
    d.pieslice((207,y-37,335,y+108),0,180,fill=(68,49,44))
    d.ellipse((221,y-51,321,y+69),fill=(226,172,136))
    # topete
    d.polygon([(204,y-71),(208,y-115),(238,y-131),(260,y-126),(288,y-139),(323,y-116),(334,y-72),
              (317,y-96),(301,y-87),(275,y-106),(245,y-89),(214,y-80)], fill=(34,30,35))
    # olhos e sobrancelhas
    blink = (t % 4.2) < 0.13
    for xx in (244,294):
        d.line((xx-14,y-20,xx+11,y-23),fill=(51,37,35),width=5)
        if blink:
            d.line((xx-9,y-5,xx+9,y-5),fill=(49,37,34),width=3)
        else:
            d.ellipse((xx-10,y-11,xx+9,y+1),fill=(249,246,230))
            d.ellipse((xx-2,y-9,xx+5,y+1),fill=(31,49,55))
    # óculos e ponte
    for xx in (242,291):
        d.rounded_rectangle((xx-24,y-23,xx+23,y+19),radius=11,outline=(25,59,70),width=5)
    d.line((264,y-4,269,y-4),fill=(25,59,70),width=4)
    d.line((218,y-13,203,y-20),fill=(25,59,70),width=4)
    d.line((315,y-13,333,y-23),fill=(25,59,70),width=4)
    # nariz
    d.line((270,y+0,265,y+22,274,y+25),fill=(141,91,75),width=3)
    # boca com lip sync aproximado, vinculada ao RMS da narração
    mouth=max(3,min(17,int(4+volume*19)))
    d.ellipse((247,y+49,294,y+52+mouth),fill=(76,34,37),outline=(116,68,61),width=2)
    if mouth>6: d.arc((253,y+54,288,y+62),180,360,fill=(244,242,234),width=3)
    # brinco? não. reflexo no óculos
    d.line((221,y-16,236,y-20),fill=(109,168,171),width=2)

def render():
    text_file=OUT/"narracao.txt"
    text_file.write_text("\n".join(x["fala"] for x in NEWS)+"\n",encoding="utf8")
    wav=OUT/"breno-voz.wav"
    segfile=OUT/"segmentos.json"
    subprocess.run([sys.executable,str(ROOT/"motor"/"gerar_voz_kokoro.py"),
        str(text_file),"--voz","pm_alex","--speed","1.04","--gap","0.35",
        "--out",str(wav),"--seg-json",str(segfile)],check=True)
    segs=json.loads(segfile.read_text(encoding="utf8"))
    with wave.open(str(wav),"rb") as f:
        sr=f.getframerate()
        samples=np.frombuffer(f.readframes(f.getnframes()),dtype=np.int16)
    duration=float(segs[-1]["fim"])+0.3
    meta={"id":"breno-na-pauta-piloto-20261024","fps":FPS,"width":1080,"height":1920,"voice":"kokoro pm_alex",
          "duration_seconds":round(duration,2),"segments":segs,"sources":[
          "https://noticias.uol.com.br/eleicoes/2026/10/24/propostas-lula-e-flavio-bolsonaro-debate.ghtm",
          "https://agenciabrasil.ebc.com.br/justica/noticia/2026-10/tse-da-24-horas-para-meta-dar-informacoes-sobre-igualdade-de-campanhas"],
          "editorial":"Perspectiva conservadora explícita; fatos separados de opinião",
          "auto_publish":False}
    (OUT/"piloto.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf8")
    static=[base_frame(n,i) for i,n in enumerate(NEWS)]
    cmd=["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y","-f","rawvideo",
         "-pixel_format","rgb24","-video_size",f"{W}x{H}","-framerate",str(FPS),"-i","pipe:0",
         "-i",str(wav),"-vf","scale=1080:1920:flags=lanczos,format=yuv420p",
         "-c:v","libx264","-preset","veryfast","-crf","24","-r",str(FPS),
         "-c:a","aac","-b:a","160k","-movflags","+faststart","-shortest",
         str(OUT/"breno-na-pauta-piloto-20261024.mp4")]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        si=0
        total=math.ceil(duration*FPS)
        for fn in range(total):
            t=fn/FPS
            while si<len(segs)-1 and t>float(segs[si]["fim"]):si+=1
            im=static[si].copy()
            d=ImageDraw.Draw(im)
            s=segs[si]
            start=float(s["ini"])
            last=float(s.get("fim_fala",s["fim"]))
            if start <= t < last:
                center_sample=int(t*sr)
                a=samples[max(0,center_sample-1800):center_sample+1800]
                vol= min(1.0,float(np.sqrt(np.mean(a.astype("float32")**2)))/5300) if len(a) else 0.0
            else:vol=0.0
            character(d,t,si,vol)
            # barra de avanço no rodapé e marcador de trecho
            d.rectangle((28,831,512,835),fill=(45,76,87))
            d.rectangle((28,831,28+round(484*min(1,t/duration)),835),fill=GOLD)
            # número do bloco e selo animado
            d.rounded_rectangle((422,684,507,722),radius=10,fill=(13,33,53),outline=(71,141,145),width=2)
            d.text((431,694),f"{si+1:02d} / {len(NEWS):02d}",font=BOLD16,fill=GOLD)
            p.stdin.write(im.tobytes())
            if fn%350==0:print(f"frame {fn}/{total} ({t:.1f}s)",flush=True)
        p.stdin.close()
        rc=p.wait(timeout=180)
        if rc!=0:raise RuntimeError(f"ffmpeg retornou {rc}")
    except Exception:
        p.kill()
        raise
    mp4=OUT/"breno-na-pauta-piloto-20261024.mp4"
    assert mp4.is_file() and mp4.stat().st_size>200000, "arquivo MP4 inválido"
    print("OK",str(mp4),"bytes",mp4.stat().st_size,flush=True)

if __name__=="__main__":render()
