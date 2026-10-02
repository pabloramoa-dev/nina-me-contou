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

def test_sfx_follow_animation_events():
    import numpy as np, sfx as S
    ep,segs=fixture();ep['batidas'][0].update(expr='chocada',zoom=True)
    ev=S.eventos(ep,segs);nomes=[n for _,n,_ in ev]
    assert 'impacto' in nomes and 'whoosh_grave' in nomes and 'digitando' in nomes and nomes[-1]=='brilho'
    assert all(0<=t<=8.2 for t,_,_ in ev)
    pista=S.trilha_sfx(ep,segs,8.2)
    assert len(pista)==int(np.ceil(8.2*S.SR)) and 0<np.abs(pista).max()<.5
    for nome,f in S.SONS.items():
        x=f();assert len(x)>100 and np.isfinite(x).all() and abs(np.abs(x).max()-1)<1e-6,nome

def test_flash_only_on_shock(tmp_path,monkeypatch):
    monkeypatch.setenv('NINA_VISUAL','v3')
    ep,segs=fixture();H.compor(ep,segs,tmp_path);s=(tmp_path/'index.html').read_text()
    assert 'id="flash"' in s and 'tl.fromTo("#flash"' not in s
    ep['batidas'][1]['expr']='chocada';H.compor(ep,segs,tmp_path);s=(tmp_path/'index.html').read_text()
    assert 'tl.fromTo("#flash"' in s and 'scale:1.08' in s

def test_voice_master_keeps_length(tmp_path):
    import numpy as np, soundfile as sf, audio_fx
    sr=44100;t=np.arange(sr*2)/sr;x=.3*np.sin(2*np.pi*220*t)*(t<1.2)
    sf.write(tmp_path/'b.wav',x,sr,subtype='PCM_16')
    audio_fx.masterizar_voz(tmp_path/'b.wav',tmp_path/'v.wav')
    y,sr2=sf.read(tmp_path/'v.wav');info=sf.info(tmp_path/'v.wav')
    assert sr2==sr and len(y)==len(x) and info.channels==1 and info.subtype=='PCM_16' and np.abs(y).max()<=.9
    g=audio_fx.ducking(y,sr);assert g[int(.6*sr)]<.5 and g[-1]>.85

def test_v4_visual_escapes_and_highlights(tmp_path,monkeypatch):
    import visual_v4 as V
    monkeypatch.setenv('NINA_VISUAL','v4')
    ep,segs=fixture();ep['batidas'][1]['fala']='<b>traição</b> & a amante, sim'
    ep['batidas'][1]['expr']='chocada'
    H.compor(ep,segs,tmp_path);s=(tmp_path/'index.html').read_text()
    assert 'class="v4"' in s and 'class="pill"' in s and 'class="marker"' in s and '<b>' not in s
    assert 'class="kw"' in s and 'keyframes' in s and 'clipPath' in s
    assert V.palavras_chave({'fala':'x','hf':{'destaque':['Paula']}},['A','Paula.','foi'])=={1}

def test_rhubarb_falls_back_to_amplitude(tmp_path,monkeypatch):
    import numpy as np,soundfile as sf,subprocess,sys as _s
    monkeypatch.setenv('RHUBARB_BIN','/nao/existe');monkeypatch.setenv('PATH','/usr/bin:/bin')
    sr=44100;t=np.arange(sr)/sr;sf.write(tmp_path/'v.wav',.3*np.sin(2*np.pi*200*t),sr)
    import os;env=dict(os.environ,HOME=str(tmp_path))
    r=subprocess.run([_s.executable,str(ROOT/'motor/lipsync_rhubarb.py'),str(tmp_path/'v.wav'),str(tmp_path/'l.json'),'30'],env=env,capture_output=True,text=True)
    assert r.returncode==0 and 'amplitude' in r.stdout and json.loads((tmp_path/'l.json').read_text())

def test_phoneme_mouths_exist():
    pytest.importorskip('manim')
    import nina_lib as N
    for l in 'ABCDEFGH':assert N.boca_fala(l) is not None
