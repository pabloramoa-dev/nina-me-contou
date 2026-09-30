"""Trilha e efeitos originais, discretos sob a voz; sem assets musicais externos."""
import numpy as np,soundfile as sf,json,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent;A=P/'assets';sr=48000
out=np.zeros(sr*60);rng=np.random.default_rng(91)
segs=json.loads((A/'segs.json').read_text())
def add(t,s):
 i=int(t*sr);n=min(len(s),len(out)-i)
 if n>0:out[i:i+n]+=s[:n]
for k,t0 in enumerate(np.arange(0,58,.6)):
 n=int(.22*sr);t=np.arange(n)/sr
 add(t0,.008*np.sin(2*np.pi*65*t)*np.exp(-t*25))
 if k%2:add(t0,.002*rng.normal(size=n)*np.exp(-t*38))
for k,t0 in enumerate(np.arange(0,58,2.4)):
 n=int(1.8*sr);t=np.arange(n)/sr
 notes=[220,261.63,329.63] if k%2 else [196,246.94,293.66]
 tone=sum(.003*np.sin(2*np.pi*f*t)*np.exp(-t*2.8) for f in notes)
 add(t0,tone)
for s in segs[1:]:
 n=int(.18*sr);t=np.arange(n)/sr
 add(s['ini'],.006*rng.normal(size=n)*np.sin(np.pi*t/.18)**2)
for s in (segs[0],segs[3]):
 for k,f in enumerate([880,1174]):
  n=int(.14*sr);t=np.arange(n)/sr
  add(s['ini']+.15+k*.14,.026*np.sin(2*np.pi*f*t)*np.exp(-t*25))
sf.write(A/'bed.wav',out,sr)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(A/'voz.wav'),'-i',str(A/'bed.wav'),'-filter_complex','[0:a][1:a]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.89:level=disabled[a]','-map','[a]','-ar','48000',str(A/'mix.wav')],check=True)
