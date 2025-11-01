"""FastAPI application setup for Calc3D."""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Get the package directory
BASE_DIR = Path(__file__).resolve().parent

# Initialize FastAPI app
app = FastAPI(
    title="Calc3D",
    description="A beautiful 3D calculator web application",
    version="0.1.0",
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Setup templates
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the home page with the 3D calculator."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "app": "calc3d", "version": "0.1.0"}
