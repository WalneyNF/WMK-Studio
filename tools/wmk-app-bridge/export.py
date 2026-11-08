#!/usr/bin/env python3
# WMK App Bridge v0.1 — conversor de arquivos .wmk/.figcraft
# Copyright (c) Walney Moreira Klein — walneyk@hotmail.com
# Depende apenas da biblioteca padrao Python; o app exportado usa npm.
import argparse
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

SCHEMA = "wmk-app-bridge/v1"
SUPPORTED_ACTIONS = {"screen.navigate"}
SUPPORTED_ROLES = {"input", "button"}
MAX_DOCUMENT_BYTES = 40 * 1024 * 1024
TEMPLATE = Path(__file__).resolve().parent / "react-template"

def load_document(path):
    if not path.is_file() or path.suffix.lower() not in (".wmk", ".figcraft"):
        raise ValueError("Informe um arquivo .wmk ou .figcraft existente")
    if not zipfile.is_zipfile(path):
        raise ValueError("O arquivo nao e um container ZIP valido")
    with zipfile.ZipFile(path) as archive:
        info = archive.getinfo("document.json")
        if info.file_size > MAX_DOCUMENT_BYTES:
            raise ValueError("document.json excede limite de seguranca")
        document = json.loads(archive.read(info))
    if not isinstance(document, dict) or not isinstance(document.get("nodes"), dict):
        raise ValueError("Documento sem nodes")
    if not isinstance(document.get("pages"), list):
        raise ValueError("Documento sem paginas")
    return document

def inspect(document):
    nodes = document["nodes"]
    screen_ids = []
    for pid in document["pages"]:
        page = nodes.get(str(pid))
        if not page:
            continue
        for child_id in page.get("children", []):
            n = nodes.get(str(child_id))
            if n and n.get("type") == "frame":
                screen_ids.append(child_id)
    if not screen_ids:
        raise ValueError("Nao ha Frames principais para exportacao")
    return screen_ids

def load_bindings(path, document, screens):
    if path is None:
        return {"schemaVersion":SCHEMA,"application":{"title":document.get("name", "WMK App"),"defaultScreen":screens[0]},"bindings":[],"dataModels":[]}
    raw = json.loads(path.read_text(encoding="utf-8"))
    if raw.get("schemaVersion") != SCHEMA:
        raise ValueError("Versao de schema nao suportada")
    nodes = document["nodes"]
    names = set()
    for b in raw.get("bindings", []):
        node_id = b.get("nodeId")
        if str(node_id) not in nodes:
            raise ValueError("Binding referencia nodeId inexistente: " + str(node_id))
        role = b.get("role")
        if role not in SUPPORTED_ROLES:
            raise ValueError("Role nao suportada: " + str(role))
        if role == "input":
            name = b.get("name")
            if not isinstance(name, str) or not re.fullmatch("[A-Za-z][A-Za-z0-9_]{0,64}", name):
                raise ValueError("Nome de input invalido")
        if role == "button":
            action = b.get("action", {})
            if action.get("type") not in SUPPORTED_ACTIONS:
                raise ValueError("Acao nao suportada")
            if action["type"] == "screen.navigate" and action.get("screenId") not in screens:
                raise ValueError("Destino da navegacao nao e Frame principal")
        key=(str(node_id),role)
        if key in names:
            raise ValueError("Binding duplicado")
        names.add(key)
    app=raw.get("application", {})
    if app.get("defaultScreen",screens[0]) not in screens:
        raise ValueError("Tela inicial invalida")
    for model in raw.get("dataModels", []):
        if not re.fullmatch("[A-Za-z][A-Za-z0-9_]{0,64}", model.get("id","")):
            raise ValueError("Nome de entidade invalido")
        field_names=set()
        for field in model.get("fields",[]):
            if field.get("type") not in ("string","number","boolean","email"):
                raise ValueError("Tipo de campo nao suportado")
            if not re.fullmatch("[A-Za-z][A-Za-z0-9_]{0,64}", field.get("name","")):
                raise ValueError("Nome de campo invalido")
            if field["name"] in field_names:
                raise ValueError("Campo duplicado")
            field_names.add(field["name"])
    return raw

def export(source, bindings, target, models=None):
    document=load_document(source)
    screen_ids=inspect(document)
    contract=load_bindings(bindings,document,screen_ids)
    if models is not None:
        model_data=json.loads(models.read_text(encoding="utf-8"))
        if model_data.get("schemaVersion") != "wmk-data-studio/v1":
            raise ValueError("Schema de modelos WMK Data Studio incompatível")
        imported=model_data.get("dataModels")
        if not isinstance(imported,list):raise ValueError("Lista de modelos inválida")
        existing=contract.get("dataModels",[])
        contract["dataModels"]=imported
        try:
            # Reaproveita a validacao dos IDs e tipos do contrato App Bridge.
            load_bindings_from_models=contract
            import tempfile
            with tempfile.TemporaryDirectory() as folder:
                temporary=Path(folder)/"bindings.json"
                temporary.write_text(json.dumps(load_bindings_from_models,ensure_ascii=False),encoding="utf-8")
                contract=load_bindings(temporary,document,screen_ids)
        except ValueError:
            contract["dataModels"]=existing
            raise
    if not TEMPLATE.exists():
        raise ValueError("Template React ausente")
    if target.exists() and any(target.iterdir()):
        raise ValueError("Destino nao vazio. Escolha uma pasta nova")
    target.mkdir(parents=True,exist_ok=True)
    shutil.copytree(TEMPLATE,target,dirs_exist_ok=True)
    src=target/"src"
    src.mkdir(exist_ok=True)
    design={"name":document.get("name","Sem titulo"),"nodes":document["nodes"],"screens":screen_ids}
    manifest={
        "schemaVersion":SCHEMA,
        "sourceFormat":document.get("format","unknown"),
        "sourceVersion":document.get("version"),
        "application":contract.get("application",{}),
        "screens":[{"id":sid,"name":document["nodes"][str(sid)]["name"],
                    "width":document["nodes"][str(sid)].get("width",0),
                    "height":document["nodes"][str(sid)].get("height",0)} for sid in screen_ids],
        "bindings":contract.get("bindings",[]),
        "dataModels":contract.get("dataModels",[]),
        "diagnostics":[
            "Conversao visual parcial: vetores, efeitos, prototipos e auto layout nao sao totalmente convertidos",
            "Bindings funcionais estao no contrato complementar, nao no arquivo WMK original",
            "Entidades sao demonstrativas e persistidas no navegador; nao ha backend"
        ]
    }
    (src/"design.json").write_text(json.dumps(design,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
    (src/"wmk.manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    (target/"wmk.manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    print("BRIDGE_OK",len(design["nodes"]),"nodes",len(screen_ids),"screens",len(manifest["bindings"]),"bindings")
    print("OUTPUT",target)

def main():
    parser=argparse.ArgumentParser(description="WMK App Bridge: .wmk -> manifesto + React TypeScript")
    parser.add_argument("source",type=Path)
    parser.add_argument("--bindings",type=Path)
    parser.add_argument("--models",type=Path,help="JSON exportado pelo WMK Data Studio")
    parser.add_argument("--out",required=True,type=Path)
    args=parser.parse_args()
    try:export(args.source,args.bindings,args.out,args.models)
    except (OSError,ValueError,KeyError,json.JSONDecodeError,zipfile.BadZipFile) as exc:
        print("BRIDGE_ERROR:",exc,file=sys.stderr)
        return 2
    return 0

if __name__=="__main__":
    raise SystemExit(main())
