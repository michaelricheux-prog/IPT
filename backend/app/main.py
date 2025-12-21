from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routers import bloc_router, planning_router, excel_router
from .database import engine, Base
from pathlib import Path

# Init DB
Base.metadata.create_all(bind=engine)

app = FastAPI(title="IPT Cloud Modulaire")

# Middleware
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Routers
app.include_router(bloc_router.router)
app.include_router(planning_router.router)
app.include_router(excel_router.router)



# Statiques
BASE_DIR = Path(__file__).resolve().parent.parent.parent 

STATIC_DIR = BASE_DIR / "static"
INDEX_FILE = BASE_DIR / "index.html"

# Montage du dossier static
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
else:
    print(f"⚠️ ATTENTION : Dossier static non trouvé à : {STATIC_DIR}")

@app.get("/")
def index():
    from fastapi.responses import FileResponse
    if INDEX_FILE.exists():
        return FileResponse(str(INDEX_FILE))
    return {"error": f"index.html introuvable à la racine {BASE_DIR}"}

