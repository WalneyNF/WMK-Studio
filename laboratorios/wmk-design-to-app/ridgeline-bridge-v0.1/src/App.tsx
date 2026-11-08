import {useEffect,useMemo,useState} from 'react';
import {DesignCanvas,screens,sourceName,nodeCount} from './DesignCanvas';
import {SemanticOverlay} from './SemanticOverlay';
import manifest from './wmk.manifest.json';
type Field={name:string;type:string;required?:boolean};
type Model={id:string;fields:Field[]};
type RecordRow={id:string;[key:string]:string};
const data=manifest as unknown as {application?:{title?:string;defaultScreen?:number};
  dataModels:Model[];bindings:unknown[];diagnostics:string[]};
const model=data.dataModels[0];
function loadRows():RecordRow[]{
 try{const v:unknown=JSON.parse(localStorage.getItem('wmk-bridge-'+(model?.id||'data'))||'[]');
 return Array.isArray(v)?v.filter((x):x is RecordRow=>typeof x==='object'&&x!==null&&typeof x.id==='string'):[];
 }catch{return [];}
}
export function App(){
 const initial=Math.max(0,screens.findIndex(s=>s.id===data.application?.defaultScreen));
 const [index,setIndex]=useState(initial);
 const [rows,setRows]=useState<RecordRow[]>(loadRows);
 const [form,setForm]=useState<Record<string,string>>({});
 const [query,setQuery]=useState('');
 const [error,setError]=useState('');
 useEffect(()=>{if(model)localStorage.setItem('wmk-bridge-'+model.id,JSON.stringify(rows));},[rows]);
 const screen=screens[index];
 const fields=model?.fields.filter(f=>f.name!=='id')||[];
 const matches=useMemo(()=>rows.filter(row=>Object.values(row).some(value=>String(value).toLocaleLowerCase('pt-BR').includes(query.toLocaleLowerCase('pt-BR')))),[rows,query]);
 const save=(event:React.FormEvent)=>{
  event.preventDefault();
  if(!model)return;
  const missing=fields.filter(f=>f.required&&!String(form[f.name]||'').trim());
  if(missing.length){setError('Campos obrigatórios: '+missing.map(f=>f.name).join(', '));return;}
  const entry:RecordRow={id:crypto.randomUUID()};
  for(const f of fields)entry[f.name]=form[f.name]||'';
  setRows(old=>[entry,...old]);setForm({});setError('');
 };
 const navigate=(id:number)=>{const next=screens.findIndex(s=>s.id===id);if(next>=0)setIndex(next);};
 return <main>
 <h1>WMK App Bridge — React + TypeScript</h1>
 <p>Documento: <strong>{sourceName}</strong> ({nodeCount} nós). Ações definidas no manifesto externo.</p>
 <nav><label htmlFor="screen">Tela:</label>
 <select id="screen" value={index} onChange={e=>setIndex(Number(e.target.value))}>
 {screens.map((s,i)=><option key={s.id} value={i}>{s.name}</option>)}</select>
 <button type="button" onClick={()=>setIndex(x=>(x+screens.length-1)%screens.length)}>Anterior</button>
 <button type="button" onClick={()=>setIndex(x=>(x+1)%screens.length)}>Próxima</button></nav>
 <div className="columns">
  <section className="preview">
   <h2>Design extraído: {screen.name}</h2>
   <div className="bridge-canvas">
    <DesignCanvas index={index}/>
    <div className="bridge-controls" style={{width:screen.width||393,height:screen.height||852}}>
     <SemanticOverlay screenId={screen.id} onNavigate={navigate}/>
    </div>
   </div>
   <p className="note">Inputs e botões interativos foram mapeados pelo arquivo de bindings, não inferidos automaticamente do desenho.</p>
  </section>
  <section className="functions"><h2>Dados do contrato: {model?.id||'Nenhuma entidade'}</h2>
   <p className="note">CRUD demonstrativo persistido em localStorage. Backend/SQLite não implementados nesta versão.</p>
   {model?<><form onSubmit={save}>
    {fields.map(f=><label key={f.name}>{f.name}{f.required?' *':''}
     {f.type==='boolean'?<select value={form[f.name]||''} onChange={e=>setForm(o=>({...o,[f.name]:e.target.value}))}><option value="">Selecione</option><option value="true">Sim</option><option value="false">Não</option></select>:
     <input type={f.type==='email'?'email':f.type==='number'?'number':'text'}
     value={form[f.name]||''} onChange={e=>setForm(o=>({...o,[f.name]:e.target.value}))}/>}
    </label>)}
    <button type="submit">Novo registro</button>{error&&<p role="alert">{error}</p>}
   </form><label htmlFor="filter">Pesquisar registros</label>
   <input id="filter" placeholder="Buscar..." value={query} onChange={e=>setQuery(e.target.value)}/>
   <div aria-live="polite">{matches.map(row=><article key={row.id}>
    <small>{fields.map(f=>f.name+': '+(row[f.name]||'-')).join(' | ')}</small>
    <button type="button" onClick={()=>setRows(old=>old.filter(item=>item.id!==row.id))}>Excluir</button>
   </article>)}</div>
   </>:<p>Nenhuma entidade descrita.</p>}
  </section>
 </div>
 <details><summary>Diagnósticos de conversão</summary><ul>{data.diagnostics.map(x=><li key={x}>{x}</li>)}</ul></details>
 <footer>Walney Moreira Klein — walneyk@hotmail.com</footer>
 </main>;
}
