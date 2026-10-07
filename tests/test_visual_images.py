import io
import json
import sys
from pathlib import Path
import pytest
from PIL import Image

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'motor'))
import visual_images as V
import hyperframes as H

def episode(n=9):
    ep={'id':'visual-test','titulo':'UM TÍTULO','batidas':[
        {'fala':f'A personagem encontrou um objeto diferente na cena {i}.',
         'arte':['conversa','ESTE TEXTO NÃO PODE APARECER ATRÁS DA IMAGEM']} for i in range(n)]}
    segs=[{'i':i,'ini':i*4,'fim':i*4+4,'fim_fala':i*4+3.75} for i in range(n)]
    return ep,segs

def png(*args):
    b=io.BytesIO();Image.new('RGBA',(600,400),'coral').save(b,format='PNG');return b.getvalue()

def test_plan_covers_every_beat_once_and_matches_voice():
    ep,segs=episode();scenes=V.planejar(ep,segs)
    assert 4<=len(scenes)<=8
    assert [i for s in scenes for i in s['beats']]==list(range(9))
    assert scenes[0]['start']==0 and scenes[-1]['end']==36
    assert scenes[0]['beats']==[0] and scenes[-1]['beats']==[8]
    assert all(s['text'] in s['prompt'] for s in scenes)

def test_short_script_split_preserves_all_spoken_words():
    ep,_=episode(1);ep['batidas'][0]['fala']=' '.join(['Uma personagem conta uma história com início meio e fim.']*5)
    before=ep['batidas'][0]['fala'].split();out=V.preparar_roteiro(ep)
    assert len(out['batidas'])==4
    assert ' '.join(b['fala'] for b in out['batidas']).split()==before
    assert len(ep['batidas'])==1

def test_cache_invalidation_and_partial_failure(tmp_path):
    ep,segs=episode();calls=[]
    def generate(prompt,cfg):
        calls.append(prompt)
        if 'CENA ATUAL 2/' in prompt:raise V.ImageFailure('image_http_500')
        return png()
    assets=tmp_path/'assets'
    images,report=V.preparar(ep,segs,assets,tmp_path,generator=generate)
    assert report['ready']==5 and report['fallbacks']==1
    assert report['scenes'][1]['mode']=='story_frame_text'
    assert all((assets/name).exists() for name in images.values())
    calls.clear();V.preparar(ep,segs,assets,tmp_path,generator=generate)
    assert len(calls)==1
    ep['batidas'][0]['fala']='Uma história nova com outro objeto.'
    calls.clear();V.preparar(ep,segs,assets,tmp_path,generator=generate)
    assert len(calls)==6

def test_missing_key_fallback_is_recorded(tmp_path,monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY',raising=False)
    ep,segs=episode();images,report=V.preparar(ep,segs,tmp_path/'assets',tmp_path)
    assert not images and report['fallbacks']==6
    assert all(s['error']=='missing_openai_api_key' for s in report['scenes'])

@pytest.mark.parametrize('visual',['v3','v4'])
def test_image_template_omits_inner_caption_and_keeps_single_bottom_caption(tmp_path,monkeypatch,visual):
    monkeypatch.setenv('NINA_VISUAL',visual)
    ep,segs=episode(4);ep['_visual_images']={i:f'visual-scene-{i:02d}.png' for i in range(4)}
    H.compor(ep,segs,tmp_path);doc=(tmp_path/'index.html').read_text()
    assert doc.count('data-template="story_frame_image"')==4
    assert 'ESTE TEXTO' not in doc and 'class="bubble"' not in doc
    assert 'class="note"' not in doc and 'class="banco"' not in doc
    assert doc.count('id="cap0_0"')==1 and 'UM TÍTULO' in doc
    assert doc.count('class="story-illustration"')==4

def test_disabled_no_requests_and_text_mode(tmp_path):
    ep,segs=episode(4);ep['visual_images']={'auto_visual_images':False}
    def no(*args):raise AssertionError('Must not generate')
    images,report=V.preparar(ep,segs,tmp_path/'assets',tmp_path,generator=no)
    assert not images and not report['scenes']
    H.compor(ep,segs,tmp_path)
    assert 'story_frame_text' in (tmp_path/'index.html').read_text()

def test_invalid_bounds_and_corrupt_image():
    with pytest.raises(ValueError):V.config({'visual_images':{'min_images':9}})
    with pytest.raises(Exception):V.validar_imagem(b'not a png')

def test_approved_assets_are_not_reported_as_generated(tmp_path):
    ep,segs=episode(4)
    ep['approved_visual_assets']=['visual_tests/assets/approved-0.webp']*4
    def no(*args):raise AssertionError('Approved fixture must not call the API')
    mapping,report=V.preparar(ep,segs,tmp_path/'assets',tmp_path,generator=no)
    assert len(mapping)==4 and report['ready']==4
    assert all(s['status']=='approved_asset' for s in report['scenes'])

def test_approved_asset_cannot_escape_repository(tmp_path):
    ep,segs=episode(4);ep['approved_visual_assets']=['../../etc/passwd']*4
    mapping,report=V.preparar(ep,segs,tmp_path/'assets',tmp_path)
    assert not mapping and report['fallbacks']==4
