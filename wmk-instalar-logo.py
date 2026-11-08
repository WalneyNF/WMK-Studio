from pathlib import Path
from PIL import Image
import shutil
root=Path(__file__).resolve().parent
source=root/'wmk-logo.png'
assets=root/'assets'/'app-icon'
if not source.is_file():
 print('ERRO: salve a logo aprovada como',source)
 raise SystemExit(2)
im=Image.open(source).convert('RGBA')
backup=assets/'backup-figcraft-original'
backup.mkdir(exist_ok=True)
targets=[]
for px in (16,32,48,64,128,256,512,1024):
 targets.append((assets/f'figcraft-{px}.png',px))
for px in (128,256):
 targets.append((assets/'hicolor'/f'{px}x{px}'/'apps'/'ai.storyteller.figcraft.png',px))
for p,size in targets:
 p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():
  orig=backup/(str(p.relative_to(assets)).replace('/','_').replace('\\','_'))
  if not orig.exists():shutil.copy2(p,orig)
 im.resize((size,size),Image.Resampling.LANCZOS).save(p,'PNG')
 print('LOGO',p)
ico=assets/'figcraft.ico'
if ico.exists() and not (backup/'figcraft.ico').exists():shutil.copy2(ico,backup/'figcraft.ico')
im.save(ico,format='ICO',sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])
print('ICON OK',ico)
print('Logo WMK instalada, recompilar para incorporar ao executavel.')
