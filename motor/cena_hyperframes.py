"""Personagem e artes originais sob a composição HyperFrames."""
import json,os,sys
from pathlib import Path
M=Path(__file__).resolve().parent
sys.path.insert(0,str(M))
from manim import *
import numpy as np
import math
import nina_lib as N
import direcao_nina as D
import dvh_vox_papel as V
import objetos as O
P=Path(os.environ['PASTA'])
EP=json.loads(Path(os.environ['EPISODIO']).read_text())
SEGS=json.loads((P/'segs.json').read_text())
config.frame_width=8
config.frame_height=2.9 if os.environ.get('NINA_RENDER_ARTS') else 14.222
config.pixel_width=960 if os.environ.get('NINA_RENDER_ARTS') else int(os.environ.get('NINA_HF_BASE_WIDTH','720'))
config.pixel_height=348 if os.environ.get('NINA_RENDER_ARTS') else round(config.pixel_width*16/9)
config.frame_rate=30

class NinaBase(Scene):
    def construct(self):
        V.estilo('papel')
        cues=json.loads((P/'lip.json').read_text())
        bats=EP['batidas'];cenario=EP.get('cenario','tarde')
        self.add(N.varanda(cenario)['grupo'])
        p=N.posicionar(N.nina(bats[0].get('expr','neutra'),cenario),escala=1.65,pos=np.array([0,-2.25,0]))
        V.colar(self,p,espessura=22)
        home=p['grupo'].get_center().copy();state={'i':0}
        inicio_braco=p['braco_esq'].get_start().copy()
        fim_braco=p['braco_esq'].get_end().copy()
        ligado=os.environ.get('NINA_DIRECAO','1') not in ('0','false','False')
        puppet=os.environ.get('NINA_PUPPET_TEST','0').lower() in ('1','true','sim')
        # Experimental only: preserve the original Nina art, voice and lip sync.
        # Pupils move inside existing eyes. No synthetic replacement character.
        plano=(json.loads((P/'direcao.json').read_text()) if (P/'direcao.json').is_file()
               else D.planejar(EP,SEGS)) if ligado else []
        def motion(m,dt):
            t=self.renderer.time
            i=max([k for k,s in enumerate(SEGS) if s['ini']<=t] or [0])
            if i!=state['i']:
                expr=bats[i].get('expr','neutra')
                if expr not in N.EXPRESSOES:expr='neutra'
                p['rosto'].become(N.rosto_alinhado(p,expr))
                p['expr']=expr;state['i']=i
            if puppet:
                # More expressive yet bounded sway / head-like nod, without stretching art.
                sway=.075*math.sin(t*1.2)+.028*math.sin(t*3.0)
                bob=.055*math.sin(t*2.4)
                m.move_to(home+np.array([sway,bob,0]))
                # Independent gaze uses the ORIGINAL iris, pupil and highlight objects.
                # Target is recomputed relative to each eye white every frame; no drift.
                gaze=.055*math.sin(t*.7)+.025*math.sin(t*1.9)
                glance_y=.018*math.sin(t*.95)
                for eye in p['rosto'][0]:
                    whites=eye[0]
                    iris=eye[1]
                    target=whites.get_center()+np.array([gaze,glance_y,0])*p['escala']
                    offset=target-iris.get_center()
                    for part in (eye[1],eye[2],eye[3]):
                        part.shift(offset)
            else:
                m.move_to(home+np.array([.045*np.sin(t*1.4),.035*np.sin(t*2.1),0]))
            if ligado:
                item=plano[i]
                dx,dy=D.deslocamento(item['gesto'],t,item['inicio'],item['fim'],item['energia'])
                shift=m.get_center()-home
                if puppet:
                    # Emphasise real articulated arm gestures (not camera/card motion).
                    dx=max(-.48,min(.48,dx*1.4))
                    dy=max(-.48,min(.48,dy*1.4))
                alvo=fim_braco+shift+np.array([dx,dy,0])*p['escala']
                p['braco_esq'].put_start_and_end_on(inicio_braco+shift,alvo)
                p['mao_esq'].move_to(alvo)
        p['grupo'].add_updater(motion)
        N.animar_nina(self,p,cues)
        self.wait(SEGS[-1]['fim']+2.2)

def _classe_arte(i):
    class Arte(Scene):
        def construct(self):
            V.estilo('papel');self.camera.background_color='#fff9ea'
            V.FONTE='DejaVu Sans'
            spec=EP['batidas'][i].get('arte')
            tipo=spec[0];arg=spec[1] if len(spec)>1 else None
            m=O.arte(tipo,arg)
            if m.width>7.3:m.scale(7.3/m.width)
            if m.height>2.6:m.scale(2.6/m.height)
            self.add(m.move_to(ORIGIN))
    Arte.__name__=f'Arte{i}'
    return Arte

for _i in range(len(EP['batidas'])):
    globals()[f'Arte{_i}']=_classe_arte(_i)
