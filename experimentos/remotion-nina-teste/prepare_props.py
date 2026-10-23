#!/usr/bin/env python3
"""Gera metadados do vídeo Remotion a partir do roteiro e dos tempos reais da voz."""
import json, math, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
EPID='nina-remotion-demo-20261023'
ep=json.loads((ROOT.parent.parent/'saida'/EPID/'ep.json').read_text(encoding='utf-8'))
segs=json.loads((ROOT.parent.parent/'saida'/EPID/'segs.json').read_text(encoding='utf-8'))
mp4=ROOT/'public'/'nina-base.mp4'
meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(mp4)]))
duration=float(meta['format']['duration'])
scenes=[]
for seg in segs:
 i=int(seg['i'])
 b=ep['batidas'][i]
 art=b.get('arte') or []
 title=(b.get('tela') or (art[1] if len(art)>1 else '') or b['fala'][:45]).strip()
 scenes.append({'start':float(seg.get('inicio',seg.get('start',0))),
                'end':float(seg.get('fim',seg.get('end',duration))),
                'title':title,
                'fala':b['fala'],
                'expr':b.get('expr','neutra')})
props={'durationFrames':math.ceil(duration*30),'scenes':scenes}
(ROOT/'props.json').write_text(json.dumps(props,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'{duration:.2f}s • {len(scenes)} cenas • {props["durationFrames"]} quadros • voz oficial')
