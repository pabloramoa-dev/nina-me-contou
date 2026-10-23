"""Gera e publica um carrossel por dia, sem tocar no pipeline de Reels.

As 7 imagens são feitas em CPU (Pillow) e incluem o retrato da Nina
gerado pelo Manim do próprio repositório. Nunca usa imagem paga nem GPU.
"""
from __future__ import annotations
import argparse
from datetime import date,datetime
import json
import os
from pathlib import Path
import subprocess
import time
from zoneinfo import ZoneInfo

from PIL import Image,ImageDraw,ImageFont
import requests

ROOT=Path(__file__).resolve().parents[1]
TZ=ZoneInfo("America/Sao_Paulo")
INICIO=date(2026,10,23)
CARROSSEIS=ROOT/"carrosseis"
REGISTRO=ROOT/"conteudo"/"carrosseis_publicados.json"
CORES=["#ffe9dc","#fff1d4","#e8f6f4","#f8e9fb","#ffecec","#fff6de","#f5e9e7"]
ROSA,TINTA="#ed256b","#241b2c"
FONT_BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
W,H=1080,1350

def ler(path,padrao):
    return json.loads(path.read_text("utf-8")) if path.exists() else padrao

def salvar(path,objeto):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(objeto,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def historia(dia:date):
    idade=(dia-INICIO).days
    if idade<0:raise ValueError("Data anterior ao primeiro carrossel")
    if idade==0:
        textos=[
            ("Ela achava que o marido escondia algo...","E estava certa! Mas ninguém imaginava o que era.","heart"),
            ("Toda sexta-feira...","Ele saía mais cedo do trabalho e não dizia para onde ia.","clock"),
            ("Uma amiga viu tudo!","Ela viu o marido entrando numa loja e mandou uma mensagem.","message"),
            ("Ela decidiu segui-lo.","Dessa vez, queria descobrir pessoalmente o que estava acontecendo.","car"),
            ("A porta se abriu...","Ela entrou na loja e encontrou algo que não esperava!","door"),
            ("A surpresa era outra!","O marido estava aprendendo a fazer bolos em uma aula de confeitaria.","gift"),
            ("Era por um sonho lindo!","Ele queria ajudar a esposa a abrir a própria confeitaria. Você teria desconfiado?","heart"),
        ]
    else:
        # Reserva de histórias independente: não consome a fila de Reels.
        from motor.gerar_roteiros import gerar_um
        p1,p2=gerar_um(10000+idade,2000+idade)
        b1,b2=p1["batidas"],p2["batidas"]
        textos=[
            ("Nina me contou...",b1[0]["fala"],"question"),
            ("Tudo começou assim:",b1[1]["fala"]+" "+b1[2]["fala"],"message"),
            ("Uma pista estranha...",b1[4]["fala"]+" "+b1[5]["fala"],"magnifier"),
            ("A história não fechava!",b1[6]["fala"],"letter"),
            ("E surgiu outro nome...",b1[7]["fala"]+" "+b1[8]["fala"],"phone"),
            ("A verdade veio à tona!",b2[3]["fala"]+" "+b2[5]["fala"],"door"),
            ("E agora, o que você faria?",b2[11]["fala"],"heart"),
        ]
    return [{"numero":i+1,"titulo":titulo,"texto":texto,"icone":icone}
            for i,(titulo,texto,icone) in enumerate(textos)]

def fonte(tamanho,bold=True):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG,tamanho)

def linhas(draw,texto,ft,largura):
    resultado,atual=[],""
    for palavra in texto.split():
        teste=(atual+" "+palavra).strip()
        if not atual or draw.textbbox((0,0),teste,font=ft)[2]<=largura:atual=teste
        else:resultado.append(atual);atual=palavra
    if atual:resultado.append(atual)
    return resultado

def encaixar(draw,texto,largura,altura,grande=56,minimo=27,espaco=8):
    for t in range(grande,minimo-1,-2):
        ft=fonte(t)
        ls=linhas(draw,texto,ft,largura)
        passo=t+espaco
        if len(ls)*passo<=altura:return ft,ls,passo
    raise ValueError("Texto muito longo para arte: "+texto[:100])

def slide(item,i,retrato,destino):
    from motor.local_story_art import icon
    bg=Image.new("RGB",(W,H),CORES[i%len(CORES)])
    d=ImageDraw.Draw(bg)
    d.rounded_rectangle((40,36,1040,110),radius=25,fill=TINTA)
    d.text((75,51),"NINA ME CONTOU  •  HISTÓRIAS ILUSTRADAS",font=fonte(31),fill="white")
    d.rounded_rectangle((925,47,1020,99),radius=16,fill=ROSA)
    d.text((943,54),f"{i+1}/7",font=fonte(27),fill="white")
    ft,ls,passo=encaixar(d,item["titulo"],940,155,64,40)
    for j,l in enumerate(ls):d.text((70,150+j*passo),l,font=ft,fill=TINTA)
    d.rounded_rectangle((62,335,1018,922),radius=45,fill="#fffdf8",outline="#f2ccc9",width=7)
    figura=icon(item["icone"]).resize((490,490),Image.Resampling.LANCZOS)
    pos_fig=(497,377) if i%2 else (81,377)
    pos_avatar=(93,420) if i%2 else (615,420)
    bg.paste(figura,pos_fig,figura)
    tamanho=325
    avatar=retrato.resize((tamanho,tamanho),Image.Resampling.LANCZOS)
    mascara=Image.new("L",(tamanho,tamanho))
    ImageDraw.Draw(mascara).ellipse((0,0,tamanho-1,tamanho-1),fill=255)
    d.ellipse((pos_avatar[0]-9,pos_avatar[1]-9,pos_avatar[0]+tamanho+9,pos_avatar[1]+tamanho+9),fill=ROSA)
    bg.paste(avatar,pos_avatar,mascara)
    d=ImageDraw.Draw(bg)
    d.rounded_rectangle((62,947,1018,1284),radius=34,fill="white")
    texto=item["texto"]
    if i==6:
        texto=texto.replace(" Me conta nos comentários.","")
        d.rounded_rectangle((78,1170,1002,1270),radius=25,fill=ROSA)
    ft,ls,passo=encaixar(d,texto,855,190 if i==6 else 265,45,27,11)
    for j,l in enumerate(ls):d.text((112,982+j*passo),l,font=ft,fill=TINTA)
    if i==6:
        chamada="CONTA PRA NINA NOS COMENTÁRIOS!"
        ft,ls,passo=encaixar(d,chamada,875,70,34,26)
        for j,l in enumerate(ls):d.text((112,1194+j*passo),l,font=ft,fill="white")
    else:d.text((735,1305),"DESLIZE  →",font=fonte(22),fill=ROSA)
    destino.parent.mkdir(parents=True,exist_ok=True)
    bg.save(destino,quality=88,optimize=True,subsampling=0)

def preparar(dia,avatar,destino):
    if not avatar.exists():raise FileNotFoundError("Retrato original da Nina ausente: "+str(avatar))
    itens=historia(dia)
    with Image.open(avatar) as im:retrato=im.convert("RGB")
    destino.mkdir(parents=True,exist_ok=True)
    for i,item in enumerate(itens):slide(item,i,retrato,destino/f"{i+1:02d}.jpg")
    legenda=(f"✨ NINA ME CONTOU — {dia:%d/%m/%Y}\n\n"+
             itens[0]["titulo"]+" "+itens[0]["texto"]+
             "\n\nArrasta até a última imagem para descobrir o final. "+
             "Depois me conta: o que você teria feito? 👇\n\n"+
             "História de ficção criada para entretenimento.\n\n"+
             "#NinaMeContou #Carrossel #Storytime #Fofoca #HistoriasIlustradas")
    salvar(destino/"conteudo.json",{"data":dia.isoformat(),"legenda":legenda,"slides":itens})
    return itens

def persistir(paths,mensagem):
    """Registra pendências ANTES do media_publish, para evitar posts duplicados."""
    subprocess.run(["git","config","user.name","nina-carrossel-bot"],cwd=ROOT,check=True)
    subprocess.run(["git","config","user.email","actions@github.com"],cwd=ROOT,check=True)
    subprocess.run(["git","add","--",*paths],cwd=ROOT,check=True)
    if subprocess.run(["git","diff","--cached","--quiet"],cwd=ROOT).returncode==0:return
    subprocess.run(["git","commit","-m",mensagem+" [skip ci]"],cwd=ROOT,check=True)
    for n in range(5):
        if subprocess.run(["git","pull","--rebase","origin","main"],cwd=ROOT).returncode!=0:
            raise RuntimeError("Conflito no Git; envio interrompido com segurança")
        if subprocess.run(["git","push","origin","HEAD:main"],cwd=ROOT).returncode==0:return
        time.sleep(3*(n+1))
    raise RuntimeError("Não foi possível persistir o estado no GitHub")

def preparar_e_subir(dia,avatar,dry_run):
    destino=(ROOT/"output"/"carrossel-teste") if dry_run else CARROSSEIS/dia.strftime("%Y%m%d")
    preparar(dia,avatar,destino)
    print(json.dumps({"preparado":True,"ensaio":dry_run,"imagens":7,"pasta":str(destino.relative_to(ROOT))},ensure_ascii=False))
    if not dry_run:
        persistir([str(destino.relative_to(ROOT))],f"carrossel: imagens {dia.isoformat()}")

def publicar(dia):
    from src import config
    from src.instagram import Publicador
    from tools.channel_ops import resume_send,pending_send,confirm_send
    cfg=config.carregar(exigir_credenciais=True)
    if cfg.dry_run or not cfg.publicar_ativo:
        raise RuntimeError("Instagram não habilitado: DRY_RUN ou PUBLICAR_ATIVO desligado")
    chave=dia.strftime("%Y%m%d")
    ident="carrossel-"+chave
    pasta=CARROSSEIS/chave
    doc=ler(pasta/"conteudo.json",None)
    if not doc or len(doc.get("slides",[]))!=7:raise RuntimeError("Carrossel incompleto ou ausente")
    feitos=ler(REGISTRO,{})
    if chave in feitos:
        print("Já publicado:",feitos[chave]["media_id"]);return
    for i in range(1,8):
        if not (pasta/f"{i:02d}.jpg").exists():raise FileNotFoundError(f"Slide {i} ausente")
    pub=Publicador(cfg)
    conta=pub.conferir_conta()
    if (conta.get("username") or "").lower().lstrip("@")!="ninamecontou":
        raise RuntimeError("Credenciais não correspondem ao @ninamecontou")
    legenda=doc["legenda"]
    media_id=resume_send(ROOT,ident,lambda cid:pub.reconciliar(cid,legenda))
    if not media_id:
        urls=[f"{cfg.raw_base_url}/carrosseis/{chave}/{i:02d}.jpg" for i in range(1,8)]
        for url in urls:
            for _ in range(10):
                try:
                    r=requests.get(url,timeout=20)
                    if r.status_code==200 and r.headers.get("content-type","").startswith("image/"):break
                except requests.RequestException:pass
                time.sleep(8)
            else:raise RuntimeError("URL pública indisponível: "+url)
        filhos=[]
        for url in urls:
            cid=pub.criar_item_carrossel(url)
            pub.aguardar_pronto(cid)
            filhos.append(cid)
        parent=pub.criar_container_carrossel(filhos,legenda)
        pub.aguardar_pronto(parent)
        pending_send(ROOT,ident,parent)
        persistir(["conteudo/send_receipts.json"],f"carrossel: pendente {chave}")
        try:media_id=pub.publicar(parent)
        except Exception:
            media_id=pub.reconciliar(parent,legenda)
            if not media_id:raise
        confirm_send(ROOT,ident,media_id)
    feitos[chave]={"media_id":media_id,"publicado_em":datetime.now(TZ).isoformat(timespec="seconds"),
                  "data":dia.isoformat(),"slides":7}
    salvar(REGISTRO,feitos)
    persistir(["conteudo/carrosseis_publicados.json","conteudo/send_receipts.json"],
             f"carrossel: publicado {chave}")
    print(json.dumps({"publicado":True,"data":dia.isoformat(),"media_id":media_id},ensure_ascii=False))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("acao",choices=["preparar","publicar"])
    ap.add_argument("--data",help="AAAA-MM-DD, padrão data de Brasília")
    ap.add_argument("--avatar",default="output/nina-carrossel-original.png")
    ap.add_argument("--dry-run",action="store_true")
    args=ap.parse_args()
    dia=date.fromisoformat(args.data) if args.data else datetime.now(TZ).date()
    if args.acao=="preparar":preparar_e_subir(dia,ROOT/args.avatar,args.dry_run)
    else:publicar(dia)

if __name__=="__main__":main()
