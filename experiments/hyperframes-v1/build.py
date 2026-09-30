import json,html,shutil
from pathlib import Path
P=Path(__file__).resolve().parent;A=P/'assets'
segs=json.loads((A/'segs.json').read_text())
shutil.copy(P/'node_modules/gsap/dist/gsap.min.js',A/'gsap.min.js')
shutil.copy('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',A/'bold.ttf')
svg=lambda x:f'<svg class="icon" viewBox="0 0 280 260" xmlns="http://www.w3.org/2000/svg">{x}</svg>'
phone=svg('<g class="phone"><rect x="55" y="7" width="168" height="244" rx="26" fill="#27232e"/><rect x="67" y="32" width="144" height="180" rx="5" fill="#d8e9d3"/><rect x="112" y="16" width="54" height="7" rx="4" fill="#7c6f81"/><circle cx="138" cy="231" r="10" fill="#efe4d5"/><path d="M99 145 L178 119 L119 95 L128 119 Z" fill="#417854"/><path d="M100 63h68M90 80h91" stroke="#fff" stroke-width="8"/></g>')
clock=svg('<circle cx="140" cy="130" r="104" fill="#ffd24a" stroke="#27232e" stroke-width="8"/><g class="hands"><path d="M140 130V55M140 130L197 151" fill="none" stroke="#27232e" stroke-width="10" stroke-linecap="round"/></g><circle cx="140" cy="130" r="9" fill="#a53450"/>')
coffee=svg('<g class="steam" stroke="#a53450" stroke-width="7" fill="none"><path d="M91 68q-19-20 0-40M130 68q-19-20 0-40M169 68q-19-20 0-40"/></g><ellipse cx="134" cy="219" rx="107" ry="16" fill="#d3c4ae"/><path d="M204 104h19a36 36 0 010 71h-24" fill="none" stroke="#27232e" stroke-width="12"/><path d="M55 90h148v74a74 49 0 01-148 0z" fill="#ffd24a" stroke="#27232e" stroke-width="7"/><ellipse cx="129" cy="93" rx="72" ry="15" fill="#7c4b33" stroke="#27232e" stroke-width="7"/>')
heart=svg('<path class="heartpath" d="M140 230L34 128C-4 79 42 21 89 39L140 77 187 40C235 19 284 77 246 127Z" fill="#bb4d63" stroke="#27232e" stroke-width="7"/><path d="M70 87Q89 65 105 79" fill="none" stroke="#fff9ea" stroke-width="9" stroke-linecap="round"/>')
car=svg('<g class="car"><path d="M34 157l30-65h146l30 65v55H34z" fill="#ca596d" stroke="#27232e" stroke-width="7"/><path d="M81 106h112l22 48H59z" fill="#c0e0de" stroke="#27232e" stroke-width="6"/><circle cx="71" cy="216" r="22" fill="#27232e"/><circle cx="211" cy="216" r="22" fill="#27232e"/><rect x="110" y="181" width="61" height="18" fill="#fff9ea"/><circle cx="61" cy="178" r="12" fill="#ffd24a"/><circle cx="217" cy="178" r="12" fill="#ffd24a"/></g>')
remote=svg('<g class="remote"><rect x="80" y="26" width="120" height="209" rx="27" fill="#453b4d" stroke="#221e25" stroke-width="8"/><circle cx="141" cy="91" r="31" fill="#ffd24a"/><rect x="109" y="151" width="62" height="19" rx="6" fill="#958695"/><path d="M116 14Q141-14 166 14M102 2Q141-37 180 2" fill="none" stroke="#a53450" stroke-width="7"/></g>')
garage=svg('<path d="M20 91L140 15 260 91v152H20z" fill="#e3b998" stroke="#27232e" stroke-width="8"/><rect x="50" y="99" width="180" height="144" fill="#282130"/><g class="door"><rect x="50" y="99" width="180" height="144" fill="#c2d6c5"/><path d="M50 123h180M50 148h180M50 173h180M50 198h180M50 223h180" stroke="#52715c" stroke-width="6"/></g><circle class="light" cx="141" cy="78" r="12" fill="#ffd24a"/>')
ship=svg('<path d="M28 165h230l-39 68H70z" fill="#453b4d" stroke="#27232e" stroke-width="7"/><rect x="84" y="79" width="103" height="85" fill="#f7e9d2" stroke="#27232e" stroke-width="6"/><path d="M127 79V27h23v52" fill="#cc5c70" stroke="#27232e" stroke-width="6"/><path d="M21 238q35-18 60 0t60 0t60 0t60 0" fill="none" stroke="#6ca3ac" stroke-width="9"/>')
cake=svg('<ellipse cx="140" cy="225" rx="118" ry="18" fill="#d3c4ae"/><path d="M47 101h186v104H47z" fill="#deac87" stroke="#27232e" stroke-width="7"/><path d="M47 141h186M47 177h186" stroke="#ad6268" stroke-width="14"/><path d="M48 101q17-49 43-23 28-48 51-16 34-38 56 11 34-17 35 28v31q-15 20-28 0-13 20-27 0-13 20-27 0-13 20-27 0-13 20-27 0-13 20-27 0-13 20-22 0z" fill="#fff9ea" stroke="#27232e" stroke-width="5"/>')
wave='<div class="wave">'+''.join(f'<i style="height:{17+(k*19)%44}px"></i>' for k in range(25))+'</div>'
cards=[
 ('O PORTÃO DA GARAGEM · PARTE 1','ELA ABRIU A GARAGEM ERRADA.',remote+'<div class="note"><strong>UM CLIQUE.</strong>E o portão errado<br>começou a subir.</div>'),
 ('QUEM CONTOU PARA A NINA','CLÁUDIA, 42 ANOS.','<div class="bubble"><small>RELATO · HISTÓRIA FICTÍCIA</small>Casada com Sérgio há 15 anos.'+wave+'</div>'),
 ('A RESENHA COMEÇOU','O CONDOMÍNIO PARTICIPA.','<div class="bubble"><small>EM DUAS PARTES</small>Segue a Nina.<br>Essa história ainda vai longe.</div><div class="stamp">VEM VER!</div>'),
 ('A DESCULPA DA VEZ','“A VAGA ERA APERTADA.”',car+'<div class="note"><strong>TROCOU DE VAGA.</strong>Foi o que Sérgio<br>contou para ela.</div>'),
 ('TEM UM PEQUENO DETALHE','NA CASA DO LADO.',garage+'<div class="note"><strong>VAGA COBERTA.</strong>Garagem emprestada.<br>Bem perto de casa.</div>'),
 ('A GARAGEM ERA DA VERA','O MARIDO ESTAVA NO MAR.',ship+'<div class="note"><strong>30 DIAS.</strong>O marido embarcado.<br>A vizinha em casa.</div>'),
 ('TUDO MUITO EDUCADO','ATÉ BOLO ELA MANDOU.',cake+'<div class="note"><strong>“OBRIGADA!”</strong>Gentileza de vizinha.<br>Tudo combinado.</div>'),
 ('UM DIA, CLÁUDIA PEGOU…','O CONTROLE DO SÉRGIO.',remote+'<div class="note"><strong>SÓ IA TIRAR O CARRO.</strong>Mas aquele botão<br>tinha outra história.</div>'),
 ('ONZE DA NOITE','“VOU À FARMÁCIA.”',clock+'<div class="note"><strong>23:00</strong>Foi o que Sérgio<br>disse antes de sair.</div>'),
 ('O BOTÃO ERRADO','O PORTÃO DA VERA SUBIU.',garage+'<div class="note"><strong>ABRIU.</strong>Cláudia não esperava<br>o que viu lá dentro.</div><div class="stamp">FLAGRANTE?</div>'),
 ('LÁ DENTRO','O CARRO DO SÉRGIO.',car+'<div class="note"><strong>MOTOR QUENTE.</strong>Bem ali.<br>Na garagem da vizinha.</div>'),
 ('NINA TEM UM PONTO','ISSO NÃO É FARMÁCIA.','<div class="bubble red"><small>UM DETALHE IMPORTANTE</small>Farmácia não fica na<br>garagem da vizinha.<div class="underline"></div></div>'),
 ('MAIS UMA PISTA','E A LUZ ESTAVA ACESA.',garage+'<div class="note"><strong>LUZ ACESA.</strong>Normalmente,<br>apagava às dez.</div>'),
 ('O QUE CLÁUDIA FEZ?','O CONTROLE AINDA NA MÃO.','<div class="bubble"><small>CONTINUA NA PARTE 2</small>Você faria o quê?<br><br>COMENTE · SIGA A NINA</div>')]
clips=[];anim=[]
for i,(s,(tag,title,art)) in enumerate(zip(segs,cards)):
 a=s['ini'];z=60 if i==len(segs)-1 else s['fim'];d=z-a
 clips.append(f'<section class="clip panel" id="p{i}" data-start="{a}" data-duration="{d}" data-track-index="2"><div class="card" id="c{i}"><div class="tape"></div><div class="eyebrow">{tag}</div><h1>{title}</h1><div class="art">{art}</div></div></section>')
 if i:
  anim.append(f'tl.fromTo("#c{i}",{{y:55,rotation:{-3 if i%2 else 3},scale:.94,opacity:0}},{{y:0,rotation:0,scale:1,opacity:1,duration:.42,ease:"back.out(1.15)"}},{a});')
 else:anim.append('tl.fromTo("#c0",{scale:.98},{scale:1,duration:.45,ease:"power2.out"},0);')
 anim.append(f'tl.to("#c{i} .art",{{y:-8,duration:{max(.3,d-.5)},ease:"none"}},{a+.5});')
 anim.append(f'tl.to("#base",{{scale:{1.10 if i in (9,11) else 1.02},x:{-12 if i%2 else 12},duration:.55,ease:"power2.inOut"}},{a});')
 if i in (3,9):anim.append(f'tl.fromTo("#wipe",{{x:"-110%"}},{{x:"110%",duration:.48,ease:"power2.inOut"}},{a});')
 words=s['texto'].split();groups=[];g=[]
 for w in words:
  if len(' '.join(g+[w]))>36 and g:groups.append(g);g=[]
  g.append(w)
 if g:groups.append(g)
 total=sum(max(2,len(w)) for w in words);t=a;j=0
 for k,g in enumerate(groups):
  start=t;spans=[]
  for w in g:
   end=t+(s['fim_fala']-a)*max(2,len(w))/total
   spans.append(f'<span id="w{i}_{j}">{html.escape(w)}</span>')
   anim.append(f'tl.set("#w{i}_{j}",{{color:"#ffd24a"}},{t});tl.set("#w{i}_{j}",{{color:"#ffffff"}},{end});')
   t=end;j+=1
  stop=(s['fim'] if i==len(segs)-1 else z) if k==len(groups)-1 else t
  clips.append(f'<div id="caption{i}_{k}" class="clip caps" data-start="{start}" data-duration="{stop-start}" data-track-index="3"><div class="speaker">NINA ME CONTOU</div><div class="words">{" ".join(spans)}</div></div>')
clips.append('<div id="outro" class="clip caps" data-start="57.25" data-duration="2.75" data-track-index="3"><div class="speaker">SEGUE A NINA</div><div class="words">CONTINUA NA PARTE 2</div></div>')
anim.append(f'tl.fromTo("#p1 .wave i",{{scaleY:.45}},{{scaleY:1,duration:.24,stagger:.02,yoyo:true,repeat:18,ease:"sine.inOut"}},{segs[1]["ini"]});')
anim.append(f'tl.fromTo("#p2 .stamp",{{scale:2,opacity:0,rotation:-30}},{{scale:1,opacity:1,rotation:-8,duration:.25,ease:"back.out(2)"}},{segs[2]["ini"]+.6});')
anim.append(f'tl.to(".hands",{{rotation:360,svgOrigin:"140 130",duration:{segs[8]["fim"]-segs[8]["ini"]},ease:"none"}},{segs[8]["ini"]});')
anim.append(f'tl.fromTo("#p9 .door",{{y:0}},{{y:-140,duration:2,ease:"power2.inOut"}},{segs[9]["ini"]+.15});')
anim.append(f'tl.fromTo("#p9 .stamp",{{scale:2,opacity:0,rotation:-30}},{{scale:1,opacity:1,rotation:-8,duration:.25,ease:"back.out(2)"}},{segs[9]["ini"]+.6});')
anim.append(f'tl.fromTo("#p10 .car",{{x:-45}},{{x:0,duration:.8,ease:"power2.out"}},{segs[10]["ini"]});')
anim.append(f'tl.fromTo(".underline",{{scaleX:0}},{{scaleX:1,duration:.8,ease:"power2.out"}},{segs[11]["ini"]+.8});')
anim.append(f'tl.fromTo("#p12 .light",{{opacity:.3}},{{opacity:1,duration:.35,yoyo:true,repeat:7}},{segs[12]["ini"]});')
confetti=''
for k in range(22):
 x=80+(k*139)%920;confetti+=f'<div class="confetti" id="f{k}" style="left:{x}px;background:{["#ffd24a","#d76577","#fff9ea"][k%3]}"></div>'
 anim.append(f'tl.fromTo("#f{k}",{{y:0,opacity:1,rotation:0}},{{y:{500+k*11},x:{(k%5-2)*35},rotation:{k*63},opacity:0,duration:2.8,ease:"power1.out"}},{segs[-1]["ini"]+k*.04});')
anim.append('tl.fromTo("#progress",{scaleX:0},{scaleX:1,duration:60,ease:"none"},0);')
anim=[x.replace('duration:', 'immediateRender:false,duration:') for x in anim]
out=f'''<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="composition.css"></head><body><div id="root" data-composition-id="nina-hf" data-width="1080" data-height="1920" data-duration="60" data-fps="30"><video id="base" class="clip" src="assets/base.mp4" data-start="0" data-duration="60" data-track-index="0" muted playsinline></video><div class="wash"></div><header><div class="brand">NINA ME CONTOU</div><div class="tag">NA VARANDA</div></header>{''.join(clips)}{confetti}<footer><span>Uma história. Outra perspectiva.</span><small>COMENTE · SIGA</small></footer><div id="progress"></div><div class="demo">HISTÓRIA FICTÍCIA · TESTE VISUAL</div><div id="grain"></div><div id="wipe"></div><audio id="voice" src="assets/mix.wav" data-start="0" data-duration="60" data-track-index="4"></audio><script src="assets/gsap.min.js"></script><script>const tl=gsap.timeline({{paused:true}});{''.join(anim)}window.__timelines=window.__timelines||{{}};window.__timelines['nina-hf']=tl;</script></div></body></html>'''
(P/'index.html').write_text(out)
print('Composição: 60 s, 1080x1920, 30 fps')

