#!/usr/bin/env python3
"""WMK Data Studio 0.1 — banco visual SQLite local, sem dependencias."""
from __future__ import annotations
import argparse
import json
import re
import secrets
import sqlite3
import threading
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit, unquote
from uuid import uuid4

BASE = Path(__file__).resolve().parent
TYPES = {"string": "TEXT", "email": "TEXT", "number": "REAL", "integer": "INTEGER", "boolean": "INTEGER", "date": "TEXT"}
IDENT = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,63}$")
MAX_BODY=1024*1024
def ident(s):
    if not isinstance(s,str) or not IDENT.fullmatch(s) or s.lower().startswith("sqlite_") or s.lower().startswith("wmk_"):
        raise ValueError("Identificador de tabela/campo inválido")
    return '"'+s+'"'
def as_object(data):
    if not isinstance(data,dict): raise ValueError("Envie objeto JSON")
    return data
class Store:
    def __init__(self,path):
        self.path=Path(path)
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.db=sqlite3.connect(self.path, check_same_thread=False)
        self.db.row_factory=sqlite3.Row
        self.lock=threading.RLock()
        with self.db:
            self.db.execute("PRAGMA foreign_keys=ON")
            self.db.execute("""CREATE TABLE IF NOT EXISTS wmk_entities (
                name TEXT PRIMARY KEY, label TEXT NOT NULL
            )""")
            self.db.execute("""CREATE TABLE IF NOT EXISTS wmk_fields (
                entity TEXT NOT NULL REFERENCES wmk_entities(name),
                name TEXT NOT NULL, kind TEXT NOT NULL, required INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY(entity,name)
            )""")
    def close(self):self.db.close()
    def entities(self):
        with self.lock:
            all_entities=self.db.execute("SELECT name,label FROM wmk_entities ORDER BY name").fetchall()
            return [{"id":e["name"],"label":e["label"],"fields":[{"name":f["name"],"type":f["kind"],"required":bool(f["required"])}
                for f in self.db.execute("SELECT name,kind,required FROM wmk_fields WHERE entity=? ORDER BY rowid",(e["name"],))]}
                for e in all_entities]
    def fielddefs(self,entity):
        fields=self.db.execute("SELECT name,kind,required FROM wmk_fields WHERE entity=? ORDER BY rowid",(entity,)).fetchall()
        if self.db.execute("SELECT 1 FROM wmk_entities WHERE name=?",(entity,)).fetchone() is None:
            raise KeyError("Entidade não encontrada")
        return [dict(f) for f in fields]
    def create_entity(self,payload):
        x=as_object(payload)
        name=x.get("name");ident(name)
        label=str(x.get("label") or name)[:120]
        with self.lock,self.db:
            self.db.execute("INSERT INTO wmk_entities(name,label) VALUES (?,?)",(name,label))
            self.db.execute("CREATE TABLE "+ident(name)+" (id TEXT PRIMARY KEY)")
        return {"name":name,"label":label}
    def add_field(self,entity,payload):
        x=as_object(payload)
        name=x.get("name");ident(name)
        if name.lower()=="id":raise ValueError("Campo id já é gerenciado automaticamente")
        kind=x.get("type")
        if kind not in TYPES:raise ValueError("Tipo de campo não suportado")
        required=bool(x.get("required",False))
        with self.lock,self.db:
            self.fielddefs(entity)
            if self.db.execute("SELECT 1 FROM wmk_fields WHERE entity=? AND name=?",(entity,name)).fetchone():
                raise ValueError("Campo já existente")
            # New NOT NULL columns on populated tables need a default or migration.
            count=self.db.execute("SELECT count(*) FROM "+ident(entity)).fetchone()[0]
            if required and count>0:
                raise ValueError("Não é possível adicionar campo obrigatório em tabela com dados sem migração")
            self.db.execute("ALTER TABLE "+ident(entity)+" ADD COLUMN "+ident(name)+" "+TYPES[kind]+(" NOT NULL" if required else ""))
            self.db.execute("INSERT INTO wmk_fields(entity,name,kind,required) VALUES (?,?,?,?)",(entity,name,kind,int(required)))
        return {"name":name,"type":kind,"required":required}
    def normalize(self,entity,data):
        data=as_object(data)
        fields=self.fielddefs(entity)
        permitted={f["name"] for f in fields}
        if any(k not in permitted for k in data):raise ValueError("Campo não declarado no esquema")
        result={}
        for f in fields:
            name,kind=f["name"],f["kind"]
            v=data.get(name,None)
            if v in (None,""):
                if f["required"]:raise ValueError("Campo obrigatório: "+name)
                result[name]=None
                continue
            if kind in ("string","email","date"):
                if not isinstance(v,str) or len(v)>2000:raise ValueError("Texto inválido: "+name)
                if kind=="email" and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+",v):raise ValueError("E-mail inválido")
                if kind=="date" and not re.fullmatch(r"\d{4}-\d{2}-\d{2}",v):raise ValueError("Use data AAAA-MM-DD")
            elif kind in ("number","integer"):
                if isinstance(v,bool) or not isinstance(v,(int,float)) or kind=="integer" and not isinstance(v,int):
                    raise ValueError("Número inválido: "+name)
            elif kind=="boolean":
                if not isinstance(v,bool):raise ValueError("Booleano inválido: "+name)
                v=int(v)
            result[name]=v
        return result
    def records(self,entity):
        with self.lock:
            self.fielddefs(entity)
            rows=self.db.execute("SELECT * FROM "+ident(entity)+" ORDER BY rowid DESC LIMIT 250").fetchall()
            result=[dict(row) for row in rows]
            bools={x["name"] for x in self.fielddefs(entity) if x["kind"]=="boolean"}
            for row in result:
                for name in bools:
                    if row[name] is not None:row[name]=bool(row[name])
            return result
    def create_record(self,entity,payload):
        with self.lock,self.db:
            fields=self.normalize(entity,payload);uid=str(uuid4())
            names=list(fields.keys())
            sql="INSERT INTO "+ident(entity)+" ("+",".join(['"id"']+[ident(x) for x in names])+") VALUES ("+",".join(["?"]*(len(names)+1))+")"
            self.db.execute(sql,[uid]+[fields[x] for x in names])
            return {"id":uid}
    def update_record(self,entity,uid,payload):
        with self.lock,self.db:
            fields=self.normalize(entity,payload)
            if self.db.execute("SELECT 1 FROM "+ident(entity)+" WHERE id=?",(uid,)).fetchone() is None:raise KeyError("Registro não encontrado")
            if fields:
                self.db.execute("UPDATE "+ident(entity)+" SET "+",".join(ident(k)+"=?" for k in fields)+" WHERE id=?",
                    list(fields.values())+[uid])
            return {"id":uid}
    def delete_record(self,entity,uid):
        with self.lock,self.db:
            self.fielddefs(entity)
            changed=self.db.execute("DELETE FROM "+ident(entity)+" WHERE id=?",(uid,)).rowcount
            if not changed:raise KeyError("Registro não encontrado")
            return {"deleted":True}
    def export(self):
        return {"schemaVersion":"wmk-data-studio/v1",
            "dataModels":[{"id":e["id"],"fields":[{"name":"id","type":"string","required":True}]+[
                {"name":f["name"],"type":f["type"] if f["type"] in ("string","email","number","boolean") else "string",
                 "required":f["required"]} for f in e["fields"]]} for e in self.entities()],
            "diagnostics":["Tipos integer/date são convertidos para string no App Bridge v0.2; gerador precisa suportá-los nativamente."]}
class Handler(BaseHTTPRequestHandler):
    store=None;token=None
    def log_message(self,fmt,*args):pass
    def send_json(self,status,payload):
        body=json.dumps(payload,ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Content-Length",str(len(body)))
        self.send_header("Cache-Control","no-store")
        self.send_header("X-Content-Type-Options","nosniff")
        self.end_headers();self.wfile.write(body)
    def read_body(self):
        n=int(self.headers.get("Content-Length","0"))
        if n<1 or n>MAX_BODY:raise ValueError("JSON ausente ou excede 1 MB")
        return json.loads(self.rfile.read(n))
    def dispatch(self):
        method=self.command
        path=urlsplit(self.path).path
        if method=="GET" and path=="/":
            body=(BASE/"index.html").read_text(encoding="utf-8").replace("__WMK_TOKEN__",self.token).encode()
            self.send_response(200);self.send_header("Content-Type","text/html; charset=utf-8")
            self.send_header("Content-Length",str(len(body)))
            self.send_header("Cache-Control","no-store");self.end_headers();self.wfile.write(body);return
        if method=="GET" and path=="/api/health":return self.send_json(200,{"ok":True,"engine":"sqlite","tool":"WMK Data Studio"})
        if method=="GET" and path=="/api/schema":return self.send_json(200,{"entities":self.store.entities()})
        if method=="GET" and path=="/api/export":return self.send_json(200,self.store.export())
        segments=[unquote(x) for x in path.strip("/").split("/")]
        if method not in ("GET",) and self.headers.get("X-WMK-Token")!=self.token:
            return self.send_json(403,{"error":"Token local obrigatório"})
        if segments==["api","entities"] and method=="POST":
            return self.send_json(201,self.store.create_entity(self.read_body()))
        if len(segments)==4 and segments[:2]==["api","entities"] and segments[3]=="fields" and method=="POST":
            return self.send_json(201,self.store.add_field(segments[2],self.read_body()))
        if len(segments)==4 and segments[:2]==["api","entities"] and segments[3]=="records":
            if method=="GET":return self.send_json(200,{"rows":self.store.records(segments[2])})
            if method=="POST":return self.send_json(201,self.store.create_record(segments[2],self.read_body()))
        if len(segments)==5 and segments[:2]==["api","entities"] and segments[3]=="records":
            if method=="PUT":return self.send_json(200,self.store.update_record(segments[2],segments[4],self.read_body()))
            if method=="DELETE":return self.send_json(200,self.store.delete_record(segments[2],segments[4]))
        return self.send_json(404,{"error":"Rota não encontrada"})
    def do_GET(self):self.handle_req()
    def do_POST(self):self.handle_req()
    def do_PUT(self):self.handle_req()
    def do_DELETE(self):self.handle_req()
    def handle_req(self):
        try:self.dispatch()
        except KeyError as e:self.send_json(404,{"error":str(e)})
        except (ValueError,sqlite3.IntegrityError,sqlite3.OperationalError,json.JSONDecodeError) as e:self.send_json(400,{"error":str(e)})
        except Exception as e:
            print("WMK_DATA_ERROR",repr(e))
            self.send_json(500,{"error":"Falha interna"})
def serve(database,port):
    store=Store(database)
    token=secrets.token_urlsafe(24)
    class LocalHandler(Handler):pass
    LocalHandler.store=store;LocalHandler.token=token
    server=ThreadingHTTPServer(("127.0.0.1",port),LocalHandler)
    print("WMK_DATA_STUDIO http://127.0.0.1:"+str(server.server_port),flush=True)
    try:server.serve_forever()
    finally:server.server_close();store.close()
if __name__=="__main__":
    cli=argparse.ArgumentParser()
    cli.add_argument("--database",type=Path,default=BASE/"data/wmk-studio.sqlite")
    cli.add_argument("--port",type=int,default=3366)
    args=cli.parse_args()
    serve(args.database,args.port)
