"""Main Flask application for the 3D calculator."""

import os
from pathlib import Path
from flask import Flask, render_template, jsonify, request

# Get the directory containing this file
BASE_DIR = Path(__file__).parent

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)


@app.route("/")
def index():
    """Render the main calculator page."""
    return render_template("index.html")


@app.route("/api/calculate", methods=["POST"])
def calculate():
    """Handle calculation requests."""
    try:
        data = request.get_json()
        expression = data.get("expression", "")

        # Safely evaluate mathematical expressions
        # Only allow basic math operations
        allowed_chars = set("0123456789+-*/().^ ")
        if not all(c in allowed_chars for c in expression):
            return jsonify({"error": "Invalid characters in expression"}), 400

        # Replace ^ with ** for Python evaluation
        expression = expression.replace("^", "**")

        # Evaluate the expression
        result = eval(expression, {"__builtins__": {}}, {})

        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def main():
    """Run the Flask application."""
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "False").lower() == "true"

    print(f"\n🚀 Starting 3D Calculator")
    print(f"📱 Open your browser at: http://localhost:{port}\n")

    app.run(host="0.0.0.0", port=port, debug=debug)


if __name__ == "__main__":
    main()
