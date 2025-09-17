import os
import tempfile
from fastapi import FastAPI, UploadFile, File, Form, Query, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from embedchain import App
import chromadb, logging

from settings import CHROMA_DIR, COLL_NAME
import yaml
from embedchain import App as ECApp

# Choose the best available constructor once
try:
    # Preferred on newer releases
    ec_app = ECApp.from_config(config_path="embedchain_config.yaml")
except AttributeError:
    # No .from_config on this App → try old Pipeline API
    try:
        from embedchain import Pipeline
    except ImportError:
        Pipeline = None

    if Pipeline and hasattr(Pipeline, "from_config"):
        ec_app = Pipeline.from_config(yaml_path="embedchain_config.yaml")
    else:
        # Last resort: construct a default App and rely on env vars
        ec_app = ECApp()

print("Embedchain initialized.")


# from embedchain import App as ECApp
# import yaml

# # Build ec_app once, with runtime compatibility
# try:
#     # Newer versions expose App.from_config(...)
#     ec_app = ECApp.from_config(config_path="embedchain_config.yaml")
# except AttributeError:
#     # Older versions: no from_config—fall back to manual init (or defaults)
#     # Option 1: just use defaults/env
#     ec_app = ECApp()
#     # Option 2: if your YAML holds fields ECApp(**cfg) understands, load & pass:
#     # with open("embedchain_config.yaml") as f:
#     #     cfg = yaml.safe_load(f) or {}
#     # ec_app = ECApp(**cfg)


# import yaml

# try:
#     # Newer docs path: App.from_config(config_path=...) or config=...
#     from embedchain import App as _App
#     if hasattr(_App, "from_config"):
#         App = _App
#         # If your file is YAML:
#         ec_app = App.from_config(config_path="embedchain_config.yaml")
#     else:
#         # Fallback to Pipeline API
#         from embedchain import App as Pipeline
#         ec_app = Pipeline.from_config(yaml_path="embedchain_config.yaml")
# except ImportError:
#     # Older builds may not have App at all
#     from embedchain import App as Pipeline
#     ec_app = Pipeline.from_config(yaml_path="embedchain_config.yaml")

print("Using chroma dir:", CHROMA_DIR)

# SAHARSH_ROOT = "/Users/saharshsamir/Desktop/everything/code/threepio-rag"
# MANME_ROOT = "/Users/manme/Desktop/code/threepio-rag"
# CHROMA_DIR = MANME_ROOT + "/chroma_store"
# COLL_NAME  = "pdf_rag_demo"

# Create/load the RAG app
# ec_app = App.from_config(config_path="embedchain_config.yaml")

STRICT_SYSTEM = (
    "You answer using the provided context snippets. "
    "If the context contains relevant information, provide a helpful answer based on that information. "
    "Only if the context is completely irrelevant or insufficient, reply: \"I don't know based on the provided PDF.\" "
    "Quote relevant lines when possible and return concise answers."
)

app = FastAPI(title="PDF Q&A (Embedchain)")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AskBody(BaseModel):
    question: str

# ---------- Upload ----------
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        return JSONResponse({"ok": False, "error": "Please upload a .pdf"}, status_code=400)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        # ADD metadata so it shows in citations (instead of /var/folders/tmp...)
        ec_app.add(tmp_path, data_type="pdf_file", metadata={"source": file.filename})
        os.remove(tmp_path)
        return {"ok": True, "message": f"Ingested {file.filename}"}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

# ---------- Ask ----------
@app.post("/ask")
async def ask(body: AskBody):
    question = body.question.strip()
    if not question:
        return JSONResponse({"ok": False, "error": "Empty question"}, status_code=400)

    try:
        answer, sources = ec_app.query(
            question,
            citations=True,
            system_prompt=STRICT_SYSTEM,
        )

        # format citations (pages 1-indexed)
        citations = []
        for chunk, meta in (sources or []):
            citations.append({
                "page": (meta.get("page") + 1) if isinstance(meta.get("page"), int) else meta.get("page"),
                "url": meta.get("url"),
                "doc_id": meta.get("doc_id"),
                "score": meta.get("score"),
                "source": meta.get("source"),
                "snippet": (chunk[:300] + "…") if chunk and len(chunk) > 300 else chunk
            })

        # if nothing retrieved, force safe fallback
        if not citations:
            answer = "I don't know based on the provided PDF."

        # RETURN the citations so you can see what was used
        return {"ok": True, "answer": answer, "citations": citations}

    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

# ---------- Debug: peek DB ----------
@app.get("/debug/vdb")
def debug_vdb(peek: int = Query(5, ge=1, le=20)):
    try:
        client = chromadb.PersistentClient(path=CHROMA_DIR)
        coll = client.get_or_create_collection(name=COLL_NAME)
        cnt = coll.count()
        try:
            sample = coll.peek(limit=peek)   # chroma >= 0.5
        except TypeError:
            sample = coll.peek(peek)         # older chroma
        rows = []
        docs  = sample.get("documents", [])
        metas = sample.get("metadatas", [])
        for i, doc in enumerate(docs):
            md = (metas[i] if i < len(metas) else {}) or {}
            rows.append({
                "i": i,
                "text_len": len(doc or ""),
                "page": (md.get("page") + 1) if isinstance(md.get("page"), int) else md.get("page"),
                "source": md.get("source"),
                "snippet": (doc[:200] + "…") if doc and len(doc) > 200 else doc
            })
        return {"collection": COLL_NAME, "count": cnt, "peek": rows}
    except Exception as e:
        logging.exception("debug_vdb failed")
        raise HTTPException(status_code=500, detail=str(e))

# ---------- Debug: retrieval only ----------
@app.post("/debug/retrieve")
async def debug_retrieve(body: AskBody, k: int = Query(5, ge=1, le=10)):
    try:
        # Use Embedchain retrieval if available
        hits = ec_app.retrieve(body.question)  # list[(text, metadata)]
        rows = []
        for t, m in (hits or [])[:k]:
            rows.append({
                "text_len": len(t or ""),
                "page": (m.get("page") + 1) if isinstance(m.get("page"), int) else m.get("page"),
                "source": m.get("source"),
                "score": m.get("score"),
                "snippet": (t[:300] + "…") if t and len(t) > 300 else t
            })
        return {"hits": rows, "count": len(hits or [])}
    except Exception:
        # Fallback: query Chroma directly with the same embedder
        try:
            client = chromadb.PersistentClient(path=CHROMA_DIR)
            coll = client.get_or_create_collection(name=COLL_NAME)
            qvec = ec_app.embedder.embed([body.question])[0]
            res = coll.query(query_embeddings=[qvec], n_results=k)
            rows = []
            docs  = res.get("documents", [[]])[0]
            metas = res.get("metadatas", [[]])[0]
            dists = res.get("distances", [[]])[0] if res.get("distances") else [None]*len(docs)
            for i, doc in enumerate(docs):
                md = (metas[i] if i < len(metas) else {}) or {}
                rows.append({
                    "text_len": len(doc or ""),
                    "page": (md.get("page") + 1) if isinstance(md.get("page"), int) else md.get("page"),
                    "source": md.get("source"),
                    "score": dists[i],
                    "snippet": (doc[:300] + "…") if doc and len(doc) > 300 else doc
                })
            return {"hits": rows, "count": len(rows)}
        except Exception as e:
            logging.exception("debug_retrieve fallback failed")
            raise HTTPException(status_code=500, detail=str(e))

