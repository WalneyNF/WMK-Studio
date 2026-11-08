/* Preview WMK do Data Studio */
(function(){
'use strict';
const $=id=>document.getElementById(id);
let data=null;
const mk=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=String(text);return e};
const color=c=>c?'rgba('+[c.r,c.g,c.b].map(v=>Math.min(255,Math.max(0,Math.round((Number(v)||0)*255)))).join(',')+','+(c.a??1)+')':undefined;
function bg(arr){
 const x=Array.isArray(arr)?arr.find(v=>v.visible!==false):null;
 if(!x)return;
 if(x.type==='solid')return color(x.color);
 if(x.type==='gradient'&&Array.isArray(x.stops)){
  const stops=x.stops.map(s=>color(s.color)+' '+(s.position*100)+'%').join(', ');
  return (x.kind==='radial'?'radial-gradient(circle, ':'linear-gradient(180deg, ')+stops+')';
 }
}
function render(id,depth,seen){
 const n=data.nodes[String(id)];
 if(!n||depth>45||seen.has(String(id)))return null;
 seen=new Set(seen);seen.add(String(id));
 const e=mk(n.type==='text'?'span':'div');
 const t=Array.isArray(n.transform)?n.transform:[1,0,0,1,0,0];
 Object.assign(e.style,{position:'absolute',left:(t[4]||0)+'px',top:(t[5]||0)+'px',
 width:(n.width||0)+'px',height:(n.height||0)+'px',boxSizing:'border-box',
 background:bg(n.fills)||'transparent',overflow:n.clip?'hidden':'visible'});
 if(t[0]!==1||t[1]!==0||t[2]!==0||t[3]!==1){
  e.style.transform='matrix('+[t[0],t[1],t[2],t[3],0,0].join(',')+')';
  e.style.transformOrigin='top left';
 }
 if(n.type==='ellipse')e.style.borderRadius='50%';
 if(n.corners?.radii?.length)e.style.borderRadius=n.corners.radii.map(v=>v+'px').join(' ');
 if(n.strokes?.length)e.style.border='1px solid '+(bg(n.strokes)||'transparent');
 e.dataset.wmkNodeId=String(id);e.title=(n.name||'Sem nome')+' ('+n.type+')';
 if(n.type==='text'){
  e.textContent=n.characters||'';
  e.style.color=bg(n.fills)||'#15232c';e.style.background='none';
  e.style.fontSize=(n.style?.font_size||14)+'px';
  e.style.fontFamily='Inter, Segoe UI, system-ui, sans-serif';
  e.style.fontWeight=/bold/i.test(n.style?.font_style||'')?700:400;
  e.style.whiteSpace='pre-wrap';e.style.overflowWrap='break-word';
 }else if(n.type==='vector'&&n.network?.vertices?.length>=3){
  const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');
  svg.setAttribute('width',String(n.width||0));svg.setAttribute('height',String(n.height||0));
  svg.setAttribute('viewBox','0 0 '+(n.width||0)+' '+(n.height||0));
  const polygon=document.createElementNS('http://www.w3.org/2000/svg','polygon');
  const loop=n.network.regions?.[0]?.loops?.[0];
  const ids=Array.isArray(loop)&&loop.length?loop:n.network.vertices.map((_,i)=>i);
  polygon.setAttribute('points',ids.map(i=>{const p=n.network.vertices[i];return p?(p.x||0)+','+(p.y||0):''}).join(' '));
  polygon.setAttribute('fill',bg(n.fills)||'transparent');polygon.setAttribute('stroke',bg(n.strokes)||'none');
  svg.append(polygon);e.style.background='none';e.append(svg);
 }
 for(const child of n.children||[]){const c=render(child,depth+1,seen);if(c)e.append(c)}
 return e;
}
function tree(id,container,depth,seen){
 const n=data.nodes[String(id)];if(!n||depth>15||seen.has(String(id)))return;
 seen=new Set(seen);seen.add(String(id));
 const btn=mk('button','wmk-tree-item','· '.repeat(depth)+(n.name||'Sem nome')+' ['+n.type+'] #'+id);
 btn.type='button';btn.onclick=()=>{
  $('wmkStage').querySelectorAll('[data-wmk-node-id]').forEach(x=>x.dataset.selected=String(x.dataset.wmkNodeId===String(id)));
  $('wmkStatus').textContent='Selecionado: '+n.name+' ('+n.type+') #'+id;
 };
 container.append(btn);
 if(depth<6)for(const child of n.children||[])tree(child,container,depth+1,seen);
}
function screen(id){
 const info=data.screens.find(s=>String(s.id)===String(id));if(!info)return;
 const root=data.nodes[String(id)],stage=$('wmkStage');
 stage.replaceChildren();
 stage.style.width=Math.max(1,Math.min(5000,Number(info.width)||393))+'px';
 stage.style.height=Math.max(1,Math.min(5000,Number(info.height)||852))+'px';
 stage.style.background=bg(root?.fills)||'#fff';
 for(const child of root?.children||[]){const n=render(child,0,new Set());if(n)stage.append(n)}
 $('wmkScreenName').textContent=info.name;
 $('wmkTree').replaceChildren();tree(id,$('wmkTree'),0,new Set());
 $('wmkScreens').querySelectorAll('button').forEach(b=>b.classList.toggle('selected',b.dataset.screenId===String(id)));
 $('wmkStatus').textContent='Tela carregada: '+info.name;
}
function show(value){
 data=value;$('wmkContent').hidden=false;
 $('wmkProjectName').textContent=value.name;
 $('wmkFormat').textContent='Formato '+value.format+' v'+value.version;
 $('wmkCount').textContent=value.nodeCount+' nós / '+value.screens.length+' telas';
 $('wmkScreens').replaceChildren();
 for(const s of value.screens){
  const b=mk('button','',s.name+' ('+s.width+'x'+s.height+')');
  b.type='button';b.dataset.screenId=String(s.id);b.onclick=()=>screen(s.id);$('wmkScreens').append(b);
 }
 $('wmkThumbnail').hidden=!value.thumbnail;
 if(value.thumbnail)$('wmkThumbnail').src=value.thumbnail;
 $('wmkDiagnostics').textContent=value.diagnostics.join('\n')+'\n\n'+Object.entries(value.counts).map(([type,num])=>type+': '+num).join('\n');
 if(value.screens.length)screen(value.screens[0].id);
 else $('wmkStatus').textContent='Nenhuma tela Frame encontrada';
}
function selectTab(wmk){
 $('tabDb').classList.toggle('selected',!wmk);
 $('tabWmk').classList.toggle('selected',wmk);
 $('tabDb').setAttribute('aria-selected',String(!wmk));
 $('tabWmk').setAttribute('aria-selected',String(wmk));
 $('dbLayout').hidden=wmk;$('wmkWorkspace').hidden=!wmk;
}
$('tabDb').onclick=()=>selectTab(false);
$('tabWmk').onclick=()=>selectTab(true);
$('wmkLoad').onclick=async()=>{
 const f=$('wmkFile').files?.[0];
 if(!f){$('wmkStatus').textContent='Selecione um arquivo .wmk ou .figcraft';return}
 if(f.size>12*1024*1024){$('wmkStatus').textContent='Arquivo acima de 12 MB';return}
 $('wmkLoad').disabled=true;$('wmkStatus').textContent='Lendo documento...';
 try{
  const res=await fetch('/api/wmk/import',{method:'POST',
   headers:{'Content-Type':'application/octet-stream','X-WMK-Token':TOKEN},body:f});
  const body=await res.json();if(!res.ok)throw Error(body.error||'Falha');
  show(body);
 }catch(err){$('wmkStatus').textContent='Erro: '+(err?.message||err)}
 finally{$('wmkLoad').disabled=false}
};
})();