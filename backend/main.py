import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from src.api.endpoints import router as api_router
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title="AI-Coach Backend")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

app.include_router(api_router)

# PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend", "dist")
# app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIR, "assets")), name="assets")

# @app.get("/")
# async def read_index():
#     """Serves the main index.html file from the frontend build folder."""
#     return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))