"""Main entry point for the 3D calculator web application."""

from flask import Flask, render_template
from pathlib import Path


def create_app():
    """Create and configure the Flask application."""
    # Get the package directory
    package_dir = Path(__file__).parent

    app = Flask(
        __name__,
        template_folder=str(package_dir / "templates"),
        static_folder=str(package_dir / "static"),
    )

    # Configuration
    app.config["SECRET_KEY"] = "dev-secret-key-change-in-production"

    # Routes
    @app.route("/")
    def index():
        """Render the main calculator page."""
        return render_template("index.html")

    @app.route("/health")
    def health():
        """Health check endpoint."""
        return {"status": "healthy", "service": "calculator-3d"}

    return app


def main():
    """Run the application."""
    app = create_app()
    print("🧮 Starting 3D Calculator Web Application...")
    print("📍 Open your browser at: http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)


if __name__ == "__main__":
    main()
