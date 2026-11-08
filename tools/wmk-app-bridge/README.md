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

## Versão 0.2 — SQLite real (implementado e testado)

O exportador produz um frontend React/TypeScript e backend Node.js com SQLite nativo. Requer Node >= 22.13; validado com Node 26.

Na pasta do projeto exportado, executar:

    npm install
    npm run dev:full

Acesse o endereço informado pelo Vite (geralmente http://localhost:5173/). A API escuta somente em 127.0.0.1:3337. Os dados ficam na pasta data/wmk.sqlite. Nunca exponha essa API publicamente: ela não tem autenticação.

Endpoints: GET /api/health; GET, POST /api/entities/:entity; GET, PUT e DELETE /api/entities/:entity/:id.

Testes executados: node --check no backend; POST, GET, PUT, DELETE, validação de entradas, rejeição de campos desconhecidos, reinício do servidor e confirmação de persistência no SQLite; tsc e build Vite.

Rodar regressão:

    python tools/wmk-app-bridge/test_bridge.py
    python tools/wmk-app-bridge/test_sqlite_backend.py

Pendente: Inspector gráfico dentro do WMK Studio, fidelidade de SVG/Auto Layout, autenticação e migrações do esquema. Este é um laboratório, não produto pronto para clientes.


### Teste de inicialização integrada (Vite + proxy HTTP + SQLite)
O arquivo test_vite_proxy.py inicia o servidor Node e o Vite em portas de teste, faz GET na página web e consulta /api/health através do proxy do Vite, depois encerra ambos os processos. Teste executado com sucesso em 08/11/2026. Ainda não equivale a teste de clique/renderização no navegador.

    python tools/wmk-app-bridge/test_vite_proxy.py
