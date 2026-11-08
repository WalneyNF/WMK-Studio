"""Leitor seguro de documentos WMK/FigCraft para prévia de telas."""
import base64
import io
import json
import zipfile
from collections import Counter

MAX_UPLOAD=12*1024*1024
MAX_DOCUMENT=10*1024*1024
MAX_NODES=30000
MAX_THUMBNAIL=2*1024*1024

def parse_wmk(content:bytes):
    if len(content)>MAX_UPLOAD:raise ValueError("Arquivo .wmk excede 12 MB")
    if not zipfile.is_zipfile(io.BytesIO(content)):
        raise ValueError("Arquivo inválido: esperado container ZIP WMK/FigCraft")
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        files={x.filename:x for x in archive.infolist()}
        if "document.json" not in files:
            raise ValueError("Não encontrei document.json no arquivo WMK")
        info=files["document.json"]
        if info.file_size>MAX_DOCUMENT:raise ValueError("Documento descompactado excede 10 MB")
        if info.compress_size and info.file_size/info.compress_size>500:
            raise ValueError("Compressão de documento suspeita")
        doc=json.loads(archive.read(info).decode("utf-8"))
        if not isinstance(doc,dict) or not isinstance(doc.get("nodes"),dict):
            raise ValueError("Documento WMK sem árvore de nós")
        nodes=doc["nodes"]
        if len(nodes)>MAX_NODES:raise ValueError("Muitos nós no documento")
        if not isinstance(doc.get("pages"),list):raise ValueError("Documento sem páginas")
        screens=[]
        for pid in doc["pages"]:
            page=nodes.get(str(pid),{})
            for child in page.get("children",[]):
                node=nodes.get(str(child),{})
                if node.get("type")=="frame":
                    screens.append({"id":child,"name":node.get("name","Tela "+str(child)),
                      "width":node.get("width",0),"height":node.get("height",0)})
        thumbnail=None
        item=files.get("thumbnail.png")
        if item and item.file_size<=MAX_THUMBNAIL:
            thumbnail="data:image/png;base64,"+base64.b64encode(archive.read(item)).decode("ascii")
        return {"name":doc.get("name","Projeto WMK"),
            "format":doc.get("format","unknown"),"version":doc.get("version"),
            "screens":screens,
            "nodeCount":len(nodes),
            "counts":dict(Counter(n.get("type","unknown") for n in nodes.values() if isinstance(n,dict))),
            "nodes":nodes,"thumbnail":thumbnail,
            "diagnostics":["Prévia HTML experimental: alguns vetores, componentes/instâncias e Auto Layout podem apresentar diferenças do editor original.",
            "O arquivo é lido para visualização e não altera tabelas ou registros SQLite."]}
