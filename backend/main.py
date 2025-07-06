import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Import the router object from your new endpoints file
from src.api.endpoints import router as api_router

app = FastAPI(title="AI-Coach Backend")

# Include the API router. All routes defined in it (like /ws) are now part of the main app.
app.include_router(api_router)

# --- STATIC FILE SERVING ---
# This part is for serving the built React app in a production environment.

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# In production, Vite builds to a 'dist' folder.
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend", "dist")

# Mount the static assets directory from the build output
app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIR, "assets")), name="assets")

@app.get("/")
async def read_index():
    """Serves the main index.html file from the frontend build folder."""
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))