import React from 'react';
import doc from './design.json';
type Color = {r:number;g:number;b:number;a?:number};
type Fill = {type:string;color?:Color;visible?:boolean;kind?:string;stops?:{position:number;color:Color}[]};
type Node = {id:number;name:string;type:string;width?:number;height?:number;
  transform?:number[];fills?:Fill[];strokes?:Fill[];children?:number[];
  corners?:{radii?:number[]};clip?:boolean;characters?:string;
  style?:{font_size?:number;font_style?:string;line_height?:{value?:number}}};
const source = doc as unknown as {nodes:Record<string,Node>;screens:number[];name:string};
export const screens = source.screens.map(id=>source.nodes[String(id)]);
export const sourceName = source.name;
export const nodeCount = Object.keys(source.nodes).length;
function cssColor(c?:Color):string|undefined{
 if(!c)return;
 return 'rgba('+[c.r,c.g,c.b].map(v=>Math.max(0,Math.min(255,Math.round(v*255)))).join(',')+','+(c.a??1)+')';
}
function background(fs?:Fill[]):string|undefined{
 const f=fs?.find(x=>x.visible!==false);
 if(!f)return;
 if(f.type==='solid')return cssColor(f.color);
 if(f.type==='gradient'&&f.stops?.length){
  const stops=f.stops.map(s=>cssColor(s.color)+' '+(s.position*100)+'%').join(', ');
  return (f.kind==='radial'?'radial-gradient(circle, ':'linear-gradient(180deg, ')+stops+')';
 }
}
function Layer({id,depth=0}:{id:number;depth?:number}):React.ReactNode{
 const n=source.nodes[String(id)];
 if(!n||depth>32)return null;
 const t=n.transform||[1,0,0,1,0,0];
 const vector=['vector','line','booleanOp','polygon','star'].includes(n.type);
 const text=n.type==='text';
 const style:React.CSSProperties={
  position:'absolute',left:t[4]||0,top:t[5]||0,width:n.width||0,height:n.height||0,
  boxSizing:'border-box',background:vector||text?undefined:background(n.fills),
  borderRadius:n.type==='ellipse'?'50%':n.corners?.radii?.map(v=>v+'px').join(' '),
  overflow:n.clip?'hidden':undefined
 };
 if(n.strokes?.length)style.border='1px solid '+(background(n.strokes)||'transparent');
 if(text){
  style.color=background(n.fills)||'#172033';style.whiteSpace='pre-wrap';
  style.fontSize=n.style?.font_size||14;style.lineHeight=(n.style?.line_height?.value||120)/100;
  style.fontFamily='Inter,Segoe UI,system-ui,sans-serif';
  style.fontWeight=/semi/i.test(n.style?.font_style||'')?600:/bold/i.test(n.style?.font_style||'')?700:400;
 }
 const children=n.children?.map(child=><Layer key={child} id={child} depth={depth+1}/>);
 return text?<span style={style} data-wmk-id={n.id} title={n.name}>{n.characters||''}</span>:
 <div style={style} data-wmk-id={n.id} title={n.name}>{children}</div>;
}
export function DesignCanvas({index}:{index:number}){
 const n=screens[index];if(!n)return <p>Tela nao encontrada.</p>;
 return <div className="canvas-wrap"><div className="canvas-screen" style={{width:n.width||393,height:n.height||852}}>
 {n.children?.map(id=><Layer key={id} id={id}/>)}</div></div>;
}
