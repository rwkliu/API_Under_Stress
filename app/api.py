from flask import Flask, request, jsonify
import mysql.connector
import uuid

app = Flask(__name__)


def connect_to_db():
    db = mysql.connector.connect(
        host="localhost",
        user="username",
        password="password123",
        database="warriors_db",
    )
    return db


@app.route("/")
def default():
    welcome_msg = "Welcome to API Under Stress!"
    return welcome_msg


# POST request that saves a new warrior entry into the database
@app.route("/warrior", methods=["POST"])
def create_warrior():
    db = connect_to_db()
    data = request.json

    # Perform input validation
    if "name" not in data or "dob" not in data or "fight_skills" not in data:
        return jsonify({"message": "Bad Request - Missing required fields"}), 400

    id = str(uuid.uuid4())
    name = data.get("name")
    dob = data.get("dob")
    fight_skills = data.get("fight_skills")

    cursor = db.cursor()
    sql = "INSERT INTO warriors (id, name, dob, fight_skills) VALUES (%s, %s, %s, %s)"
    values = (id, name, dob, str(fight_skills))

    try:
        cursor.execute(sql, values)
        db.commit()
        return jsonify({"message": "Warrior created successfully", "id": id}), 201
    except Exception as e:
        print("Error creating warrior:", e)
        db.rollback()
        return jsonify({"message": "Internal Server Error"}), 500
    finally:
        cursor.close()


# GET request that searches the database for entries that matches the given id
@app.route("/warrior/<id>", methods=["GET"])
def get_warrior(id):
    db = connect_to_db()
    cursor = db.cursor()
    sql = "SELECT * FROM warriors WHERE id = %s"
    val = (id,)

    try:
        cursor.execute(sql, val)
        result = cursor.fetchone()
        if result:
            return jsonify(result), 200
        else:
            return jsonify({"message": "Warrior not found"}), 404
    except Exception as e:
        print("Error retrieving warrior:", e)
        return jsonify({"message": "Internal Server Error"}), 500
    finally:
        cursor.close()


# GET request that searches the databases for entries that matches the given name
@app.route("/warrior", methods=["GET"])
def search_warriors():
    db = connect_to_db()
    search_term = request.args.get("t")
    if not search_term:
        return jsonify({"message": "Bad Request"}), 400

    cursor = db.cursor()
    sql = "SELECT * FROM warriors WHERE name LIKE %s LIMIT 50"
    val = ("%" + search_term + "%",)

    try:
        cursor.execute(sql, val)
        result = cursor.fetchall()
        return jsonify(result), 200
    except Exception as e:
        print("Error searching warriors:", e)
        return jsonify({"message": "Internal Server Error"}), 500
    finally:
        cursor.close()


# GET request that returns the number of warriors
@app.route("/counting-warriors", methods=["GET"])
def count_warriors():
    db = connect_to_db()
    cursor = db.cursor()
    sql = "SELECT COUNT(*) FROM warriors"

    try:
        cursor.execute(sql)
        result = cursor.fetchone()[0]
        return jsonify({"count": result}), 200
    except Exception as e:
        print("Error counting warriors:", e)
        return jsonify({"message": "Internal Server Error"}), 500
    finally:
        cursor.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
