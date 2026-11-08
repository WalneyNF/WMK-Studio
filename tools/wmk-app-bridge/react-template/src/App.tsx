import {useCallback,useEffect,useState} from 'react';
import {DesignCanvas,screens,sourceName,nodeCount} from './DesignCanvas';
import {SemanticOverlay} from './SemanticOverlay';
import manifest from './wmk.manifest.json';
type Field={name:string;type:string;required?:boolean};
type Model={id:string;fields:Field[]};
type RecordRow={id:string;[key:string]:unknown};
type Manifest={application?:{title?:string;defaultScreen?:number};dataModels:Model[];diagnostics:string[]};
const config=manifest as unknown as Manifest;
const model=config.dataModels[0];
const api='/api/entities/'+encodeURIComponent(model?.id||'');
export function App(){
 const initial=Math.max(0,screens.findIndex(s=>s.id===config.application?.defaultScreen));
 const [index,setIndex]=useState(initial);
 const [rows,setRows]=useState<RecordRow[]>([]);
 const [form,setForm]=useState<Record<string,string>>({});
 const [editing,setEditing]=useState<string|null>(null);
 const [query,setQuery]=useState('');
 const [error,setError]=useState('');
 const [notice,setNotice]=useState('');
 const [busy,setBusy]=useState(false);
 const fields=model?.fields.filter(f=>f.name!=='id')||[];
 const reload=useCallback(async()=>{
  if(!model)return;
  const res=await fetch(api);
  const body=await res.json() as {data?:RecordRow[];error?:string};
  if(!res.ok)throw new Error(body.error||'Falha ao carregar dados');
  setRows(body.data||[]);
 },[]);
 useEffect(()=>{void reload().catch(e=>setError(String(e)));},[reload]);
 function clear(){setForm({});setEditing(null);setError('');}
 function fromForm(){
  const data:Record<string,unknown>={};
  for(const f of fields){
   const value=form[f.name]||'';
   data[f.name]=f.type==='number'?(value===''?null:Number(value)):f.type==='boolean'?(value===''?null:value==='true'):value===''?null:value;
  }
  return data;
 }
 async function submit(event:React.FormEvent){
  event.preventDefault();if(!model)return;
  setBusy(true);setError('');setNotice('');
  try{
   const res=await fetch(editing?api+'/'+encodeURIComponent(editing):api,{
    method:editing?'PUT':'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(fromForm())
   });
   const body=await res.json() as {error?:string};
   if(!res.ok)throw new Error(body.error||'Falha ao gravar');
   clear();await reload();setNotice(editing?'Registro alterado com sucesso':'Registro incluído no SQLite');
  }catch(e){setError(e instanceof Error?e.message:String(e));}
  finally{setBusy(false);}
 }
 async function remove(id:string){
  if(!confirm('Excluir este registro permanentemente?'))return;
  setBusy(true);setError('');setNotice('');
  try{
   const res=await fetch(api+'/'+encodeURIComponent(id),{method:'DELETE'});
   const body=await res.json() as {error?:string};
   if(!res.ok)throw new Error(body.error||'Falha ao excluir');
   if(editing===id)clear();await reload();setNotice('Registro excluído');
  }catch(e){setError(e instanceof Error?e.message:String(e));}
  finally{setBusy(false);}
 }
 function edit(row:RecordRow){
  const values:Record<string,string>={};
  for(const f of fields){
   const value=row[f.name];
   values[f.name]=value===null||value===undefined?'':String(value);
  }
  setEditing(row.id);setForm(values);setError('');setNotice('');
 }
 const matches=rows.filter(row=>Object.values(row).some(v=>String(v??'').toLowerCase().includes(query.toLowerCase())));
 const screen=screens[index];
 function navigate(id:number){const next=screens.findIndex(s=>s.id===id);if(next>=0)setIndex(next);}
 return <main>
 <h1>WMK App Bridge — Aplicação real com SQLite</h1>
 <p>Documento: <strong>{sourceName}</strong> ({nodeCount} nós). Layout experimental, CRUD via API Node.js + SQLite.</p>
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
   <p className="note">Os botões e campos interativos foram associados aos IDs do documento por bindings.json.</p>
  </section>
  <section className="functions"><h2>Cadastro SQLite: {model?.id||'Sem entidade'}</h2>
   <p className="note">API real em 127.0.0.1:3337. Para funcionar execute <code>npm run dev:full</code>.</p>
   {model?<><form onSubmit={e=>void submit(e)}>
    {fields.map(f=><label key={f.name}>{f.name}{f.required?' *':''}
     {f.type==='boolean'?<select value={form[f.name]||''} onChange={e=>setForm(o=>({...o,[f.name]:e.target.value}))}><option value="">Selecione</option><option value="true">Sim</option><option value="false">Não</option></select>:
     <input required={f.required} type={f.type==='email'?'email':f.type==='number'?'number':'text'}
     value={form[f.name]||''} onChange={e=>setForm(o=>({...o,[f.name]:e.target.value}))}/>}
    </label>)}
    <div className="actions"><button disabled={busy} type="submit">{editing?'Atualizar registro':'Salvar novo registro'}</button>
    <button disabled={busy} type="button" onClick={clear}>Novo / Cancelar</button></div>
   </form>
   {error&&<p role="alert" className="error">{error}</p>}
   {notice&&<p role="status" className="notice">{notice}</p>}
   <label htmlFor="filter">Pesquisar registros gravados</label>
   <input id="filter" value={query} onChange={e=>setQuery(e.target.value)} placeholder="Buscar no banco carregado"/>
   <div aria-live="polite">{matches.map(row=><article key={row.id}>
    <small>{fields.map(f=>f.name+': '+String(row[f.name]??'-')).join(' | ')}</small>
    <div className="actions"><button disabled={busy} onClick={()=>edit(row)}>Editar</button>
    <button disabled={busy} onClick={()=>void remove(row.id)}>Excluir</button></div>
   </article>)}</div>
   <button type="button" onClick={()=>void reload().catch(e=>setError(String(e)))}>Atualizar lista</button>
   </>:<p>Nenhuma entidade no manifesto.</p>}
  </section>
 </div>
 <details><summary>Diagnósticos da conversão</summary><ul>{config.diagnostics.map(x=><li key={x}>{x}</li>)}</ul></details>
 <footer>Walney Moreira Klein — walneyk@hotmail.com</footer>
 </main>;
}
