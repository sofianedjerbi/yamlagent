"""Flask application for Calc3D."""

from flask import Flask, jsonify, render_template, request

from calc3d.calculator import Calculator

app = Flask(__name__)
calculator = Calculator()


@app.route("/")
def index():
    """Render the main calculator page."""
    return render_template("index.html")


@app.route("/calculate", methods=["POST"])
def calculate():
    """Handle calculation requests."""
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    expression = data.get("expression", "")

    if not expression:
        return jsonify({"error": "No expression provided"}), 400

    result = calculator.evaluate_expression(expression)

    if isinstance(result, str) and result.startswith("Error"):
        return jsonify({"error": result}), 400

    return jsonify({"result": result})


def main():
    """Run the Flask development server."""
    print("🚀 Starting Calc3D server...")
    print("📱 Open http://localhost:5000 in your browser")
    app.run(debug=True, host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
