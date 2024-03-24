from flask import Flask, request, jsonify, current_app
from bookmark import *
from tokenizer import *

app = Flask(__name__)

global classifier
classifier = Classifier()


@app.route("/api/v1/get_tags", methods=["POST"])
def get_tags():
    data = request.get_json()
    url = data["url"]
    # print(url)
    name, tags = current_app.ensure_sync(classifier.get_tags_for_website)(url)
    # print(name, tags)
    return jsonify({"name": name, "tags": tags})


if __name__ == "__main__":
    
    app.run(debug=True, port=5000)
