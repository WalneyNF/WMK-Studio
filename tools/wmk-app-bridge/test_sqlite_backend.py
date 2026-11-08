from pathlib import Path
import json,os,subprocess,tempfile,time,urllib.request,urllib.error
r=Path(r'D:\Ferramentas\figcraft')
root=r/'laboratorios/wmk-design-to-app/ridgeline-sqlite-v0.2'
server=root/'backend/server.mjs'
check=subprocess.run(['node','--check',str(server)],capture_output=True,text=True,timeout=20)
assert check.returncode==0,check.stderr
print('NODE_SYNTAX_OK')
with tempfile.TemporaryDirectory() as tmp:
 env={**os.environ,'PORT':'3347','WMK_DATABASE_PATH':str(Path(tmp)/'test.sqlite')}
 def boot():
  proc=subprocess.Popen(['node',str(server)],cwd=root,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
  for _ in range(100):
   if proc.poll() is not None:raise RuntimeError('Server exited '+str(proc.returncode)+' '+(proc.stdout.read() if proc.stdout else ''))
   try:
    with urllib.request.urlopen('http://127.0.0.1:3347/api/health',timeout=0.25) as res:return proc,json.load(res)
   except Exception:time.sleep(0.1)
  proc.terminate();raise RuntimeError('Server did not start')
 def call(method,path,data=None):
  body=None if data is None else json.dumps(data).encode('utf-8')
  req=urllib.request.Request('http://127.0.0.1:3347'+path,data=body,method=method,headers={'Content-Type':'application/json'})
  try:
   with urllib.request.urlopen(req,timeout=5) as res:return res.status,json.load(res)
  except urllib.error.HTTPError as exc:return exc.code,json.loads(exc.read())
 proc,health=boot()
 try:
  assert health['ok'] is True and 'trails' in health['entities']
  assert call('GET','/api/entities/trails')[1]['data']==[]
  code,created=call('POST','/api/entities/trails',{'title':'Trilha API','description':'Salvo no SQLite'})
  assert code==201,created
  rid=created['data']['id']
  assert call('GET','/api/entities/trails/'+rid)[1]['data']['title']=='Trilha API'
  assert call('POST','/api/entities/trails',{'description':'Sem nome'})[0]==400
  assert call('POST','/api/entities/trails',{'title':'Oi','unknown':'no'})[0]==400
  code,changed=call('PUT','/api/entities/trails/'+rid,{'title':'Trilha editada','description':'Persistente'})
  assert code==200 and changed['data']['title']=='Trilha editada'
  assert call('GET','/api/entities/trails')[1]['data'][0]['title']=='Trilha editada'
  print('CRUD_CREATE_READ_UPDATE_VALIDATION_OK',rid)
 finally:
  proc.terminate()
  try:proc.wait(timeout=5)
  except subprocess.TimeoutExpired:proc.kill()
 proc,health=boot()
 try:
  code,rows=call('GET','/api/entities/trails')
  assert len(rows['data'])==1 and rows['data'][0]['title']=='Trilha editada'
  code,deleted=call('DELETE','/api/entities/trails/'+rid)
  assert code==200 and deleted['deleted']
  assert call('GET','/api/entities/trails')[1]['data']==[]
  assert call('DELETE','/api/entities/trails/'+rid)[0]==404
  print('SQLITE_RESTART_PERSISTENCE_DELETE_OK')
 finally:
  proc.terminate()
  try:proc.wait(timeout=5)
  except subprocess.TimeoutExpired:proc.kill()
