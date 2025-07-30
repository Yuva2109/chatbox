from flask import Flask, request, jsonify
from flask_cors import CORS
from auth import hash_password, verify_password
from database import store_user, fetch_offline_messages
from ClientRegistry import ClientRegistry

app = Flask(__name__)
CORS(app)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password required."}), 400

    success = store_user(username, password)
    if not success:
        return jsonify({"error": "Username already exists."}), 409

    return jsonify({"message": "Signup successful."}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password required."}), 400

    if not verify_password(username, password):
        return jsonify({"error": "Invalid credentials."}), 401

    return jsonify({"message": f"Welcome, {username}!"}), 200

@app.route('/users/online', methods=['GET'])
def get_online_users():
    users = ClientRegistry.get_all_usernames()
    return jsonify({"online_users": users}), 200

@app.route('/messages/<username>', methods=['GET'])
def get_offline_messages(username):
    if not username:
        return jsonify({"error": "Username required."}), 400

    messages = fetch_offline_messages(username)
    if not messages:
        return jsonify({"messages": []}), 200

    return jsonify({"messages": messages}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
