// WMK App Bridge — backend local com SQLite real.
// Requires Node.js >= 22.13 (tested Node 26). Not intended for public internet.
import { createServer } from 'node:http';
import { DatabaseSync } from 'node:sqlite';
import { readFileSync, mkdirSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { randomUUID } from 'node:crypto';
const base=dirname(fileURLToPath(import.meta.url));
const manifest=JSON.parse(readFileSync(resolve(base,'../wmk.manifest.json'),'utf8'));
const ident=v=>{if(!/^[a-zA-Z][a-zA-Z0-9_]{0,64}$/.test(v))throw Error('Identificador inválido');return '"'+v+'"';};
const models=new Map();
for(const model of manifest.dataModels||[]){
 ident(model.id);
 if(models.has(model.id))throw Error('Entidade duplicada: '+model.id);
 const names=new Set(['id']);
 for(const field of model.fields||[]){
  ident(field.name);
  if(field.name!=='id'&&names.has(field.name))throw Error('Campo duplicado');
  if(!['string','email','number','boolean'].includes(field.type))throw Error('Tipo não permitido');
  names.add(field.name);
 }
 models.set(model.id,model);
}
const dbPath=resolve(base,process.env.WMK_DATABASE_PATH||'../data/wmk.sqlite');
mkdirSync(dirname(dbPath),{recursive:true});
const db=new DatabaseSync(dbPath);
db.exec('PRAGMA journal_mode=WAL; PRAGMA foreign_keys=ON;');
for(const model of models.values()){
 const cols=(model.fields||[]).filter(x=>x.name!=='id').map(f=>ident(f.name)+' '+(f.type==='number'?'REAL':f.type==='boolean'?'INTEGER':'TEXT')+(f.required?' NOT NULL':'')).join(', ');
 db.exec('CREATE TABLE IF NOT EXISTS '+ident(model.id)+' ("id" TEXT PRIMARY KEY'+(cols?', '+cols:'')+')');
}
function send(res,status,data){
 const body=JSON.stringify(data);
 res.writeHead(status,{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'});
 res.end(body);
}
async function readJSON(req){
 let length=0,parts=[];
 for await(const chunk of req){
  length+=chunk.length;
  if(length>1024*1024)throw Object.assign(new Error('Requisição excede 1 MB'),{status:413});
  parts.push(chunk);
 }
 try{return JSON.parse(Buffer.concat(parts).toString('utf8'));}
 catch{throw Object.assign(new Error('JSON inválido'),{status:400});}
}
function validate(model,payload){
 if(!payload||typeof payload!=='object'||Array.isArray(payload))throw Object.assign(new Error('Objeto obrigatório'),{status:400});
 const fields=(model.fields||[]).filter(f=>f.name!=='id');
 const permitted=new Set(fields.map(x=>x.name));
 for(const name of Object.keys(payload))if(!permitted.has(name))throw Object.assign(new Error('Campo desconhecido: '+name),{status:400});
 const out={};
 for(const field of fields){
  let value=payload[field.name];
  if(value===undefined||value===null||value===''){
   if(field.required)throw Object.assign(new Error('Campo obrigatório: '+field.name),{status:400});
   out[field.name]=null;continue;
  }
  if(field.type==='number'){
   if(typeof value!=='number'||!Number.isFinite(value))throw Object.assign(new Error('Número inválido: '+field.name),{status:400});
  }else if(field.type==='boolean'){
   if(typeof value!=='boolean')throw Object.assign(new Error('Booleano inválido: '+field.name),{status:400});
   value=value?1:0;
  }else{
   if(typeof value!=='string'||value.length>2000)throw Object.assign(new Error('Texto inválido: '+field.name),{status:400});
   if(field.type==='email'&&!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value))throw Object.assign(new Error('Email inválido'),{status:400});
  }
  out[field.name]=value;
 }
 return out;
}
function asObject(model,row){
 if(!row)return null;
 const out={...row};
 for(const field of model.fields||[])if(field.type==='boolean'&&row[field.name]!=null)out[field.name]=Boolean(row[field.name]);
 return out;
}
function getModel(name){return models.get(name);}
const server=createServer(async(req,res)=>{
 try{
  const path=new URL(req.url||'/', 'http://localhost').pathname;
  if(path==='/api/health'&&req.method==='GET')return send(res,200,{ok:true,service:'WMK App Bridge',database:'sqlite',entities:[...models.keys()]});
  const parts=path.split('/').filter(Boolean);
  if(parts[0]!=='api'||parts[1]!=='entities'||parts.length<3||parts.length>4)return send(res,404,{error:'Rota não encontrada'});
  const model=getModel(parts[2]);
  if(!model)return send(res,404,{error:'Entidade não encontrada'});
  const name=ident(model.id),fields=(model.fields||[]).filter(x=>x.name!=='id');
  const rowId=parts[3];
  if(!rowId&&req.method==='GET'){
   const rows=db.prepare('SELECT * FROM '+name+' ORDER BY rowid DESC LIMIT 500').all().map(row=>asObject(model,row));
   return send(res,200,{data:rows});
  }
  if(rowId&&req.method==='GET'){
   const row=db.prepare('SELECT * FROM '+name+' WHERE id=?').get(rowId);
   return row?send(res,200,{data:asObject(model,row)}):send(res,404,{error:'Registro não encontrado'});
  }
  if(!rowId&&req.method==='POST'){
   const values=validate(model,await readJSON(req)),id=randomUUID(),names=Object.keys(values);
   db.prepare('INSERT INTO '+name+' ('+['"id"',...names.map(ident)].join(',')+') VALUES ('+Array(names.length+1).fill('?').join(',')+')').run(id,...names.map(k=>values[k]));
   const row=db.prepare('SELECT * FROM '+name+' WHERE id=?').get(id);
   return send(res,201,{data:asObject(model,row)});
  }
  if(rowId&&req.method==='PUT'){
   const exists=db.prepare('SELECT id FROM '+name+' WHERE id=?').get(rowId);
   if(!exists)return send(res,404,{error:'Registro não encontrado'});
   const values=validate(model,await readJSON(req)),names=Object.keys(values);
   if(names.length)db.prepare('UPDATE '+name+' SET '+names.map(k=>ident(k)+'=?').join(',')+' WHERE id=?').run(...names.map(k=>values[k]),rowId);
   const row=db.prepare('SELECT * FROM '+name+' WHERE id=?').get(rowId);
   return send(res,200,{data:asObject(model,row)});
  }
  if(rowId&&req.method==='DELETE'){
   const changed=db.prepare('DELETE FROM '+name+' WHERE id=?').run(rowId).changes;
   return changed?send(res,200,{deleted:true}):send(res,404,{error:'Registro não encontrado'});
  }
  return send(res,405,{error:'Método não permitido'});
 }catch(e){const code=Number(e?.status)||500;console.error('[wmk-api]',e);send(res,code,{error:code===500?'Erro interno do servidor':e.message});}
});
const port=Number(process.env.PORT||3337);
server.listen(port,'127.0.0.1',()=>console.log('WMK_API_READY http://127.0.0.1:'+server.address().port));
function stop(){server.close(()=>{db.close();process.exit(0)});}
process.on('SIGINT',stop);process.on('SIGTERM',stop);
