# WMK App Bridge v0.1

Exportador CLI experimental de documentos WMK/FigCraft para React + TypeScript + Vite, com manifesto versionado de componentes e eventos.

## Executar no Windows

1. Abra o terminal em D:\Ferramentas\figcraft.
2. Execute:

    python tools\wmk-app-bridge\export.py laboratorios\wmk-design-to-app\ridgeline-web-poc\ridgeline-laboratorio.wmk --bindings tools\wmk-app-bridge\examples\ridgeline.bindings.json --out laboratorios\wmk-design-to-app\minha-exportacao

3. Execute npm install e npm run build na pasta de saida.
4. Execute npm run dev para visualizar no navegador.

A pasta de saida deve estar vazia. O arquivo .wmk nao e alterado.

## Arquitetura
- export.py: parser ZIP/document.json, validador, gerador de app.
- examples/ridgeline.bindings.json: contrato de eventos de nós conhecidos.
- react-template: projeto React TypeScript reutilizavel.
- wmk.manifest.json: contrato portavel publicado no projeto de saida.
- src/design.json: arvore de documento para visualizacao.

## Recursos presentes
- Frames principais viram telas e o manifesto lista suas dimensoes.
- Inputs e botoes sao vinculados a nodeId real; screen.navigate validado contra Frames existentes.
- Entidade de dados opcional gera formulario demonstrativo de inclusao, busca e exclusao, persistido em localStorage.
- Suporte a outros arquivos .wmk com bindings proprios.

## Limitacoes
Esta versao nao modifica o executavel WMK Studio; usa um exportador externo. Nao implementa backend, SQLite, login, heranca de metodos nem conversao visual completa de vetores e auto-layout. O CRUD e apenas local. O teste no browser e a comparacao visual fiel ainda sao pendencias.

## Testes
python tools\wmk-app-bridge\test_bridge.py
npm run build na pasta exportada

Créditos: Walney Moreira Klein — walneyk@hotmail.com; fork WMK Studio baseado em FigCraft/ArtCraft Team. Licencas originais preservadas.
