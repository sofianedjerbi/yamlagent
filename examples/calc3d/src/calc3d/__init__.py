"""Calc3D - A beautiful 3D calculator web application."""

__version__ = "0.1.0"


def main() -> None:
    """Entry point for the calc3d application."""
    import uvicorn

    print("Starting Calc3D server...")
    print("Open your browser at http://localhost:8000")
    uvicorn.run(
        "calc3d.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
