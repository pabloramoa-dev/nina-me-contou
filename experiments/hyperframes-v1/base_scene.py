"""Camada original da Nina para composição HyperFrames; teste isolado."""
import json, sys
from pathlib import Path
P = Path(__file__).resolve().parent
sys.path.insert(0, str(P.parents[1] / 'motor'))
from manim import *
import nina_lib as N
import dvh_vox_papel as V
config.frame_width=8
config.frame_height=14.222
config.pixel_width=720
config.pixel_height=1280
config.frame_rate=30
class NinaBase(Scene):
    def construct(self):
        V.estilo('papel')
        segs=json.loads((P/'assets/segs.json').read_text())
        cues=json.loads((P/'assets/lip.json').read_text())
        self.add(N.varanda('tarde')['grupo'])
        p=N.posicionar(N.nina('chocada','tarde'),escala=1.65,pos=np.array([0,-2.25,0]))
        V.colar(self,p,espessura=22)
        home=p['grupo'].get_center().copy()
        expressions=[s['expr'] for s in segs]
        state={'i':0}
        def motion(m,dt):
            t=self.renderer.time
            i=min(len(segs)-1,max([k for k,s in enumerate(segs) if s['ini']<=t] or [0]))
            if i!=state['i']:
                p['rosto'].become(N.rosto_alinhado(p,expressions[i]))
                p['expr']=expressions[i];state['i']=i
            m.move_to(home+np.array([.045*np.sin(t*1.4),.035*np.sin(t*2.1),0]))
        p['grupo'].add_updater(motion)
        N.animar_nina(self,p,cues)
        self.wait(60)
