from pathlib import Path
import json,zipfile,subprocess
r=Path(r'D:\Ferramentas\figcraft')
root=r/'laboratorios/wmk-design-to-app/ridgeline-react-ts'
source=json.loads((root/'src/design.json').read_text(encoding='utf8'))
assert len(source['nodes'])==349 and len(source['screens'])==3
assert all(source['nodes'][str(k)]['type']=='frame' for k in source['screens'])
expected=['package.json','tsconfig.json','index.html','src/main.tsx','src/DesignCanvas.tsx','src/App.tsx','src/style.css','src/design.json','README.md']
for f in expected:assert (root/f).exists(),f
app=(root/'src/App.tsx').read_text(encoding='utf8')
assert all(x in app for x in ['localStorage','setIndex','setQuery','setDifficulty','toggle','DesignCanvas'])
design=(root/'src/DesignCanvas.tsx').read_text(encoding='utf8')
assert all(x in design for x in ['nodes','screens','children','fills','font_size'])
z=root.parent/'WMK-Ridgeline-React-TypeScript-v0.2.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
 for p in sorted(root.rglob('*')):
  if p.is_file() and not any(k in p.parts for k in ('node_modules','dist','.git')):
   archive.write(p,p.relative_to(root))
with zipfile.ZipFile(z) as archive:assert archive.testzip() is None
report={'source':'ridgeline-app.figcraft','screens':len(source['screens']),'nodes':len(source['nodes']),
'stack':'React 19 + TypeScript + Vite','structural_tests':'passed',
'installed_dependencies':(root/'node_modules').exists(),
'build_executed':False,
'note':'Code generation completed. npm installation pending or unsuccessful at verification time. Build and browser runtime not verified.',
'zip':str(z),'size_bytes':z.stat().st_size}
(root/'relatorio-fase2.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('STATIC_TESTS_OK','NODE_COUNT',report['nodes'],'SCREENS',report['screens'],'ZIP_BYTES',z.stat().st_size,'DEPS',report['installed_dependencies'])
