from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/health")
def health_check():
    """Health check endpoint.
    Returns a 200 OK status with a simple message.
    """
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
