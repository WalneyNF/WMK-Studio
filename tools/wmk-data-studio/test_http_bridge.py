from pathlib import Path
import os,subprocess,tempfile,time,urllib.request,urllib.error,json,socket
base=Path(r'D:\Ferramentas\figcraft\tools\wmk-data-studio')
with tempfile.TemporaryDirectory() as tmp:
 db=Path(tmp)/'wmk.sqlite'
 p=subprocess.Popen(['python',str(base/'server.py'),'--database',str(db),'--port','3369'],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
 def req(method,path,data=None,token=None):
  body=None if data is None else json.dumps(data).encode('utf8')
  headers={'Content-Type':'application/json'}
  if token:headers['X-WMK-Token']=token
  request=urllib.request.Request('http://127.0.0.1:3369'+path,method=method,data=body,headers=headers)
  try:
   with urllib.request.urlopen(request,timeout=3) as res:return res.status,res.read().decode('utf8')
  except urllib.error.HTTPError as error:return error.code,error.read().decode('utf8')
 try:
  for _ in range(100):
   if p.poll() is not None:raise RuntimeError('Server stopped: '+str(p.returncode))
   try:
    code,body=req('GET','/')
    if code==200:break
   except Exception:time.sleep(.1)
  else:raise RuntimeError('Server timeout')
  import re
  token=re.search(r'const TOKEN="([^"]+)";',body).group(1)
  assert token and '__WMK_TOKEN__' not in body
  assert req('GET','/api/health')[0]==200
  assert req('POST','/api/entities',{'name':'clientes'})[0]==403
  assert req('POST','/api/entities',{'name':'clientes','label':'Clientes'},token)[0]==201
  assert req('POST','/api/entities/clientes/fields',{'name':'nome','type':'string','required':True},token)[0]==201
  status,body=req('POST','/api/entities/clientes/records',{'nome':'Cliente teste'},token)
  assert status==201,(status,body)
  uid=json.loads(body)['id']
  assert req('GET','/api/entities/clientes/records')[0]==200
  status,body=req('GET','/api/export');exp=json.loads(body)
  assert status==200 and exp['schemaVersion']=='wmk-data-studio/v1'
  assert exp['dataModels'][0]['fields'][1]['name']=='nome'
  assert req('PUT','/api/entities/clientes/records/'+uid,{'nome':'Cliente alterado'},token)[0]==200
  assert 'Cliente alterado' in req('GET','/api/entities/clientes/records')[1]
  assert req('DELETE','/api/entities/clientes/records/'+uid,token=token)[0]==200
  assert 'Cliente alterado' not in req('GET','/api/entities/clientes/records')[1]
  Path(tmp,'wmk-data-models.json').write_text(json.dumps(exp),encoding='utf8')
  output=Path(tmp)/'react-result'
  r=Path(r'D:\Ferramentas\figcraft')
  args=['python',str(r/'tools/wmk-app-bridge/export.py'),str(r/'laboratorios/wmk-design-to-app/ridgeline-web-poc/ridgeline-laboratorio.wmk'),'--bindings',str(r/'tools/wmk-app-bridge/examples/ridgeline.bindings.json'),'--models',str(Path(tmp,'wmk-data-models.json')),'--out',str(output)]
  result=subprocess.run(args,capture_output=True,text=True,errors='replace',timeout=30)
  assert result.returncode==0,(result.stdout,result.stderr)
  manifest=json.loads((output/'wmk.manifest.json').read_text(encoding='utf8'))
  assert manifest['dataModels'][0]['id']=='clientes'
  assert manifest['dataModels'][0]['fields'][1]['name']=='nome'
  print('HTTP_API_CRUD_TOKEN_OK')
  print('DATA_STUDIO_TO_APP_BRIDGE_EXPORT_OK',result.stdout.strip())
 finally:
  p.terminate()
  try:p.wait(timeout=5)
  except subprocess.TimeoutExpired:p.kill()
