from pathlib import Path
import json
r=Path(r'D:\Ferramentas\figcraft')
base=r/'laboratorios/wmk-design-to-app'
old=base/'ridgeline-web-poc'
dst=base/'ridgeline-react-ts'
src=dst/'src';src.mkdir(parents=True,exist_ok=True)
d=json.loads((old/'design.json').read_text(encoding='utf8'))
(src/'design.json').write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')),encoding='utf8')
package={"name":"wmk-ridgeline-react-poc","version":"0.2.0","private":True,"type":"module","scripts":{"dev":"vite","build":"tsc --noEmit && vite build","typecheck":"tsc --noEmit"},"dependencies":{"react":"^19.0.0","react-dom":"^19.0.0"},"devDependencies":{"@types/react":"^19.0.0","@types/react-dom":"^19.0.0","typescript":"~5.8.0","vite":"^6.0.0","@vitejs/plugin-react":"^4.3.0"}}
(dst/'package.json').write_text(json.dumps(package,indent=2),encoding='utf8')
config={"compilerOptions":{"target":"ES2022","lib":["ES2022","DOM","DOM.Iterable"],"module":"ESNext","moduleResolution":"Bundler","resolveJsonModule":True,"jsx":"react-jsx","strict":True,"noEmit":True,"skipLibCheck":True,"esModuleInterop":True,"isolatedModules":True,"types":["vite/client"]},"include":["src"]}
(dst/'tsconfig.json').write_text(json.dumps(config,indent=2),encoding='utf8')
(dst/'index.html').write_text('<!doctype html><html lang="pt-BR"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>WMK Ridgeline React</title></head><body><div id="root"></div><script type="module" src="/src/main.tsx"></script></body></html>',encoding='utf8')
(dst/'.gitignore').write_text('node_modules/\ndist/\n',encoding='utf8')
(src/'main.tsx').write_text("""import React from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './App';
import './style.css';
const root = document.getElementById('root');
if (!root) throw new Error('Div root ausente');
createRoot(root).render(<React.StrictMode><App /></React.StrictMode>);
""",encoding='utf8')
(src/'DesignCanvas.tsx').write_text("""import React from 'react';
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
""",encoding='utf8')
(src/'App.tsx').write_text("""import {useEffect,useMemo,useState} from 'react';
import {DesignCanvas,screens,sourceName,nodeCount} from './DesignCanvas';
type Trail={id:string;name:string;difficulty:string;km:number};
const trails:Trail[]=[
 {id:'1',name:'Trilha da Serra',difficulty:'Media',km:6.5},
 {id:'2',name:'Mirante do Vale',difficulty:'Facil',km:2.8},
 {id:'3',name:'Circuito das Montanhas',difficulty:'Dificil',km:12.2}
];
function readFavorites():string[]{
 try{const v:unknown=JSON.parse(localStorage.getItem('wmk-poc-favorites')||'[]');
 return Array.isArray(v)?v.filter((x):x is string=>typeof x==='string'):[]}
 catch{return []}
}
export function App(){
 const [index,setIndex]=useState(0);
 const [query,setQuery]=useState('');
 const [difficulty,setDifficulty]=useState('Todas');
 const [favorites,setFavorites]=useState<string[]>(readFavorites);
 const [selected,setSelected]=useState<Trail|null>(null);
 useEffect(()=>localStorage.setItem('wmk-poc-favorites',JSON.stringify(favorites)),[favorites]);
 const found=useMemo(()=>trails.filter(t=>t.name.toLowerCase().includes(query.toLowerCase())&&(difficulty==='Todas'||t.difficulty===difficulty)),[query,difficulty]);
 const toggle=(id:string)=>setFavorites(prev=>prev.includes(id)?prev.filter(x=>x!==id):[...prev,id]);
 return <main>
  <h1>WMK Studio → React + TypeScript</h1>
  <p>Arquivo real: <strong>{sourceName}</strong> · {nodeCount} nos</p>
  <nav aria-label="Telas extraidas">
   <label htmlFor="screen">Tela:</label>
   <select id="screen" value={index} onChange={e=>setIndex(Number(e.target.value))}>
    {screens.map((s,i)=><option value={i} key={s.id}>{s.name}</option>)}
   </select>
   <button onClick={()=>setIndex(x=>(x+screens.length-1)%screens.length)}>Anterior</button>
   <button onClick={()=>setIndex(x=>(x+1)%screens.length)}>Proxima</button>
  </nav>
  <div className="columns">
   <section className="preview"><h2>Design extraido</h2><DesignCanvas index={index}/><p className="note">Reconstrucao aproximada. Vetores, efeitos e auto-layout incompletos.</p></section>
   <section className="functions">
    <h2>Interacoes reais de demonstracao</h2>
    <p className="note">Trilhas de exemplo programadas no React, nao extraidas do WMK. Favoritos persistem no navegador.</p>
    <label htmlFor="search">Buscar trilha</label>
    <input id="search" value={query} onChange={e=>setQuery(e.target.value)} placeholder="Pesquisar..."/>
    <label htmlFor="filter">Dificuldade</label>
    <select id="filter" value={difficulty} onChange={e=>setDifficulty(e.target.value)}>
     {['Todas','Facil','Media','Dificil'].map(v=><option key={v}>{v}</option>)}
    </select>
    <div aria-live="polite">{found.length===0?<p>Nenhuma trilha encontrada.</p>:found.map(t=><article key={t.id}>
     <strong>{t.name}</strong><small>{t.difficulty} · {t.km} km</small>
     <button onClick={()=>setSelected(t)}>Detalhes</button>
     <button aria-pressed={favorites.includes(t.id)} onClick={()=>toggle(t.id)}>
      {favorites.includes(t.id)?'★ Favorito':'☆ Favoritar'}
     </button>
    </article>)}</div>
    {selected&&<aside><h3>{selected.name}</h3><p>{selected.difficulty} · {selected.km} km</p><button onClick={()=>setSelected(null)}>Fechar</button></aside>}
    <p>Favoritos salvos: {favorites.length}</p>
   </section>
  </div>
  <footer>Walney Moreira Klein — walneyk@hotmail.com</footer>
 </main>;
}
""",encoding='utf8')
(src/'style.css').write_text("""*{box-sizing:border-box}body{margin:0;background:#10051c;color:#f6eaff;font:15px/1.5 Inter,system-ui,Segoe UI,sans-serif}main{max-width:1330px;margin:auto;padding:20px}h1{color:#e6b3ff}h2{font-size:1.15rem}nav{display:flex;gap:10px;align-items:center;margin-bottom:17px;flex-wrap:wrap}button,select,input{background:#341c4d;color:white;border:1px solid #78519a;border-radius:7px;padding:9px 12px;font:inherit}button{cursor:pointer}button:hover{background:#67318c}.columns{display:grid;grid-template-columns:minmax(430px,1.2fr) minmax(300px,.8fr);gap:18px}section{background:#241136;border:1px solid #6a3c82;border-radius:12px;padding:15px}.canvas-wrap{overflow:auto;background:#38254b;padding:16px;border-radius:12px;display:flex;justify-content:center}.canvas-screen{position:relative;background:white;overflow:hidden;flex-shrink:0;box-shadow:0 12px 28px #0008;border-radius:12px}.note,footer{color:#bfa6cf}.functions{display:flex;flex-direction:column;gap:12px}.functions article{background:#301a49;padding:12px;border-radius:9px;margin:9px 0}.functions article small{display:block}.functions article button{margin:6px 6px 0 0;font-size:13px}aside{background:#3d2458;border-radius:9px;padding:12px}footer{padding:24px 0}@media(max-width:900px){.columns{grid-template-columns:1fr}.canvas-wrap{justify-content:flex-start}}""",encoding='utf8')
(dst/'README.md').write_text("""# WMK Studio — React/TypeScript 0.2 (experimental)
## Executar
npm install
npm run dev
npm run build
## O que foi extraido
O arquivo src/design.json contem os 349 nos originais e 3 Frames de tela. O componente DesignCanvas reconstrui textos, formas simples e alguns estilos a partir dos dados de origem.
## O que foi programado
Navegacao entre telas; pesquisa, filtro, detalhes e favoritos com localStorage. Os dados das trilhas sao **exemplos**, nao conteudo gerado do WMK.
## Limitacoes
Sem conversao fiel de vetores, auto-layout ou prototipo; sem backend ou banco. A conversao ainda nao eh generica para todos os arquivos WMK.
Walney Moreira Klein — walneyk@hotmail.com. Base WMK Studio/FigCraft.
""",encoding='utf8')
print('GENERATED',dst,'NODES',len(d['nodes']),'SCREENS',len(d['screens']))
