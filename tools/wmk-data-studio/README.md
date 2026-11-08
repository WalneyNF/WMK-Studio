# WMK Data Studio v0.1

Editor visual local de banco SQLite; cria tabelas, campos, registros e exporta modelos de dados para o WMK App Bridge.

## Executar

Na raiz do fork:

    wmk-data-studio.cmd

Ou:

    python tools/wmk-data-studio/server.py --port 3366

Abra http://127.0.0.1:3366/ no navegador.

## Recursos implementados
- Nova entidade/tabela (nome tecnico e descricao).
- Novos campos: string, email, number, integer, boolean, date; opcao obrigatorio.
- Adicionar, listar, editar, pesquisar e excluir registros SQLite.
- Exportar JSON de entidades (wmk-data-models.json).
- App Bridge atualizado: recebe argumento --models para importar JSON do Data Studio.
- Token local de mutacao e escuta em 127.0.0.1.
- Banco do editor em tools/wmk-data-studio/data/wmk-studio.sqlite.

## Fluxo para gerar app React/TS

1. Modele clientes e seus campos, depois escolha Exportar modelos JSON.
2. Salve como wmk-data-models.json.
3. Use o App Bridge com arquivo de design, bindings e os modelos:

    python tools/wmk-app-bridge/export.py "meu-design.wmk" --bindings "meus-bindings.json" --models "wmk-data-models.json" --out "D:/Projetos/meu-app"

4. Na pasta do aplicativo exportado, execute npm install e npm run dev:full.

O esquema do banco é transportado para o projeto exportado; os registros reais do banco do editor nao sao exportados automaticamente.

## Testes executados

    python tools/wmk-data-studio/test_studio.py
    python tools/wmk-data-studio/test_http_bridge.py

Passaram: SQLite em disco, criacao e edicao de registros, persistencia, validacao, rejeicao de mutacoes sem token, verificacao sintatica JS da interface e exportacao de modelos ao WMK App Bridge.

## Limitacoes

Este modulo é um laboratorio web standalone no fork, ainda nao integrado a interface Rust do WMK Studio.
A UI nao teve teste end-to-end de cliques em um navegador real.
Sem relacoes, migrations de alteracao de esquema, regras de privacidade ou backup automatico.
O adaptador App Bridge converte os tipos integer/date para string por enquanto.
Nao usar em producao ou expor na internet sem autenticacao, autorizacao, auditoria e seguranca adequada.

Creditos: Walney Moreira Klein — walneyk@hotmail.com. WMK Studio/figcraft: preservar licencas originais.

## Versao 0.2 — Importacao WMK Studio

Nova aba Importacao WMK Studio. Abra um arquivo .wmk ou .figcraft e clique Ler projeto WMK.

A ferramenta apresenta telas Frame, arvore de componentes, posicoes, textos, cores e formas simples em HTML. Alguns vetores sao reconstruidos como poligonos SVG. Ha tambem a miniatura PNG original embutida no documento, quando disponivel.

O upload tem limite de 12 MB e document.json descompactado tem limite de 10 MB. Nenhum documento importado e gravado pelo servidor, nem altera tabelas SQLite. A operacao exige token local.

A previa e APROXIMADA: mascaras, Auto Layout, tipografia exata, instancias e curvas complexas podem diferir. A miniatura nao significa screenshots separados por Frame.

Teste: python tools/wmk-data-studio/test_import_wmk.py

Confirmado com o documento Ridgeline: 349 nos, tres telas e miniatura. HTTP import, rejeicao de ZIP invalido e teste de sintaxe JS aprovados. Comparacao visual no navegador ainda pendente.
