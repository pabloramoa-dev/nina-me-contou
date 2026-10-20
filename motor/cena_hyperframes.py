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
        puppet=os.environ.get('NINA_PUPPET_TEST','0').lower() in ('1','true','sim')
        if puppet:
            g=p['grupo']
            head=VGroup(*[g[j] for j in (0,1,2,3,12,13,14,15,16,17,18,19)])
            shoulder=p['braco_esq'].get_start().copy()
            g.remove(p['braco_esq'],p['mao_esq'])
            upper=Line(shoulder,shoulder+LEFT*.7+DOWN*.8,stroke_color=N.PT,stroke_width=15)
            fore=upper.copy()
            hand=VGroup(
                Ellipse(width=.30,height=.36,fill_color=N.PELE,fill_opacity=1,stroke_color=N.PT,stroke_width=4),
                Line([-.09,.07,0],[-.11,.43,0],stroke_color=N.PELE,stroke_width=12),
                Line([0,.09,0],[0,.49,0],stroke_color=N.PELE,stroke_width=12),
                Line([.09,.07,0],[.11,.39,0],stroke_color=N.PELE,stroke_width=11),
                Line([.12,-.06,0],[.29,.10,0],stroke_color=N.PELE,stroke_width=11))
            g.add(upper,fore,hand)
            originals=[part.copy() for part in g]
            pivot=p['cab'].get_center()+DOWN*1.6
            neck=p['cab'].get_center()+DOWN*1.4
            outline=g.copy()
            # Mark outline dynamic so Manim cannot cache its first pose.
            outline.add_updater(lambda mob,dt: None)
            self.add(outline,g)
        else:
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
            if puppet:
                # Restore bind pose: no cumulative rotation or stretching.
                for part,original in zip(m,originals):
                    part.become(original)
                expr=bats[i].get('expr','neutra')
                if expr not in N.EXPRESSOES:expr='neutra'
                p['rosto'].become(N.rosto_alinhado(p,expr))
                p['expr']=expr
                local=t-SEGS[i]['ini']
                span=SEGS[i]['fim']-SEGS[i]['ini']
                ramp=max(0.,min(1.,local/.45,(span-local)/.45))
                ramp=ramp*ramp*(3-2*ramp)
                sign=1 if i%2==0 else -1
                body_angle=sign*(2.8+1.2*math.sin(local*2.1))*DEGREES*ramp
                head_angle=sign*(7+2*math.sin(local*2.6))*DEGREES*ramp
                shift=np.array([sign*.18*ramp,.09*math.sin(local*2.8)*ramp,0])
                targets=[(-1.22,.35),(-.28,.62),(-1.35,-.20),
                         (-.72,.90),(-1.42,.05),(-1.10,.48),(-1.28,.20)]
                tx,ty=targets[i%len(targets)]
                rest=np.array([-.42,-1.56,0])
                target=rest*(1-ramp)+np.array([tx,ty,0])*ramp
                target+=np.array([.09*math.sin(local*3),.10*math.sin(local*3.6),0])*ramp
                wrist=shoulder+target
                # Two-bone IK preserves upper-arm and forearm lengths.
                delta=wrist-shoulder
                dist=min(np.linalg.norm(delta),2.68)
                unit=delta/max(np.linalg.norm(delta),.001)
                L1,L2=1.35,1.35
                along=(L1*L1-L2*L2+dist*dist)/(2*max(dist,.001))
                elbow=shoulder+unit*along+np.array([-unit[1],unit[0],0])*math.sqrt(max(0,L1*L1-along*along))
                upper.put_start_and_end_on(shoulder,elbow)
                fore.put_start_and_end_on(elbow,wrist)
                hand.move_to(wrist).rotate(sign*.22*ramp)
                head.rotate(head_angle,about_point=neck)
                m.rotate(body_angle,about_point=pivot).shift(shift)
                p['head_angle']=head_angle+body_angle
                gaze=.065*math.sin(local*1.6)
                for eye in p['rosto'][0]:
                    offset=eye[0].get_center()+np.array([gaze,0,0])*p['escala']-eye[1].get_center()
                    for part in (eye[1],eye[2],eye[3]):part.shift(offset)
                # Outline follows the actual silhouette, not a static arm.
                outline.become(m.copy().clear_updaters())
                for part in outline.family_members_with_points():
                    part.set_stroke('#fbf8f0',width=part.get_stroke_width()+16,opacity=1)
                    if part.get_fill_opacity()>0:part.set_fill('#fbf8f0',opacity=1)
            else:
                if i!=state['i']:
                    expr=bats[i].get('expr','neutra')
                    if expr not in N.EXPRESSOES:expr='neutra'
                    p['rosto'].become(N.rosto_alinhado(p,expr))
                    p['expr']=expr;state['i']=i
                m.move_to(home+np.array([.045*np.sin(t*1.4),.035*np.sin(t*2.1),0]))
            if ligado and not puppet:
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
