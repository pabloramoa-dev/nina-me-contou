"""Reutiliza o áudio original do episódio; sem síntese ou conexões externas."""
import json,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent;A=P/'assets';R=P.parents[1]
ep=json.loads((R/'episodios/ep005-p1.json').read_text())
subprocess.run(['ffmpeg','-y','-v','error','-i',str(R/'reels/ep005-p1.mp4'),'-vn','-af','apad,atrim=duration=60',str(A/'voz.wav')],check=True)
ends=[3.61637,8.36701,13.0117,17.1868,21.725,26.4124,30.4595,34.2081,38.1703,41.5572,44.7717,48.6056,52.9516,57.25]
segs=[];ini=0
for i,(b,fim) in enumerate(zip(ep['batidas'],ends)):
 segs.append({'i':i,'texto':b['fala'],'expr':b['expr'],'ini':ini,'fim':fim,'fim_fala':fim-.25})
 ini=fim
(A/'segs.json').write_text(json.dumps(segs,ensure_ascii=False,indent=2))
(P/'roteiro.txt').write_text('\n'.join(b['fala'] for b in ep['batidas'])+'\n')
subprocess.run(['python',str(R/'motor/lipsync_amplitude.py'),str(A/'voz.wav'),str(A/'lip.json'),'30'],check=True)
print('Áudio original Dora preservado; 60 segundos.')
