from flask import Flask, request, jsonify, Response
from flask_caching import Cache
from datetime import datetime
import mysql.connector
import uuid, json
from validators import validate_fight_skills

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

    # Validate fight_skills
    validation_error = validate_fight_skills(data['fight_skills'])
    if validation_error:
        return jsonify({"message": validation_error}), 400 

    # Check the name is not too long
    if len(data['name']) > 100:
        return jsonify({"message": "Bad Request - name is too long"}), 400
    
    id = str(uuid.uuid4())
    name = data.get("name")
    dob = data.get("dob")
    fight_skills = data.get("fight_skills")

    # Check valid dob format
    if validate_dob(dob) == False:
        return jsonify({"message": "Bad Request - Invalid date format"}), 400
    # Check the name is more than 100 characters
    if len(name) > 100:
        return jsonify({"message": "Bad Request - name is too long"}), 400

    # Check for empty skills
    if fight_skills is None:
        return jsonify({"message": "Bad Request - fight_skills cannot be empty"}), 400
    
    # Check for more than 20 fight skills
    if len(fight_skills) > 20:
        return jsonify({"message": "Bad Request - fight_skills cannot have more than 20 skills"}), 400
    try:
        if len(fight_skills) > 20:
            return (
                jsonify(
                    {
                        "message": "Bad Request - fight_skills cannot cannot have more than 20 skills"
                    }
                ),
                400,
            )
    except Exception:
        return jsonify({"message": "fight skill is not a string"}), 400
    # Check for skills that are more than 250 characters
    if any(len(fight_skill) > 250 for fight_skill in fight_skills):
        return jsonify({"message": "Bad Request - a fight skill name is too long"}), 400
    # Check for total sum of the fight skill character lengths doesn't exceed max length
    max_skills_length = 5019
    if sum([len(fight_skill) for fight_skill in fight_skills]) > max_skills_length:
        return jsonify({"message": "Bad Request - fight skills length exceeded"}), 400

    fight_skills_list_string = ",".join(fight_skills)
    cursor = db.cursor()
    sql = "INSERT INTO warriors (id, name, dob, fight_skills) VALUES (%s, %s, %s, %s)"
    values = (id, name, dob, fight_skills_list_string)

    try:
        cursor.execute(sql, values)
        db.commit()

        # Fetch the inserted record
        cursor.execute("SELECT * FROM warriors WHERE id = %s", (id,))
        inserted_warrior = cursor.fetchone()

        # Construct the response
        response_data = {
            "id": inserted_warrior[0],
            "name": inserted_warrior[1],
            "dob": inserted_warrior[2],
            "fight_skills": inserted_warrior[3].split(',')
        }

        resp = jsonify(response_data)
        resp.status_code = 201
        resp.headers["location"] = f"/warrior/{id}"
        return resp

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
