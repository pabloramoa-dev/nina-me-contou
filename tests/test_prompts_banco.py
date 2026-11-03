import copy
import json
import sys
from pathlib import Path
from unittest.mock import patch
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'motor'))
import prompts_banco as B
import visual_images as V
import storyboard_prompts as S
from antecipacao import antecipar
from cta import garantir_cta


def prepared(path):
    raw = json.loads(path.read_text())
    try:
        raw = antecipar(raw)
    except ValueError:
        pass  # Gancho legado continua bloqueado em produzir.py.
    return V.preparar_roteiro(garantir_cta(raw))


def test_acervo_completo_e_prompts_validos(monkeypatch):
    monkeypatch.setenv('NINA_REQUIRE_STORED_PROMPTS', '1')
    files = sorted((ROOT/'episodios').glob('*.json')) + sorted((ROOT/'avulsos').glob('*.json'))
    assert len(files) == 369
    for path in files:
        ep = prepared(path)
        item = B.carregar(ep)
        assert len(item['cenas']) == 10
        for s in item['cenas']:
            assert s['ancora'] in s['prompt']


def test_sem_chamada_de_modelo_textual_e_tempos_reais(tmp_path, monkeypatch):
    monkeypatch.setenv('NINA_REQUIRE_STORED_PROMPTS', '1')
    ep = prepared(ROOT/'episodios/ep182.json')
    segs = [{'ini': i*7.3, 'fim': (i+1)*7.3} for i in range(len(ep['batidas']))]
    with patch.object(S, '_pedir_plano', side_effect=AssertionError('API de texto proibida')):
        scenes = V.planejar(ep, segs)
        result, meta = S.preparar(ep, scenes, tmp_path, V.STYLE)
    assert meta['modo'] == 'banco_historias'
    assert result[0]['start'] == 0
    assert result[-1]['end'] == segs[-1]['fim']
    assert json.loads((tmp_path/'prompts_planejados.json').read_text())['quantidade'] == 10


def test_roteiro_alterado_bloqueia_antes_da_api(tmp_path, monkeypatch):
    monkeypatch.setenv('NINA_REQUIRE_STORED_PROMPTS', '1')
    ep = prepared(ROOT/'episodios/ep182.json')
    ep['batidas'][3]['fala'] += ' Uma mudança no roteiro.'
    with patch.object(V, 'gerar', side_effect=AssertionError('Não cobrar')) as gen:
        with pytest.raises(ValueError, match='alterado'):
            V.preparar(ep, [], tmp_path/'assets', tmp_path)
        gen.assert_not_called()


def test_cena_corrompida_bloqueia(monkeypatch, tmp_path):
    monkeypatch.setenv('NINA_REQUIRE_STORED_PROMPTS', '1')
    ep = prepared(ROOT/'episodios/ep182.json')
    item = copy.deepcopy(B.carregar(ep))
    item['cenas'][3]['ancora'] = 'acontecimento inventado'
    path = tmp_path/'banco.json'
    path.write_text(json.dumps({'roteiros': {B.assinatura(ep): item}}))
    monkeypatch.setattr(B, 'BANCO', path)
    with pytest.raises(ValueError, match='corresponde'):
        B.carregar(ep)


def test_dez_imagens_e_procedencia_preservada(tmp_path, monkeypatch):
    import io
    from PIL import Image
    from siliconflow_policy import validar_relatorio
    monkeypatch.setenv('NINA_REQUIRE_STORED_PROMPTS', '1')
    ep = prepared(ROOT/'episodios/ep182.json')
    segs = [{'ini':i*6, 'fim':(i+1)*6} for i in range(len(ep['batidas']))]
    buf=io.BytesIO()
    Image.new('RGB', (768,512), 'coral').save(buf,format='PNG')
    with patch.object(S, '_pedir_plano', side_effect=AssertionError('Sem modelo de texto')):
        with patch.object(V, 'gerar', return_value=buf.getvalue()) as gerar:
            mapping, report = V.preparar(ep,segs,tmp_path/'assets',tmp_path)
    assert gerar.call_count == 10
    assert len({call.args[0] for call in gerar.call_args_list}) == 10
    assert len(mapping) == len(ep['batidas'])
    assert validar_relatorio(report) == 10
