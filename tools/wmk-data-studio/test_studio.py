from pathlib import Path
import sys, tempfile, json, subprocess, time, urllib.request, urllib.error
from importlib.util import spec_from_file_location, module_from_spec
path=Path(r'D:\Ferramentas\figcraft\tools\wmk-data-studio\server.py')
spec=spec_from_file_location('wmk_data',path);module=module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
with tempfile.TemporaryDirectory() as tmp:
 db=Path(tmp)/'wmk.sqlite';store=module.Store(db)
 try:
  assert store.entities()==[]
  store.create_entity({'name':'clientes','label':'Clientes'})
  store.add_field('clientes',{'name':'nome','type':'string','required':True})
  store.add_field('clientes',{'name':'email','type':'email','required':False})
  store.add_field('clientes',{'name':'ativo','type':'boolean','required':False})
  uid=store.create_record('clientes',{'nome':'Maria','email':'maria@example.com','ativo':True})['id']
  assert store.records('clientes')[0]['nome']=='Maria'
  assert store.records('clientes')[0]['ativo'] is True
  assert store.update_record('clientes',uid,{'nome':'Maria B','email':'maria@example.com','ativo':False})['id']==uid
  assert store.records('clientes')[0]['nome']=='Maria B'
  assert store.records('clientes')[0]['ativo'] is False
  model=store.export()
  assert model['dataModels'][0]['id']=='clientes'
  assert any(x['name']=='nome' for x in model['dataModels'][0]['fields'])
  for invalid in (
   lambda:store.create_entity({'name':'clientes;DROP TABLE'}),
   lambda:store.add_field('clientes',{'name':'id','type':'string'}),
   lambda:store.add_field('clientes',{'name':'bad','type':'unknown'}),
   lambda:store.create_record('clientes',{'nome':'','email':'a@example.com'}),
   lambda:store.create_record('clientes',{'nome':'João','email':'not-email'}),
   lambda:store.add_field('clientes',{'name':'cpf','type':'string','required':True})):
   try:invalid();raise AssertionError('Invalid request accepted')
   except ValueError:pass
  print('STORE_CREATE_UPDATE_SCHEMA_VALIDATION_OK')
 finally:store.close()
 store=module.Store(db)
 try:
  assert store.records('clientes')[0]['nome']=='Maria B'
  store.delete_record('clientes',uid)
  assert store.records('clientes')==[]
  print('SQLITE_PERSISTENCE_AND_DELETE_OK')
 finally:store.close()
# JS syntax check extracted from HTML by Node
html=path.parent/'index.html'
source=html.read_text(encoding='utf8')
script=source.split('<script>',1)[1].split('</script>',1)[0]
with tempfile.TemporaryDirectory() as tmp:
 js=Path(tmp)/'ui.js';js.write_text(script,encoding='utf8')
 result=subprocess.run(['node','--check',str(js)],capture_output=True,text=True,timeout=30)
 assert result.returncode==0,result.stderr
 print('BROWSER_JS_SYNTAX_OK')
