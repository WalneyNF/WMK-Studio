from pathlib import Path
import json
r=Path(r'D:\Ferramentas\figcraft')
p=r/'manuais'/'inventario-componentes-presets-rad.html'
s=p.read_text(encoding='utf8').replace('sete tipos de componente propostos','oito tipos de componente propostos')
p.write_text(s,encoding='utf8')
root=r/'wmk-rad-presets'
rg=json.loads((root/'registry.json').read_text(encoding='utf8'))
pr=json.loads((root/'examples/crud-clientes-v1.json').read_text(encoding='utf8'))
types={c['id']:c for c in rg['componentDefinitions']}
actions={'crud.new','crud.save','crud.delete','crud.cancel'}
def validate(node):
 t=node['component']
 if t not in types:raise ValueError('Unknown component '+t)
 specs=types[t].get('slots',{})
 for name,children in node.get('slots',{}).items():
  if name not in specs:raise ValueError('Unknown slot '+name)
  spec=specs[name]
  if not spec['min']<=len(children)<=spec['max']:raise ValueError('Cardinality')
  for child in children:
   if child['component'] not in spec['accept']:raise ValueError('Invalid hierarchy')
   validate(child)
 if t=='wmk.button' and node.get('props',{}).get('action') not in actions:raise ValueError('Invalid action')
validate(pr['composition'])
import copy
def rejected(change):
 p=copy.deepcopy(pr['composition']);change(p)
 try:validate(p)
 except ValueError:return True
 return False
assert rejected(lambda n:n['slots']['actions'][0]['slots']['buttons'][0].update(component='wmk.input'))
assert rejected(lambda n:n['slots']['content'][0]['slots']['fields'][0]['props'].update({'action':'crud.hack'}) if False else n['slots']['actions'][0]['slots']['buttons'][0]['props'].update(action='crud.hack'))
assert rejected(lambda n:n.update(component='unregistered.component'))
print('PRESET_POSITIVE_AND_3_NEGATIVE_TESTS_OK')
