from pathlib import Path
import importlib.util,json,tempfile,copy
m=Path(r'D:\Ferramentas\figcraft\tools\wmk-app-bridge\export.py')
spec=importlib.util.spec_from_file_location('wmk_bridge_export',m)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
src=Path(r'D:\Ferramentas\figcraft\laboratorios\wmk-design-to-app\ridgeline-web-poc\ridgeline-laboratorio.wmk')
bd=Path(r'D:\Ferramentas\figcraft\tools\wmk-app-bridge\examples\ridgeline.bindings.json')
doc=mod.load_document(src);screens=mod.inspect(doc);orig=json.loads(bd.read_text(encoding='utf8'))
assert len(doc['nodes'])==349 and len(screens)==3
assert len(mod.load_bindings(bd,doc,screens)['bindings'])==5
with tempfile.TemporaryDirectory() as temp:
 p=Path(temp)/'bindings.json'
 def bad(change):
  d=copy.deepcopy(orig);change(d);p.write_text(json.dumps(d),encoding='utf8')
  try:mod.load_bindings(p,doc,screens)
  except ValueError:return True
  return False
 assert bad(lambda d:d['bindings'][0].update(nodeId=999999))
 assert bad(lambda d:d['bindings'][1]['action'].update(screenId=999999))
 assert bad(lambda d:d['bindings'][1]['action'].update(type='shell.execute'))
 assert bad(lambda d:d.update(schemaVersion='unsupported-v900'))
 assert bad(lambda d:d['dataModels'][0]['fields'][1].update(type='python'))
 assert bad(lambda d:d['bindings'].append(copy.deepcopy(d['bindings'][0])))
print('PASS: original, five bindings and six invalid inputs rejected')
