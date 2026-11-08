from pathlib import Path
import subprocess,json,zipfile
r=Path(r'D:\Ferramentas\figcraft\laboratorios\wmk-design-to-app\ridgeline-web-poc')
p=subprocess.run(['node','--check',str(r/'app.js')],capture_output=True,text=True,timeout=30)
print('NODE_JS_SYNTAX',p.returncode, (p.stdout+p.stderr)[-1200:])
a=json.loads((r/'relatorio-auditoria.json').read_text(encoding='utf8'))
assert a['nodes']==349 and len(a['screens'])==3
assert zipfile.is_zipfile(r/'ridgeline-laboratorio.wmk')
index=(r/'index.html').read_text(encoding='utf8')
assert all(x in index for x in ['app.js','styles.css','id="stage"','id="sel"'])
assert p.returncode==0
print('AUDIT_JSON_AND_HTML OK; SCREENS:',[v['name'] for v in a['screens']])
z=r.parent/'WMK-Laboratorio-Design-para-Web-PoC.zip'
with zipfile.ZipFile(z) as archive:
 assert archive.testzip() is None
 print('ZIP_OK',len(archive.namelist()),'FILES')
