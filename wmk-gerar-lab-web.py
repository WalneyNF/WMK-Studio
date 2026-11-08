from pathlib import Path
import zipfile,json,collections,shutil
r=Path(r'D:\Ferramentas\figcraft');src=r/'examples/ridgeline-app.figcraft'
out=r/'laboratorios/wmk-design-to-app/ridgeline-web-poc';out.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(src) as z:d=json.loads(z.read('document.json'))
shutil.copy2(src,out/'ridgeline-laboratorio.wmk')
nodes=d['nodes'];types=dict(collections.Counter(n['type'] for n in nodes.values()))
screens=[x for x in nodes[str(d['pages'][0])]['children'] if nodes[str(x)]['type']=='frame']
data={'name':d['name'],'nodes':nodes,'screens':screens,'types':types}
(out/'design.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
js=String=None
js=r"""
const D=__DATA__;
const get=id=>D.nodes[String(id)];
const screenIds=D.screens;
const sel=document.getElementById('sel');
const stage=document.getElementById('stage');
const warnings=document.getElementById('warnings');
const csscolor=c=>c?'rgba('+['r','g','b'].map(k=>Math.round((Number(c[k])||0)*255)).join(',')+','+(c.a??1)+')':null;
let issues=new Set();
function fill(f){
  let x=(f||[]).find(v=>v.visible!==false);
  if(!x)return null;
  if(x.type==='solid')return csscolor(x.color);
  if(x.type==='gradient'&&x.stops){
    let stops=x.stops.map(v=>csscolor(v.color)+' '+((v.position||0)*100)+'%').join(',');
    return (x.kind==='radial'?'radial-gradient(circle,':'linear-gradient(180deg,')+stops+')';
  }
  issues.add('preenchimento '+x.type);return null;
}
function make(id,depth=0){
  const n=get(id),el=document.createElement(n?.type==='text'?'span':'div');
  if(!n||depth>32){issues.add('referencia/recursao');return el;}
  const style=el.style,trans=n.transform||[1,0,0,1,0,0];
  style.position='absolute';style.boxSizing='border-box';
  style.left=(trans[4]||0)+'px';style.top=(trans[5]||0)+'px';
  style.width=(n.width||0)+'px';style.height=(n.height||0)+'px';
  const bg=fill(n.fills);if(bg)style.background=bg;
  if(n.type==='ellipse')style.borderRadius='50%';
  if(n.corners?.radii)style.borderRadius=n.corners.radii.map(a=>a+'px').join(' ');
  if(n.clip)style.overflow='hidden';
  if(n.strokes?.length)style.border='1px solid '+(fill(n.strokes)||'transparent');
  if(n.type==='text'){
    el.textContent=n.characters||'';
    style.background='transparent';style.whiteSpace='pre-wrap';
    style.overflowWrap='break-word';
    style.fontFamily='Inter,Segoe UI,system-ui,sans-serif';
    style.fontSize=(n.style?.font_size||14)+'px';
    style.lineHeight=String((n.style?.line_height?.value||120)/100);
    style.color=fill(n.fills)||'#111';
    if(/bold/i.test(n.style?.font_style||''))style.fontWeight='700';
    if(/semi/i.test(n.style?.font_style||''))style.fontWeight='600';
  }
  if(['vector','line','booleanOp','polygon','star'].includes(n.type)){
    issues.add('geometria vetorial');
    style.background='transparent';
  }
  if(n.layout)issues.add('auto layout aproximado');
  if(trans[1]||trans[2])issues.add('rotacao');
  el.dataset.nodeId=String(n.id);el.title=n.name+' ['+n.type+']';
  (n.children||[]).forEach(child=>el.appendChild(make(child,depth+1)));
  return el;
}
screenIds.forEach((id,i)=>{
  const opt=document.createElement('option');
  opt.value=i;opt.textContent=get(id).name;sel.append(opt);
});
function render(index){
  issues.clear();
  const n=get(screenIds[index]);stage.replaceChildren();
  const el=make(n.id);el.style.position='relative';
  el.style.left='0';el.style.top='0';
  stage.style.width=(n.width||393)+'px';stage.style.height=(n.height||852)+'px';
  stage.append(el);sel.value=String(index);
  warnings.textContent='Conversao experimental: '+[...issues].join(', ')+'. Eventos e banco de dados nao foram gerados.';
}
sel.addEventListener('change',()=>render(Number(sel.value)));
document.getElementById('next').addEventListener('click',()=>render((Number(sel.value)+1)%screenIds.length));
document.getElementById('prev').addEventListener('click',()=>render((Number(sel.value)+screenIds.length-1)%screenIds.length));
render(0);
"""
(out/'app.js').write_text(js.replace('__DATA__',json.dumps(data,ensure_ascii=False,separators=(',',':'))),encoding='utf8')
(out/'index.html').write_text("""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="styles.css"><title>WMK Design para Web</title></head><body><main><h1>WMK Studio — Laboratorio Design para Web</h1><p>Documento real do projeto. Conversao aproximada de telas e elementos, nao um aplicativo full-stack.</p><nav><label for="sel">Tela:</label><select id="sel"></select><button id="prev">Anterior</button><button id="next">Proxima</button></nav><section class="viewport"><div id="stage"></div></section><p id="warnings"></p><p>Walney Moreira Klein — walneyk@hotmail.com</p></main><script src="app.js"></script></body></html>""",encoding='utf8')
(out/'styles.css').write_text("""*{box-sizing:border-box}body{background:#0B0217;color:#F5E9FF;font-family:Inter,Segoe UI,system-ui;margin:0;padding:20px}main{max-width:1100px;margin:auto}h1{color:#E6B3FF}nav{display:flex;gap:12px;align-items:center;margin:15px 0;flex-wrap:wrap}select,button{background:#30144f;color:white;border:1px solid #8055a2;padding:10px;border-radius:8px;font:inherit}button{cursor:pointer}button:hover{background:#8A2BE2}.viewport{background:#24113D;padding:25px;border:1px solid #70438e;border-radius:16px;overflow:auto}#stage{background:white;margin:auto;position:relative;overflow:hidden;border-radius:16px;box-shadow:0 18px 40px #0008}#warnings{color:#E6B3FF}""",encoding='utf8')
report={'source':src.name,'copy':'ridgeline-laboratorio.wmk','format':d['format'],'version':d['version'],'nodes':len(nodes),'types':types,'screens':[{'name':nodes[str(id)]['name'],'width':nodes[str(id)]['width'],'height':nodes[str(id)]['height']} for id in screens],'styles':len(d.get('styles',[])),'variable_collections':len(d.get('variables',{}).get('collections',[])),'variable_count':len(d.get('variables',{}).get('variables',[])),'limitations':['vetores complexos nao renderizados fielmente','Auto Layout simplificado','sem acoes de prototipo automatizadas','sem backend/banco','sem logica CRUD'],'note':'Copia .wmk e identica ao exemplo original .figcraft; metadado format=figcraft preservado.'}
(out/'relatorio-auditoria.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
(out/'LEIA-ME.md').write_text("""# WMK Laboratorio — Documento para Web
Este laboratorio usa uma copia exata de examples/ridgeline-app.figcraft renomeada para ridgeline-laboratorio.wmk, sem alterar o documento original. O metadado interno format=figcraft foi preservado.
## Executar
Abra index.html em navegador. Clique nas telas no seletor ou Anterior/Proxima.
## Limites
Os textos, geometrias simples e preenchimentos sao extraidos do documento. Vetores complexos, componentes aninhados, auto layout, efeitos e interacoes nao sao renderizados fielmente. Este e um teste de leitura e prototipagem, nao um app de producao.
## Proximo passo
Usar renderer SVG da engine e Code Connect para gerar componentes React/TypeScript, e definir eventos, dados e backend em contrato separado.
Credito WMK: Walney Moreira Klein - walneyk@hotmail.com. Origem FigCraft, ArtCraft Team.
""",encoding='utf8')
zpath=out.parent/'WMK-Laboratorio-Design-para-Web-PoC.zip'
with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(out.iterdir()):z.write(p,p.name)
with zipfile.ZipFile(zpath) as z:assert z.testzip() is None
print('DIR',out,'ZIP',zpath,'ZIP_BYTES',zpath.stat().st_size,'NODES',len(nodes),'SCREENS',len(screens))
