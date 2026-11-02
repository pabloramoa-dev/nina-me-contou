import React from 'react';
import {AbsoluteFill, Audio, Img, OffthreadVideo, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

type Scene = {start:number;end:number;title:string;fala:string;expr:string};
export type VisualFrame = {start:number;end:number;src:string;origin?:string};
export type NinaProps = {durationFrames:number;scenes:Scene[];visuals?:VisualFrame[]};
const clamp=(n:number,min:number,max:number)=>Math.max(min,Math.min(max,n));
const selectedWords=(s:string,progress:number)=>{
  const words=s.split(/\s+/).filter(Boolean);
  if(words.length<=5)return s;
  const groups: string[]=[];
  for(let i=0;i<words.length;i+=5)groups.push(words.slice(i,i+5).join(' '));
  return groups[Math.min(groups.length-1,Math.floor(clamp(progress,0,0.99999)*groups.length))];
};
const accents=['#f5b94f','#d9858d','#86b3a0','#f1bb64','#dd9cb0','#79b7b2'];

export const NinaUpgrade:React.FC<NinaProps>=({scenes,visuals=[]})=>{
 const frame=useCurrentFrame();const {fps,durationInFrames}=useVideoConfig();const t=frame/fps;
 const index=Math.max(0,scenes.findIndex(s=>t>=s.start&&t<s.end));
 const scene=scenes[index]??scenes[0];
 const elapsed=Math.max(0,t-scene.start);const d=Math.max(1,scene.end-scene.start);
 const progress=clamp(elapsed/d,0,1);
 const appearing=spring({frame:elapsed*fps,fps,config:{damping:16,mass:0.8,stiffness:110}});
 const leaving=clamp((scene.end-t)*2.5,0,1);
 const panelScale=interpolate(appearing,[0,1],[0.76,1])*interpolate(leaving,[0,1],[0.96,1]);
 const panelY=interpolate(appearing,[0,1],[-95,0]);
 const baseZoom=1.03+0.016*Math.sin(t*.48)+(index===3?.035:0);
 const baseX=12*Math.sin(t*.36);
 const caption=selectedWords(scene.fala,progress);
 const textAppear=spring({frame:(elapsed-.1)*fps,fps,config:{damping:18}});
 const accent=accents[index%accents.length];
 const picture=visuals.find(v=>t>=v.start&&t<v.end);
 const pictureDuration=picture?Math.max(.15,picture.end-picture.start):1;
 const pictureElapsed=picture?clamp(t-picture.start,0,pictureDuration):0;
 const pictureProgress=pictureElapsed/pictureDuration;
 const pictureFade=picture?Math.min(1,pictureElapsed/.28,(picture.end-t)/.25):0;
 const pictureScale=1.04+.065*pictureProgress;
 const pictureX=picture?((visuals.indexOf(picture)%2===0?-1:1)*26*(pictureProgress-.5)):0;
 const pictureY=11*Math.sin(pictureProgress*Math.PI);
 const endFade=interpolate(frame,[durationInFrames-18,durationInFrames-1],[1,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});
 return <AbsoluteFill style={{backgroundColor:'#e9d7bc',fontFamily:'Arial, sans-serif',overflow:'hidden',opacity:endFade}}>
   {/* Personagem e lip-sync oficiais renderizados em Manim, não uma imitação da Nina. */}
   <AbsoluteFill style={{transform:`translateX(${baseX}px) scale(${baseZoom})`,transformOrigin:'50% 56%'}}>
     <OffthreadVideo muted src={staticFile('nina-base.mp4')} style={{width:'100%',height:'100%',objectFit:'cover'}} />
   </AbsoluteFill>
   <Audio src={staticFile('mix.wav')} />
   {/* Barra de identidade e progresso da história */}
   <div style={{position:'absolute',top:58,left:66,right:66,display:'flex',justifyContent:'space-between',alignItems:'center',color:'#231f20'}}>
     <div style={{fontWeight:950,fontSize:48,letterSpacing:2,textShadow:'0 2px #fff'}}>NINA ME CONTOU</div>
     <div style={{background:'#fff8e9',border:'4px solid #302725',borderRadius:18,padding:'13px 20px',fontSize:25,fontWeight:900,boxShadow:'7px 8px #302725'}}>NINA CONTA</div>
   </div>
   <div style={{position:'absolute',top:153,left:65,width:950,height:13,background:'#51352d38',borderRadius:18,overflow:'hidden'}}>
     <div style={{width:`${Math.min(100,100*frame/durationInFrames)}%`,height:'100%',background:'#ca5538',borderRadius:18}} />
   </div>
   {/* Cenas cinematograficas ocupam somente a faixa superior.
       A Nina e as legendas oficiais permanecem totalmente visiveis. */}
   {picture ? <div style={{position:'absolute',top:205,left:50,width:980,height:660,
     overflow:'hidden',background:'#f6e8d6',border:'6px solid #34283a',
     borderRadius:26,boxShadow:'14px 17px 0 #38253b55',boxSizing:'border-box',
     opacity:clamp(pictureFade,0,1)}}>
      <Img src={staticFile(picture.src)} style={{width:'100%',height:'100%',
        objectFit:'cover',objectPosition:'center',
        transform:`translate(${pictureX}px,${pictureY}px) scale(${pictureScale})`,
        transformOrigin:'50% 48%'}} />
      <div style={{position:'absolute',inset:0,pointerEvents:'none',
        background:'linear-gradient(180deg,transparent 70%,#1d233322 100%)'}} />
   </div> : null}
   {!picture ? <>
   {/* Cartão original serve de fallback sem sobrepor a apresentadora. */}
   <div style={{position:'absolute',top:226,left:90,width:900,transform:`translateY(${panelY}px) rotate(${interpolate(appearing,[0,1],[7,index%2?2:-2])}deg) scale(${panelScale})`,opacity:Math.min(1,appearing*1.5,leaving*4),transformOrigin:'50% 25%'}}>
     <div style={{height:320,background:'#fff7e7',border:'7px solid #302625',borderRadius:22,boxShadow:'18px 22px 0 #47322c55',padding:'30px 42px',boxSizing:'border-box',display:'flex',alignItems:'center',gap:26}}>
       <div style={{height:195,width:195,borderRadius:24,background:accent,border:'5px solid #292321',display:'flex',flexDirection:'column',justifyContent:'center',alignItems:'center',flexShrink:0,transform:`rotate(${Math.sin(t*4)*4}deg)`}}>
         <span style={{fontSize:78,color:'#302625',fontWeight:950}}>{['?','!', '...', '?!','♥','★','✓'][index%7]}</span>
         <div style={{height:9,width:85,background:'#302625',borderRadius:4}}/>
       </div>
       <div style={{display:'flex',flexDirection:'column',justifyContent:'center',minWidth:0,gap:12}}>
         <span style={{fontSize:25,fontWeight:900,letterSpacing:4,color:'#b3523e'}}>CAPÍTULO {index+1}</span>
         <div style={{fontSize:Math.min(49,scene.title.length>22?40:49),lineHeight:1.09,fontWeight:1000,color:'#29221f',textTransform:'uppercase',overflowWrap:'break-word'}}>{scene.title}</div>
       </div>
     </div>
   </div>
   </> : null}
   {/* Legendas na parte inferior, sem painel fixo: estilo solto aprovado pelo usuário. */}
   <div style={{position:'absolute',left:100,right:100,bottom:195,minHeight:112,display:'flex',justifyContent:'center',alignItems:'center',opacity:Math.max(0,textAppear),transform:`translateY(${interpolate(textAppear,[0,1],[16,0])}px)`,pointerEvents:'none'}}>
     <div style={{maxWidth:880,fontSize:40,fontWeight:950,lineHeight:1.12,letterSpacing:0.3,textAlign:'center',color:'#fffdf6',WebkitTextStroke:'1px #1d201e',textShadow:'3px 3px 0 #292321,-3px 3px 0 #292321,3px -3px 0 #292321,-3px -3px 0 #292321,0 6px 10px #292321aa'}}>
       {caption}
     </div>
   </div>
   <div style={{position:'absolute',left:70,bottom:48,fontSize:20,fontWeight:850,color:'#2a241e',letterSpacing:2,opacity:0.85}}>
     HISTÓRIA FICTÍCIA
   </div>
 </AbsoluteFill>;
};
