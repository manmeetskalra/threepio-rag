# settings.py
import os
from pathlib import Path

# repo root on Render is /opt/render/project/src
REPO_ROOT = Path(__file__).resolve().parent  # adjust if your file lives deeper

# Allow override via env var; default to a repo-local folder (fine for a POC)
CHROMA_DIR = Path(os.getenv("CHROMA_DIR", REPO_ROOT / "chroma_store"))
COLL_NAME  = os.getenv("COLL_NAME", "pdf_rag_demo")

# If you need different roots per dev:
SAHARSH_ROOT = os.getenv("SAHARSH_ROOT", str(REPO_ROOT))
MANME_ROOT   = os.getenv("MANME_ROOT",   str(REPO_ROOT))
