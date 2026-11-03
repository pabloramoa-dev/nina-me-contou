#!/usr/bin/env python3
"""Compile os dez prompts de cada roteiro antes da produção, sem chamadas de API.

Reexecute após cadastrar/editar histórias. Revise prompts_banco.json no commit.
Não gera imagens, áudio nem publica vídeos.
"""
import json
import re
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'motor'))
from antecipacao import antecipar
from cta import garantir_cta, eh_cta
from visual_images import preparar_roteiro, STYLE
from prompts_banco import assinatura, BANCO, VERSAO

PLANOS = ['Plano geral de apresentação', 'Plano médio dos personagens',
          'Close da reação principal', 'Enquadramento lateral da ação',
          'Plano sobre o ombro', 'Detalhe do gesto ou objeto citado',
          'Plano médio em três quartos', 'Close expressivo',
          'Plano conjunto da resolução', 'Plano final do desfecho']


def compilar(ep):
    bats = ep['batidas']
    groups = [[i] for i in range(len(bats)) if not eh_cta(bats[i])]
    if len(groups) < 10:
        raise ValueError('Roteiro não comporta 10 cenas')
    while len(groups) > 10:
        j = min(range(len(groups)-1), key=lambda j: sum(len(bats[k]['fala'].split()) for k in groups[j]+groups[j+1]) + (10000 if j == 0 else 0))
        groups[j:j+2] = [groups[j]+groups[j+1]]
    groups[-1].extend(i for i,b in enumerate(bats) if eh_cta(b))
    cenas = []
    for n, inds in enumerate(groups):
        text = ' '.join(bats[i]['fala'] for i in inds)
        narrative = ' '.join(bats[i]['fala'] for i in inds if not eh_cta(bats[i]))
        # Texto específico da cena, nunca o título sozinho ou um resumo do final.
        sentences = re.split(r'(?<=[.!?])\s+', narrative)
        concrete = next((s for s in sentences if re.search(r'\b(?:abriu|viu|encontrou|entrou|chegou|entregou|mostrou|olhou|pegou|recebeu|perguntou|disse|foto|celular|porta|mesa|carro|recibo)\b', s, re.I)), sentences[0])
        anchor = ' '.join(concrete.split()[:8])
        # Âncora literal preserva pontuação e espaçamento da narração.
        anchor = concrete[:len(anchor)] if anchor not in narrative else anchor
        prompt = (STYLE + '\n'+PLANOS[n]+'. Cena '+str(n+1)+'/10. '
                  'Ação e personagens desta cena: '+concrete[:650]+
                  '\nRetrate o acontecimento narrado, com gesto e expressão compatíveis. '
                  'Mantenha aparência e roupas consistentes dos personagens recorrentes. '
                  'Se a fala for uma reflexão, mostre a reação dos envolvidos no ambiente já estabelecido, sem inventar provas ou eventos. '
                  'Nina é narradora fora de quadro. Não desenhe convites a seguir ou comentar. '
                  'Uma única cena, sem colagem nem revelação de acontecimentos posteriores.')
        if len(prompt)>2400: raise ValueError('Prompt longo')
        cenas.append({'scene':n,'beats':inds,'text':text,'ancora':anchor,'prompt':prompt})
    return {'titulo':ep.get('titulo',''),'id':ep['id'],'cenas':cenas}


def main():
    rows = {}; erros=[]; fontes=[]
    for folder in ('episodios','avulsos'):
        for path in sorted((ROOT/folder).glob('*.json')):
            raw=json.loads(path.read_text())
            try:
                try:
                    antecipado = antecipar(raw)
                except ValueError as exc:
                    # Arquivo legado já bloqueado pelo gancho: prepare os prompts,
                    # mas preserve o bloqueio de produção até a revisão do texto.
                    erros.append({'arquivo':str(path.relative_to(ROOT)),'erro':str(exc)})
                    antecipado = raw
                ep=preparar_roteiro(garantir_cta(antecipado))
                rows[assinatura(ep)]=dict(compilar(ep), arquivo=str(path.relative_to(ROOT)))
                fontes.append(str(path.relative_to(ROOT)))
            except ValueError as e:
                erros.append({'arquivo':str(path.relative_to(ROOT)),'erro':str(e)})
    BANCO.write_text(json.dumps({'versao':VERSAO,'roteiros':rows,'bloqueados':erros},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'roteiros':len(rows),'prompts':10*len(rows),'bloqueados':erros},ensure_ascii=False,indent=2))

if __name__=='__main__': main()
