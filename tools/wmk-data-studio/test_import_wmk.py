from pathlib import Path
import io,zipfile,importlib.util,json,subprocess,tempfile,time,urllib.request,urllib.error,os,re
root=Path(r'D:\Ferramentas\figcraft\tools\wmk-data-studio')
source=Path(r'D:\Ferramentas\figcraft\laboratorios\wmk-design-to-app\ridgeline-web-poc\ridgeline-laboratorio.wmk')
spec=importlib.util.spec_from_file_location('wmk_import',root/'wmk_import.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
result=mod.parse_wmk(source.read_bytes())
assert result['nodeCount']==349 and len(result['screens'])==3
assert result['thumbnail'].startswith('data:image/png;base64,')
print('PARSER_REAL_WMK_OK',result['name'],result['nodeCount'],len(result['screens']))
for bad in [b'not-a-zip',b'']:
 try:mod.parse_wmk(bad);raise AssertionError('Invalid archive accepted')
 except ValueError:pass
print('BAD_ARCHIVES_REJECTED')
check=subprocess.run(['node','--check',str(root/'wmk-import.js')],capture_output=True,text=True,timeout=20)
assert check.returncode==0,check.stderr
print('PREVIEW_JS_SYNTAX_OK')
with tempfile.TemporaryDirectory() as folder:
 env=os.environ.copy()
 proc=subprocess.Popen(['python',str(root/'server.py'),'--database',str(Path(folder)/'test.sqlite'),'--port','3373'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,env=env)
 def request(method,path,data=None,token=''):
  headers={'Content-Type':'application/octet-stream'}
  if token:headers['X-WMK-Token']=token
  try:
   with urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:3373'+path,data=data,method=method,headers=headers),timeout=8) as response:
    return response.status,response.read()
  except urllib.error.HTTPError as err:return err.code,err.read()
 try:
  for _ in range(80):
   if proc.poll() is not None:raise RuntimeError('Server quit')
   try:code,html=request('GET','/');break
   except Exception:time.sleep(.1)
  else:raise AssertionError('Server unavailable')
  assert code==200 and b'Importa' in html
  token=re.search(rb'const TOKEN="([^"]+)";',html).group(1).decode('ascii')
  assert request('GET','/wmk-import.js')[0]==200
  assert request('POST','/api/wmk/import',source.read_bytes())[0]==403
  status,raw=request('POST','/api/wmk/import',source.read_bytes(),token)
  assert status==200,(status,raw[:200])
  item=json.loads(raw)
  assert item['nodeCount']==349 and len(item['screens'])==3
  assert request('POST','/api/wmk/import',b'not zip',token)[0]==400
  print('HTTP_IMPORT_OK','SCREENS',len(item['screens']),'BYTES',len(raw))
 finally:
  proc.terminate()
  try:proc.wait(timeout=5)
  except subprocess.TimeoutExpired:proc.kill()
