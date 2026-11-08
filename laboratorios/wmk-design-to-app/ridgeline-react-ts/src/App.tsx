import {useEffect,useMemo,useState} from 'react';
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
