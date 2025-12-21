# backend/app/main.py
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .routers import articles, cdc, dt  # <-- on importe le router

from ..database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="POC Articles")
app.include_router(dt.router)
app.include_router(articles.router)
app.include_router(cdc.router)

# Serveur frontend
frontend_dir = os.path.join(os.path.dirname(__file__), "../../frontend")
index_file = os.path.join(frontend_dir, "index.html")
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/")
def root():
    return FileResponse(index_file)

# ✅ Inclure les routes
app.include_router(articles.router)
