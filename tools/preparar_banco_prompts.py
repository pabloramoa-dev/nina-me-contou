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

MANUAIS = ROOT/'motor'/'prompts_episodios'
# Estilo em inglês: o FLUX.1-schnell da SiliconFlow segue inglês muito melhor
# do que português. Nenhum texto do roteiro em PT vai para a imagem.
STYLE_EN = ('Style: modern editorial comic-magazine illustration, colorful 2D digital art, clean '
            'rounded outlines, expressive faces, cinematic framing, full illustrated background, '
            'horizontal composition, subject centered with safe margins, warm palette of coral, '
            'gold, teal and cream. Fictional adults only. ')
NEGATIVO_EN = (' No text, no letters, no words, no captions, no speech bubbles, no numbers, '
               'no logos, no watermark, no frame or border, no collage, single scene. '
               'No nudity, no sexual content, no gore, no graphic violence. Not a photo, not anime.')
SHOTS_EN = ['Wide establishing shot', 'Medium shot', 'Close-up on the main reaction',
            'Side angle on the action', 'Over-the-shoulder shot', 'Detail shot of the key object or gesture',
            'Three-quarter medium shot', 'Expressive close-up', 'Group shot of the resolution',
            'Final shot of the outcome']


def carregar_manual(ep_id):
    arq = MANUAIS/f'{ep_id}.json'
    if not arq.exists():
        return None
    dados = json.loads(arq.read_text(encoding='utf-8'))
    if len(dados.get('cenas', [])) != 10:
        raise ValueError(f'{arq.name}: são exigidas 10 cenas manuais')
    return dados


def prompt_manual(dados, n):
    # A cena vem PRIMEIRO: o FLUX.1-schnell lê no máximo ~256 tokens; o que
    # passar disso é cortado. Assim o corte só atinge as restrições finais.
    cena = dados['cenas'][n].strip().rstrip('.')
    return ('Colorful 2D editorial comic illustration, no text. ' + SHOTS_EN[n] + ' (scene ' + str(n+1) + ' of 10): ' + cena + '. '
            + 'Characters, same look in every scene: ' + dados['personagens'].strip().rstrip('.') + '. '
            + 'Setting: ' + dados.get('cenario', '').strip().rstrip('.') + '. '
            + STYLE_EN + NEGATIVO_EN.strip())


PLANOS = ['Plano geral de apresentação', 'Plano médio dos personagens',
          'Close da reação principal', 'Enquadramento lateral da ação',
          'Plano sobre o ombro', 'Detalhe do gesto ou objeto citado',
          'Plano médio em três quartos', 'Close expressivo',
          'Plano conjunto da resolução', 'Plano final do desfecho']


def compilar(ep, manual=None):
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
        origem = 'compilado'
        if manual:
            prompt = prompt_manual(manual, n)
            origem = 'manual_en'
        if len(prompt)>2400: raise ValueError('Prompt longo')
        cenas.append({'scene':n,'beats':inds,'text':text,'ancora':anchor,'prompt':prompt,'origem':origem})
    return {'titulo':ep.get('titulo',''),'id':ep['id'],'cenas':cenas}


def preparar_ep(raw):
    try:
        antecipado = antecipar(raw)
    except ValueError:
        antecipado = raw
    return preparar_roteiro(garantir_cta(antecipado))


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
                manual = carregar_manual(ep['id']) if folder == 'episodios' else None
                rows[assinatura(ep)]=dict(compilar(ep, manual), arquivo=str(path.relative_to(ROOT)))
                fontes.append(str(path.relative_to(ROOT)))
            except ValueError as e:
                erros.append({'arquivo':str(path.relative_to(ROOT)),'erro':str(e)})
    BANCO.write_text(json.dumps({'versao':VERSAO,'roteiros':rows,'bloqueados':erros},ensure_ascii=False,indent=2)+'\n')
    manuais = sum(1 for r in rows.values() if r['cenas'][0].get('origem') == 'manual_en')
    print(json.dumps({'roteiros':len(rows),'prompts':10*len(rows),'manuais':manuais,'bloqueados':erros},ensure_ascii=False,indent=2))

if __name__=='__main__': main()
