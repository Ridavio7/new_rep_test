from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")


def load_data():
    """Загружает данные из data.json"""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def validate_user_data(data: dict) -> bool:
    if not isinstance(data, dict):
        return False
    if (
        not data.get("name")
        or not isinstance(data["name"], str)
        or len(data["name"].strip()) == 0
    ):
        return False
    if data.get("age") and (not isinstance(data["age"], int) or data["age"] < 0):
        return False
    return True


@app.route("/", methods=["GET"])
def hello():
    return "Welcome to the User API!"


@app.route("/users", methods=["GET"])
def get_users():
    users = load_data()
    return jsonify(users)


@app.route("/users", methods=["POST"])
def add_user():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415

    user_data = request.json
    if not validate_user_data(user_data):
        return jsonify({"error": "Invalid user data"}), 400

    users = load_data()
    user_data["id"] = max([u.get("id", 0) for u in users], default=0) + 1
    users.append(user_data)
    save_data(users)

    return jsonify({"status": "OK", "user": user_data}), 201


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    users = load_data()
    user = next((u for u in users if u.get("id") == user_id), None)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user)


@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    users = load_data()
    original_count = len(users)
    users = [u for u in users if u.get("id") != user_id]
    if len(users) == original_count:
        return jsonify({"error": "User not found"}), 404
    save_data(users)
    return jsonify({"status": "OK", "deleted_id": user_id}), 200


def main():
    app.run(host="0.0.0.0", port=8080)


if __name__ == "__main__":
    main()
