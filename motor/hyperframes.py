"""Composição de produção: visual aprovado, dados e artes do próprio roteiro."""
from __future__ import annotations
import base64,html,json,math,os,re,shutil,subprocess,sys
from pathlib import Path
import numpy as np
import soundfile as sf
from PIL import ImageFont
from hf_assets import ICONS
import audio_fx
import sfx as SFX
from render_version import HYPERFRAMES_VERSION

FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
TAIL=2.2
TEXT_TYPES={'titulo','seguir','manchete','manchete_v','carimbo','direct','conversa','notificacao'}

def sh(cmd,**kw):
    subprocess.run([str(x) for x in cmd],check=True,**kw)

def validar_timeline(ep,segs):
    if not ep.get('batidas') or len(ep['batidas'])!=len(segs):
        raise ValueError('Batidas e segmentos não correspondem')
    prev=0
    for i,(b,s) in enumerate(zip(ep['batidas'],segs)):
        a,z=float(s['ini']),float(s['fim'])
        if not all(math.isfinite(v) for v in (a,z)) or a<prev-.001 or z<=a:
            raise ValueError(f'Segmento inválido: {i}')
        end_voice=float(s.get('fim_fala',z-.25))
        if not math.isfinite(end_voice) or not a < end_voice <= z:
            raise ValueError(f'Fim de fala inválido: {i}')
        if s.get('i',i)!=i or not b.get('fala','').strip():
            raise ValueError(f'Fala inválida: {i}')
        prev=z
    return round(prev+TAIL,6)

def linhas(txt,size,width,max_lines=3):
    f=ImageFont.truetype(FONT,size);out=[];line=''
    for word in str(txt).split():
        if f.getlength(word)>width:return None
        candidate=(line+' '+word).strip()
        if f.getlength(candidate)>width and line:out.append(line);line=word
        else:line=candidate
    if line:out.append(line)
    return out if len(out)<=max_lines else None

def bloco(txt,width=850,max_height=128,max_size=58,min_size=26):
    txt=' '.join(str(txt).split())
    for size in range(max_size,min_size-1,-1):
        ls=linhas(txt,size,width)
        if ls and len(ls)*size*1.06<=max_height:
            return '<br>'.join(html.escape(x) for x in ls),size
    # Texto excepcionalmente longo: resumo visual, fala e legenda ficam completos.
    words=txt.split()
    while words:
        words.pop()
        ls=linhas(' '.join(words)+'…',min_size,width)
        if ls and len(ls)*min_size*1.06<=max_height:
            return '<br>'.join(html.escape(x) for x in ls),min_size
    return '…',min_size

def titulo(b,ep,i):
    custom=b.get('hf',{}).get('titulo')
    if custom:return str(custom)
    if i==0:return ep['titulo']
    txt=b.get('tela') or b['fala']
    return re.split(r'(?<=[.!?])\s+',txt,maxsplit=1)[0]

def chunks(text,width=840):
    f=ImageFont.truetype(FONT,45);out=[];g=[]
    for w in text.split():
        if g and (f.getlength(' '.join(g+[w]))>width or len(' '.join(g+[w]))>37):
            out.append(g);g=[]
        g.append(w)
    if g:out.append(g)
    return out

def compor(ep,segs,pasta):
    dur=validar_timeline(ep,segs);parts=[];anim=[]
    for i,(b,s) in enumerate(zip(ep['batidas'],segs)):
        a=float(s['ini']);z=float(s['fim']);d=z-a
        spec=b.get('arte') or [None];tipo=spec[0];arg=spec[1] if len(spec)>1 else None
        tag=b.get('hf',{}).get('selo') or f'EP {ep.get("ep",0):02d} · PARTE {ep.get("parte",1)} · NINA CONTA'
        title,size=bloco(titulo(b,ep,i))
        body,body_size=bloco(arg if arg is not None else (b.get('tela') or b['fala']),max_height=225,max_size=34,min_size=24,width=505 if tipo in ICONS else 790)
        if tipo in ICONS:
            art=ICONS[tipo]+f'<div class="note" style="font-size:{body_size}px">{body}</div>'
        elif tipo=='imagem':
            art=f'<img class="native-art" src="assets/arte{i}.png" alt="Imagem do roteiro">'
        elif tipo and tipo not in TEXT_TYPES:
            art=f'<img class="native-art" src="assets/arte{i}.png" alt="Arte do roteiro">'
        else:
            wave='<div class="wave">'+''.join(f'<i style="height:{17+k*19%44}px"></i>' for k in range(25))+'</div>' if tipo in ('direct','notificacao') else ''
            label='CONTINUAÇÃO' if tipo=='seguir' and ep.get('parte')==1 else 'NINA ME CONTOU'
            art=f'<div class="bubble" style="font-size:{body_size}px"><small>{label}</small>{body}{wave}<div class="underline"></div></div>'
        end=dur if i==len(segs)-1 else z
        parts.append(f'<section id="p{i}" class="clip panel" data-start="{a}" data-duration="{end-a}" data-track-index="2"><div id="c{i}" class="card"><div class="tape"></div><div class="eyebrow">{html.escape(str(tag))}</div><h1 style="font-size:{size}px">{title}</h1><div class="art">{art}</div></div></section>')
        if i:
            anim.append(f'tl.fromTo("#c{i}",{{y:55,rotation:{-3 if i%2 else 3},scale:.94,opacity:0}},{{y:0,rotation:0,scale:1,opacity:1,duration:.42,immediateRender:false,ease:"back.out(1.15)"}},{a});')
        anim.append(f'tl.to("#c{i} .art",{{y:-8,duration:{max(.1,d-.5)},ease:"none"}},{a+.5});')
        anim.append(f'tl.to("#base",{{scale:{1.10 if b.get("zoom") or b.get("expr")=="chocada" else 1.02},x:{-12 if i%2 else 12},duration:.55,ease:"power2.inOut"}},{a});')
        if SFX.tem_wipe(b,i):
            anim.append(f'tl.fromTo("#wipe",{{x:"-110%"}},{{x:"110%",duration:.48,immediateRender:false,ease:"power2.inOut"}},{a});')
        if SFX.tem_flash(b,i):
            anim.append(f'tl.fromTo("#flash",{{opacity:0}},{{opacity:.85,duration:.07,immediateRender:false,ease:"power1.in"}},{a});tl.to("#flash",{{opacity:0,duration:.38,ease:"power2.out"}},{a+.07});')
        active=max(.1,min(d-.1,2.5))
        if tipo=='porta':anim.append(f'tl.to("#p{i} .door",{{y:-140,duration:{active},ease:"power2.inOut"}},{a+.1});')
        if tipo=='carro':anim.append(f'tl.fromTo("#p{i} .car",{{x:-45}},{{x:0,duration:.8,immediateRender:false,ease:"power2.out"}},{a});')
        if tipo=='relogio':anim.append(f'tl.to("#p{i} .hands",{{rotation:360,svgOrigin:"140 130",duration:{d},ease:"none"}},{a});')
        if tipo in ('cafe','caneca'):anim.append(f'tl.fromTo("#p{i} .steam",{{y:7,opacity:.35}},{{y:-5,opacity:1,duration:{active/2},yoyo:true,repeat:1,immediateRender:false}},{a});')
        if tipo=='coracao':anim.append(f'tl.fromTo("#p{i} .heartpath",{{scale:.92,svgOrigin:"140 130"}},{{scale:1,duration:{active/4},yoyo:true,repeat:3,immediateRender:false}},{a});')
        if tipo in ('direct','notificacao'):anim.append(f'tl.fromTo("#p{i} .wave i",{{scaleY:.45}},{{scaleY:1,duration:{min(.24,max(.05,d/8))},stagger:.015,yoyo:true,repeat:4,immediateRender:false}},{a});')
        anim.append(f'tl.fromTo("#p{i} .underline",{{scaleX:0}},{{scaleX:1,duration:.8,immediateRender:false,ease:"power2.out"}},{a});')
        ws=b['fala'].split();total=sum(max(2,len(w)) for w in ws);t=a;j=0
        fim_fala=float(s.get('fim_fala',z-.25));fim_fala=max(a+.01,min(z,fim_fala))
        groups=chunks(b['fala'])
        for k,g in enumerate(groups):
            start=t;spans=[]
            for w in g:
                endw=t+(fim_fala-a)*max(2,len(w))/total
                spans.append(f'<span id="w{i}_{j}">{html.escape(w)}</span>')
                anim.append(f'tl.set("#w{i}_{j}",{{color:"#ffd24a"}},{t});tl.fromTo("#w{i}_{j}",{{scale:1,y:0}},{{scale:1.08,y:-3,duration:{min(.09,max(.02,(endw-t)/2))},immediateRender:false,ease:"power2.out"}},{t});tl.to("#w{i}_{j}",{{scale:1,y:0,duration:.12,ease:"power2.in"}},{max(t+.02,endw-.05)});tl.set("#w{i}_{j}",{{color:"#ffffff"}},{endw});')
                t=endw;j+=1
            stop=z if k==len(groups)-1 else t
            parts.append(f'<div id="cap{i}_{k}" class="clip caps" data-start="{start}" data-duration="{stop-start}" data-track-index="3"><div class="speaker">NINA ME CONTOU</div><div class="words">{" ".join(spans)}</div></div>')
    final,final_size=bloco(ep.get('fim') or ('CONTINUA NA PARTE 2' if ep.get('parte')==1 else 'SEGUE A NINA'),max_height=120,max_size=45)
    parts.append(f'<div id="outro" class="clip caps" data-start="{segs[-1]["fim"]}" data-duration="{TAIL}" data-track-index="3"><div class="speaker">SEGUE A NINA</div><div class="words" style="font-size:{final_size}px">{final}</div></div>')
    confetti=''
    for k in range(22):
        x=80+k*139%920;color=['#ffd24a','#d76577','#fff9ea'][k%3]
        confetti+=f'<div id="f{k}" class="confetti" style="left:{x}px;background:{color}"></div>'
        anim.append(f'tl.fromTo("#f{k}",{{y:0,opacity:1,rotation:0}},{{y:{500+k*11},x:{(k%5-2)*35},rotation:{k*63},opacity:0,duration:1.3,immediateRender:false,ease:"power1.out"}},{segs[-1]["fim"]+k*.03});')
    anim.append(f'tl.fromTo("#progress",{{scaleX:0}},{{scaleX:1,duration:{dur},ease:"none"}},0);')
    out=f'''<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="composition.css"></head><body><div id="root" data-composition-id="nina-hf" data-width="1080" data-height="1920" data-duration="{dur}" data-fps="30"><video id="base" class="clip" src="assets/base.mp4" data-start="0" data-duration="{dur}" data-track-index="0" muted playsinline></video><div class="wash"></div><header><div class="brand">NINA ME CONTOU</div><div class="tag">NA VARANDA</div></header>{''.join(parts)}{confetti}<footer><span>Uma história. Outra perspectiva.</span><small>COMENTE · SIGA</small></footer><div id="progress"></div><div class="demo">HISTÓRIA FICTÍCIA</div><div id="grain"></div><div id="wipe"></div><div id="flash"></div><audio id="voice" src="assets/mix.wav" data-start="0" data-duration="{dur}" data-track-index="4"></audio><script src="assets/gsap.min.js"></script><script>const tl=gsap.timeline({{paused:true}});{''.join(anim)}window.__timelines=window.__timelines||{{}};window.__timelines['nina-hf']=tl;</script></div></body></html>'''
    (pasta/'index.html').write_text(out,encoding='utf-8')
    return dur

def _bed(dur,sr):
    """Trilha original sintetizada (pulso grave + acordes), igual à versão aprovada."""
    out=np.zeros(math.ceil(sr*dur));rng=np.random.default_rng(91)
    def add(t,x):
        i=int(t*sr);n=min(len(x),len(out)-i)
        if n>0:out[i:i+n]+=x[:n]
    for k,t0 in enumerate(np.arange(0,dur,.6)):
        t=np.arange(int(.22*sr))/sr
        add(t0,.008*np.sin(2*np.pi*65*t)*np.exp(-t*25))
        if k%2:add(t0,.002*rng.normal(size=len(t))*np.exp(-t*38))
    for k,t0 in enumerate(np.arange(0,dur,2.4)):
        t=np.arange(int(1.8*sr))/sr;notes=[220,261.63,329.63] if k%2 else [196,246.94,293.66]
        add(t0,sum(.003*np.sin(2*np.pi*f*t)*np.exp(-t*2.8) for f in notes))
    return out

def mixar(voz,segs,dur,destino,ep=None):
    """Voz + trilha (com ducking) + efeitos sincronizados com as animações."""
    sr=SFX.SR;n=math.ceil(sr*dur);destino=Path(destino)
    v48=destino.with_name('voz48.wav')
    sh(['ffmpeg','-y','-v','error','-i',voz,'-ac','1','-ar',str(sr),v48])
    v,_=sf.read(v48,dtype='float64');v=np.pad(v,(0,max(0,n-len(v))))[:n]
    bed=audio_fx.tratar_trilha(_bed(dur,sr),sr)*2.4
    bed=bed*audio_fx.ducking(v,sr)
    efeitos=SFX.trilha_sfx(ep,segs,dur) if ep else np.zeros(n)
    mix=audio_fx.finalizar(v+bed+efeitos[:n],sr)
    sf.write(destino.with_name('bed.wav'),bed,sr);sf.write(destino.with_name('sfx.wav'),efeitos,sr)
    sf.write(destino,mix,sr,subtype='PCM_16')

def conferir(mp4,dur):
    data=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(mp4)]))
    videos=[s for s in data['streams'] if s['codec_type']=='video'];audios=[s for s in data['streams'] if s['codec_type']=='audio']
    if len(videos)!=1 or not audios:raise ValueError('MP4 incompleto: vídeo ou áudio ausente')
    v=videos[0]
    if (v['width'],v['height'],v['avg_frame_rate'])!=(1080,1920,'30/1') or abs(float(data['format']['duration'])-dur)>.15:
        raise ValueError('Resolução, fps ou duração divergente')
    return data

def renderizar(ep,pasta,raiz):
    pasta=Path(pasta);raiz=Path(raiz);segs=json.loads((pasta/'segs.json').read_text())
    dur=validar_timeline(ep,segs)
    if not 15 <= dur <= 90:raise ValueError(f'Duração de produção fora de 15–90 s: {dur}')
    audio=sf.info(pasta/'voz.wav')
    if abs(audio.frames/audio.samplerate-segs[-1]['fim'])>.3:raise ValueError('Áudio e timeline divergentes')
    work=pasta/'hyperframes';assets=work/'assets';assets.mkdir(parents=True,exist_ok=True)
    video=raiz/'video';cli=video/'node_modules/hyperframes/bin/hyperframes.mjs'
    if not cli.is_file():raise FileNotFoundError('HyperFrames ausente: execute npm ci --prefix video')
    env=dict(os.environ,PASTA=str(pasta),EPISODIO=str(pasta/'ep.json'),HYPERFRAMES_NO_TELEMETRY='1',DO_NOT_TRACK='1',HYPERFRAMES_FFMPEG_PATH=shutil.which('ffmpeg') or 'ffmpeg',HYPERFRAMES_FFPROBE_PATH=shutil.which('ffprobe') or 'ffprobe')
    scene=raiz/'motor/cena_hyperframes.py'
    sh([sys.executable,'-m','manim','--disable_caching','--media_dir',pasta/'media_hf','-o','nina-base',scene,'NinaBase'],env=env)
    bases=list((pasta/'media_hf/videos').glob('**/nina-base.mp4'))
    bases=[p for p in bases if 'partial_movie_files' not in str(p)]
    if len(bases)!=1:raise ValueError('Camada Nina não encontrada')
    sh(['ffmpeg','-y','-v','error','-i',bases[0],'-c:v','libx264','-preset','fast','-crf','18','-g','30','-keyint_min','30','-sc_threshold','0','-pix_fmt','yuv420p','-an','-movflags','+faststart',assets/'base.mp4'])
    native=[]
    for i,b in enumerate(ep['batidas']):
        spec=b.get('arte') or [None];tipo=spec[0]
        if tipo=='imagem':
            src=(raiz/str(spec[1])).resolve();src.relative_to(raiz.resolve())
            if str(src).endswith('.b64'):
                (assets/f'arte{i}.png').write_bytes(base64.b64decode(src.read_text().strip(),validate=True))
            else:shutil.copy(src,assets/f'arte{i}.png')
        elif tipo and tipo not in ICONS and tipo not in TEXT_TYPES:native.append(i)
    if native:
        sh([sys.executable,'-m','manim','-s','--disable_caching','--media_dir',pasta/'media_arts',scene,*[f'Arte{i}' for i in native]],env=dict(env,NINA_RENDER_ARTS='1'))
        for i in native:
            found=[p for p in (pasta/'media_arts/images').glob(f'**/Arte{i}*.png')
                   if p.name==f'Arte{i}.png' or p.name.startswith(f'Arte{i}_')]
            if len(found)!=1:raise ValueError(f'Arte {i} ausente')
            shutil.copy(found[0],assets/f'arte{i}.png')
    shutil.copy(FONT,assets/'bold.ttf');shutil.copy(video/'assets/composition.css',work/'composition.css')
    shutil.copy(video/'node_modules/gsap/dist/gsap.min.js',assets/'gsap.min.js')
    mixar(pasta/'voz.wav',segs,dur,assets/'mix.wav',ep);compor(ep,segs,work)
    sh(['node',cli,'lint',work],env=env)
    final=pasta/(ep['id']+'.mp4');tmp=pasta/(ep['id']+'.rendering.mp4')
    sh(['node',cli,'render',work,'--output',tmp,'--workers',os.environ.get('NINA_HF_WORKERS','2'),'--no-browser-gpu'],env=env)
    conferir(tmp,dur);tmp.replace(final)
    info={'motor':'hyperframes','versao':HYPERFRAMES_VERSION,'duracao':dur,'resolucao':[1080,1920],'fps':30,'voz':'pt-BR-ThalitaNeural','audio':'pedalboard' if audio_fx.disponivel() else 'ffmpeg','sfx':len(SFX.eventos(ep,segs)),'cenario':ep.get('cenario','tarde'),'batidas':len(segs)}
    (pasta/'render.json').write_text(json.dumps(info,ensure_ascii=False,indent=2))
    return final
