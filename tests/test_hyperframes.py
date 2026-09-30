import json,sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'motor'))
import hyperframes as H
from cta import garantir_cta,eh_cta
from src import fila

def fixture():
    ep={'id':'teste','ep':7,'parte':2,'titulo':'UMA HISTÓRIA','cenario':'noite','fim':'SEGUE A NINA','batidas':[{'fala':'A Nina viu o carro.','expr':'neutra','arte':['carro']},{'fala':'Como você está?','expr':'ironica','arte':['conversa','Tudo bem?']}]}
    segs=[{'i':0,'ini':0,'fim':3,'fim_fala':2.75},{'i':1,'ini':3,'fim':6,'fim_fala':5.75}]
    return ep,segs

def test_all_text_escaped_and_content_driven(tmp_path):
    ep,segs=fixture();ep['batidas'][1]['fala']='<script>alert(1)</script> & sim'
    ep['batidas'][1]['arte'][1]='<img src=x onerror=alert(1)>'
    d=H.compor(ep,segs,tmp_path);s=(tmp_path/'index.html').read_text()
    assert d==8.2 and 'data-duration="8.2"' in s
    assert '<script>alert' not in s and '<img src=x' not in s
    assert '&lt;script&gt;' in s and '&lt;img' in s
    assert 'NA VARANDA' in s and 'O PORTÃO DA GARAGEM' not in s
    assert 'data-start="6"' in s and 'id="voice"' in s

@pytest.mark.parametrize('segments',[
    [{'i':0,'ini':0,'fim':1}],
    [{'i':0,'ini':0,'fim':3},{'i':1,'ini':2,'fim':6}],
    [{'i':0,'ini':0,'fim':float('nan')},{'i':1,'ini':3,'fim':6}],
])
def test_invalid_timeline_refuses_output(segments):
    ep,_=fixture()
    with pytest.raises(ValueError):H.validar_timeline(ep,segments)

def test_long_title_fits_with_real_font():
    title,size=H.bloco('Uma história muito longa sobre alguém que abriu uma porta e encontrou uma surpresa inesperada')
    from html import unescape
    ls=unescape(title).split('<br>')
    font=H.ImageFont.truetype(H.FONT,size)
    assert len(ls)*size*1.06<=128 and all(font.getlength(x)<=850 for x in ls)

def test_cta_only_final():
    ep,_=fixture();ep['batidas'].insert(0,{'fala':'Me segue antes!','arte':['seguir']})
    fixed=garantir_cta(ep)
    assert not any(eh_cta(b) for b in fixed['batidas'][:-1])
    assert eh_cta(fixed['batidas'][-1])
    assert ep['batidas'][0]['fala']=='Me segue antes!'

def test_queue_signature_includes_visual_version(tmp_path,monkeypatch):
    ep,_=fixture();epdir=tmp_path/'episodios';epdir.mkdir();reels=tmp_path/'reels';reels.mkdir()
    (epdir/'ep007-p2.json').write_text(json.dumps(ep))
    monkeypatch.setattr(fila.config,'EPISODIOS',epdir);monkeypatch.setattr(fila.config,'REELS',reels)
    monkeypatch.setenv('NINA_MOTOR','manim');old=fila.assinatura('ep007-p2')
    (reels/'ep007-p2.mp4').write_bytes(b'mp4');(reels/'ep007-p2.hash').write_text(old)
    assert not fila.desatualizado('ep007-p2')
    monkeypatch.delenv('NINA_MOTOR');assert fila.assinatura('ep007-p2')!=old and fila.desatualizado('ep007-p2')

def test_refuse_mp4_without_audio(monkeypatch):
    monkeypatch.setattr(H.subprocess,'check_output',lambda _:json.dumps({'streams':[{'codec_type':'video','width':1080,'height':1920,'avg_frame_rate':'30/1'}],'format':{'duration':'60'}}).encode())
    with pytest.raises(ValueError,match='áudio'):H.conferir('x.mp4',60)

def test_unknown_images_stay_explicit(tmp_path):
    ep,segs=fixture();ep['batidas'][0]['arte']=['imagem','assets/quiz.jpg.b64']
    H.compor(ep,segs,tmp_path)
    assert 'assets/arte0.png' in (tmp_path/'index.html').read_text()
