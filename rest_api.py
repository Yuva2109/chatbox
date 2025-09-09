from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"message": "API is working!"})

@app.route('/send', methods=['POST'])
def send_message():
    data = request.get_json()
    message = data.get('message')
    # Add your processing logic here
    return jsonify({"reply": f"Echo: {message}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Required by Render
    app.run(host='0.0.0.0', port=port)
