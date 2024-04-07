from flask import Flask, request, jsonify, current_app
from ml_models import *
from tokenizer import *

app = Flask(__name__)

global models
models = Models()


@app.route("/api/v1/get_tags", methods=["POST"])
async def get_tags():
    data = request.get_json()
    url = data["url"]
    name, tags = await models.get_tags_for_website(url)
    return jsonify({"name": name, "tags": tags})


@app.route("/api/v1/summary", methods=["POST"])
def get_summary():
    data = request.get_json()
    url = data["url"]
    summary = models.summarize_website(url)
    return jsonify({"summary": summary})


@app.route("/api/v1/estimate_reading_time", methods=["POST"])
def get_estimated_reading_time():
    data = request.get_json()
    url = data["url"]
    time = models.estimate_reading_time(url)
    return jsonify({"reading_time": time})


if __name__ == "__main__":
    app.run(debug=False, port=5000)
