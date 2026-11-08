from pathlib import Path
import zipfile,json
r=Path(r'D:\Ferramentas\figcraft')
examples=list((r/'examples').glob('*.figcraft'))
print('EXAMPLES',[(p.name,p.stat().st_size) for p in examples])
for p in examples[:3]:
 print('\nEXAMPLE',p.name,'IS_ZIP',zipfile.is_zipfile(p))
 if zipfile.is_zipfile(p):
  with zipfile.ZipFile(p) as z:
   print('CONTENTS',[(q.filename,q.file_size) for q in z.infolist()[:12]])
   for k in z.namelist():
    if k.endswith('.json'):
     obj=json.loads(z.read(k))
     print('JSON_ROOT',k,'TYPE',type(obj).__name__,'KEYS',list(obj)[:30] if isinstance(obj,dict) else len(obj))
     if isinstance(obj,dict):
      for a,b in obj.items():
       print('KEY',a,'TYPE',type(b).__name__,'LEN',len(b) if hasattr(b,'__len__') else '-', 'SAMPLE',repr(b)[:380])
     break
