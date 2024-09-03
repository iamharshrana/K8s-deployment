from flask import Flask, request, jsonify
from pymongo import MongoClient, errors
from datetime import datetime
import os


app = Flask(__name__)


client = MongoClient(os.environ.get("MONGODB_URI", "mongodb://mongodb-service:27017/"))


db = client.flask_db


collection = db.data


@app.route('/')
def index():

    return f"Welcome to the Flask app! The current time is: {datetime.now()}"


@app.route('/data', methods=['GET', 'POST'])
def data():
    try:
        if request.method == 'POST':
            data = request.get_json()
            collection.insert_one(data)
            return jsonify({"status": "Data inserted"}), 201
        elif request.method == 'GET':

            data = list(collection.find({}, {"_id": 0}))

            return jsonify(data), 200
    except errors.PyMongoError as e:

        return jsonify({"error": str(e)}), 500
    except Exception as e:
        # Handle general errors
        return jsonify({"error": "An unexpected error occurred: " + str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
