"""Prompts pré-compilados do acervo: leitura e validação, sem API de texto."""
import hashlib
import json
from pathlib import Path

BANCO = Path(__file__).with_name('prompts_banco.json')
VERSAO = 'banco-historias-v1'


def assinatura(ep):
    dados = {'titulo': ep.get('titulo', ''), 'batidas': ep['batidas']}
    return hashlib.sha256(json.dumps(dados, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def carregar(ep):
    banco = json.loads(BANCO.read_text(encoding='utf-8'))
    item = banco['roteiros'].get(assinatura(ep))
    if item is None:
        raise ValueError('Roteiro sem prompts pré-cadastrados ou alterado: prepare o banco antes de renderizar')
    cenas = item['cenas']
    if len(cenas) != 10 or len({s['prompt'] for s in cenas}) != 10:
        raise ValueError('Banco deve conter exatamente 10 prompts distintos')
    indices = []
    for i, s in enumerate(cenas):
        if s['scene'] != i or not s['beats'] or not 90 <= len(s['prompt']) <= 2400:
            raise ValueError('Cena pré-cadastrada inválida')
        trecho = ' '.join(ep['batidas'][k]['fala'] for k in s['beats'])
        if s['text'] != trecho or s['ancora'] not in trecho or s['ancora'] not in s['prompt']:
            raise ValueError('Prompt não corresponde à cena do roteiro')
        indices.extend(s['beats'])
    if indices != list(range(len(ep['batidas']))):
        raise ValueError('Cenas não cobrem o roteiro em ordem')
    return item


def planejar(ep, segs):
    return [dict(s, start=segs[s['beats'][0]]['ini'], end=segs[s['beats'][-1]]['fim'])
            for s in carregar(ep)['cenas']]


def preparar(ep, cenas, pasta):
    item = carregar(ep)
    if [(s['beats'], s['text']) for s in cenas] != [(s['beats'], s['text']) for s in item['cenas']]:
        raise ValueError('Divisão de cenas divergente do banco')
    meta = {'modo': 'banco_historias', 'cenas': 10, 'versao': VERSAO,
            'hash': assinatura(ep), 'modelo': None, 'provedor': 'banco_local'}
    for cena, salva in zip(cenas, item['cenas']):
        cena.update(prompt=salva['prompt'], storyboard_mode=meta['modo'], storyboard_version=VERSAO)
    doc = dict(meta, quantidade=10, prompts=[s['prompt'] for s in cenas], plano=item)
    (Path(pasta)/'prompts_planejados.json').write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding='utf-8')
    return cenas, meta
