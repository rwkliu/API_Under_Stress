from flask import Flask, request, jsonify
from flask_caching import Cache
from datetime import datetime
from gevent import monkey
import mysql.connector
import uuid
from validators import validate_fight_skills

monkey.patch_all()

app = Flask(__name__)

# App config settings
app.json.sort_keys = False

# Configure the redis cache
app.config["CACHE_TYPE"] = "RedisCache"
app.config["CACHE_REDIS_HOST"] = "redis"
app.config["CACHE_REDIS_PORT"] = 6379
app.config["CACHE_REDIS_DB"] = 0

# Set up the Cache instance and initialize the cache
cache = Cache(app)
cache.init_app(app)


def connect_to_db():
    db = mysql.connector.connect(
        host="db",
        user="root",
        password="root",
        database="warriors_db",
    )
    return db


@app.route("/")
def default():
    welcome_msg = "Welcome to API Under Stress!"
    return welcome_msg


def validate_dob(dob):
    format = "%Y-%m-%d"
    try:
        return bool(datetime.strptime(dob, format))
    except ValueError:
        return False


# POST request that saves a new warrior entry into the database
@app.route("/warrior", methods=["POST"])
def create_warrior():
    db = connect_to_db()
    data = request.json

    # Check name, dob, and fight_skills keys are in the request body
    if "name" not in data or "dob" not in data or "fight_skills" not in data:
        return jsonify({"message": "Bad Request - Missing required fields"}), 400

    # Check valid dob format
    if validate_dob(data["dob"]) == False:
        return jsonify({"message": "Bad Request - Invalid date format"}), 400

    # Check the name is more than 100 characters
    if len(data["name"]) > 100:
        return jsonify({"message": "Bad Request - name is too long"}), 400

    # Validate fight_skills
    validation_error = validate_fight_skills(data["fight_skills"])
    if validation_error:
        return jsonify({"message": validation_error}), 400

    id = str(uuid.uuid4())
    name = data.get("name")
    dob = data.get("dob")
    fight_skills = data.get("fight_skills")

    fight_skills_list_string = ",".join(fight_skills)
    cursor = db.cursor()
    sql = "INSERT INTO warriors (id, name, dob, fight_skills) VALUES (%s, %s, %s, %s)"
    values = (id, name, dob, fight_skills_list_string)

    try:
        cursor.execute(sql, values)
        db.commit()
        cache.set(f"view//warrior/{id}", {}, timeout=60)

        return {}, 201, {"Location": f"/warrior/{id}"}

    except Exception as e:
        print("Error creating warrior:", e)
        db.rollback()
        return jsonify({"message": "Internal Server Error"}), 500
    finally:
        cursor.close()


# GET request that searches the database for entries that matches the given id
@app.route("/warrior/<id>", methods=["GET"])
@cache.cached(timeout=60)
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


def get_search_term():
    search_term = request.args.get("t")
    return search_term


def search_term_none():
    return request.args.get("t") == None


# GET request that searches for entries that matches the given search term
@app.route("/warrior", methods=["GET"])
@cache.cached(timeout=60, make_cache_key=get_search_term, unless=search_term_none)
def search_warriors():
    search_term = get_search_term()
    if not search_term:
        return jsonify({"message": "Bad Request"}), 400
    db = connect_to_db()

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
