from pathlib import Path
import os,subprocess,tempfile,time,urllib.request
root=Path(r'D:\Ferramentas\figcraft\laboratorios\wmk-design-to-app\ridgeline-sqlite-v0.2')
with tempfile.TemporaryDirectory() as temp:
 env={**os.environ,'PORT':'3337','WMK_DATABASE_PATH':str(Path(temp)/'proxy-test.sqlite')}
 backend=subprocess.Popen(['node',str(root/'backend/server.mjs')],cwd=root,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 vite=subprocess.Popen(['node',str(root/'node_modules/vite/bin/vite.js'),'--host','127.0.0.1','--port','5199','--strictPort'],cwd=root,env=os.environ.copy(),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 try:
  for attempt in range(100):
   if backend.poll() is not None:raise RuntimeError('Backend saiu: '+str(backend.returncode))
   if vite.poll() is not None:raise RuntimeError('Vite saiu: '+str(vite.returncode))
   try:
    with urllib.request.urlopen('http://127.0.0.1:5199/',timeout=.35) as res:page=res.read().decode()
    with urllib.request.urlopen('http://127.0.0.1:5199/api/health',timeout=.35) as res:health=res.read().decode()
    break
   except Exception:time.sleep(.15)
  else:raise RuntimeError('Servidores nao responderam')
  assert '<div id="root"></div>' in page
  assert '"database":"sqlite"' in health and '"ok":true' in health
  print('VITE_HTTP_OK',len(page),'VITE_PROXY_API_SQLITE_OK',health[:150])
 finally:
  for proc in (vite,backend):
   proc.terminate()
   try:proc.wait(timeout=5)
   except subprocess.TimeoutExpired:proc.kill()
