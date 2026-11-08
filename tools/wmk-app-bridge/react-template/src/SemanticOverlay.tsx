import React, {useState} from 'react';
import design from './design.json';
import manifest from './wmk.manifest.json';

type Node={id:number;parent?:number;name:string;width?:number;height?:number;transform?:number[]};
type Binding={nodeId:number;role:string;name?:string;placeholder?:string;action?:{type:string;screenId:number}};
const nodes=(design as unknown as {nodes:Record<string,Node>}).nodes;
const bindings=(manifest as unknown as {bindings:Binding[]}).bindings;
function inside(node:Node,rootId:number):boolean{
 let current:Node|undefined=node;
 const seen=new Set<number>();
 while(current&&!seen.has(current.id)){
  if(current.id===rootId)return true;
  seen.add(current.id);
  current=current.parent===undefined?undefined:nodes[String(current.parent)];
 }
 return false;
}
function relative(node:Node,rootId:number):{left:number;top:number}{
 let x=0,y=0,current:Node|undefined=node;
 const seen=new Set<number>();
 while(current&&current.id!==rootId&&!seen.has(current.id)){
  seen.add(current.id);
  const transform=current.transform||[1,0,0,1,0,0];
  x+=transform[4]||0;y+=transform[5]||0;
  current=current.parent===undefined?undefined:nodes[String(current.parent)];
 }
 return {left:x,top:y};
}
export function SemanticOverlay({screenId,onNavigate}:{screenId:number;onNavigate:(id:number)=>void}){
 const [values,setValues]=useState<Record<string,string>>({});
 return <div className="wmk-overlay" aria-label="Controles funcionais do contrato WMK">
 {bindings.filter(b=>{const n=nodes[String(b.nodeId)];return n&&inside(n,screenId);}).map(b=>{
  const n=nodes[String(b.nodeId)];const pos=relative(n,screenId);
  const style:React.CSSProperties={position:'absolute',left:pos.left,top:pos.top,
    width:Math.max(40,n.width||70),height:Math.max(28,n.height||28),zIndex:200};
  if(b.role==='input'){
   const name=b.name||String(b.nodeId);
   return <input key={b.nodeId} aria-label={name} title={name} style={style}
     className="wmk-input" placeholder={b.placeholder||n.name}
     value={values[name]||''} onChange={e=>setValues(old=>({...old,[name]:e.target.value}))}/>;
  }
  if(b.role==='button')return <button key={b.nodeId} type="button"
   aria-label={n.name} title={'Ação WMK: '+(b.action?.type||'')}
   className="wmk-hotspot" style={style}
   onClick={()=>{if(b.action?.type==='screen.navigate')onNavigate(b.action.screenId);}}/>;
  return null;
 })}
 </div>;
}
