from flask import Flask, request, jsonify
from flask_caching import Cache
import mysql.connector
import uuid

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


# POST request that saves a new warrior entry into the database
@app.route("/warrior", methods=["POST"])
def create_warrior():
    db = connect_to_db()
    data = request.json

    # Check name, dob, and fight_skills keys are in the request body
    if "name" not in data or "dob" not in data or "fight_skills" not in data:
        return jsonify({"message": "Bad Request - Missing required fields"}), 400

    id = str(uuid.uuid4())
    name = data.get("name")
    dob = data.get("dob")
    fight_skills = data.get("fight_skills")

    # Check for empty skills or more than 20 skills
    if fight_skills == None:
        return jsonify({"message": "Bad Request - fight_skills cannot be empty"}), 400
    if len(fight_skills) > 20:
        return (
            jsonify(
                {
                    "message": "Bad Request - fight_skills cannot cannot have more than 20 skills"
                }
            ),
            400,
        )
    # Check for skills that are more than 250 characters
    if any(len(fight_skill) > 250 for fight_skill in fight_skills):
        return jsonify({"message": "Bad Request - a fight skill name is too long"}), 400
    # Check for total sum of the fight skill character lengths doesn't exceed max length
    max_skills_length = 5000
    if sum([len(fight_skill) for fight_skill in fight_skills]) > max_skills_length:
        return jsonify({"message": "Bad Request - fight skills length exceeded"}), 400
    # Check the name is more than 100 characters
    if len(name) > 100:
        return jsonify({"message": "Bad Request - name is too long"}), 400

    cursor = db.cursor()
    sql = "INSERT INTO warriors (id, name, dob, fight_skills) VALUES (%s, %s, %s, %s)"
    values = (id, name, dob, str(fight_skills))

    try:
        cursor.execute(sql, values)
        db.commit()
        return (
            jsonify(
                {
                    "message": "Warrior created successfully",
                    "id": id,
                    "name": name,
                    "dob": dob,
                    "fight_skills": fight_skills,
                }
            ),
            201,
        )
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


# GET request that searches for entries that matches the given search term
@app.route("/warrior", methods=["GET"])
@cache.cached(timeout=60, make_cache_key=get_search_term)
def search_warriors():
    db = connect_to_db()
    search_term = get_search_term()
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
