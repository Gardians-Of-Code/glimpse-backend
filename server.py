import base64
import re
from flask import Flask, request, jsonify, Response, current_app
from ml_models import *
from tokenizer import *
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

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


@app.route("/api/v1/urldata", methods=["POST"])
def get_url_data():
    data = request.get_json()
    url = data["url"]
    # if not url_regex.match(url):
    #     return jsonify({"error": "Invalid URL"}), 400
    
    response = requests.get(url)
    
    # fetch the icon of the website
    icon = requests.get(f"https://logo.clearbit.com/${url}")
    if icon.status_code == 404:
        icon = requests.get(f"https://www.google.com/s2/favicons?domain=${url}")
    icon = icon.content
    
    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    
    data = {
        "title": soup.title.string,
        "description": soup.find("meta", {"name": "description"})["content"],
        "image": base64.b64encode(icon).decode('utf-8'),
        "url": url
    }
    
    return jsonify(data), response.status_code
        


@app.route("/api/v1/proxy", methods=["POST"])
def get_proxy():
    data = request.get_json()
    url = data["url"]
    show_language = data["showLanguage"]
    headers = {"Accept-Language": show_language}

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Rewrite URLs of linked resources
        for element in soup.find_all(['link', 'script']):
            attr = 'href' if element.name == 'link' else 'src'
            if element.get(attr):
                resource_url = urljoin(url, element.get(attr))
                element[attr] = resource_url

        # Get the language of the page
        language = soup.html.get('lang')

        # TODO: Implement translation if language does not include show_language

        # Calculate the estimated reading time
        text = soup.body.get_text()
        word_count = len(text.split())
        reading_time = round(word_count / 200)  # 200 is the average reading speed in words per minute

        response = Response(soup.prettify())
        response.headers["x-reading-time"] = str(reading_time)
        response.headers["Access-Control-Expose-Headers"] = "x-reading-time"
        return response
    except Exception as e:
        return jsonify({"error": "Error fetching url"}), 500

@app.route("/api/v1/weather", methods=["POST"])
def get_weather():
    data = request.get_json()
    lat = float(data["lat"])
    lon = float(data["lon"])    
    units = data["units"]
    response = requests.get(f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=minutely&appid={os.environ['WEATHER_API_KEY']}&units={units}")
    return jsonify(response.json()), response.status_code


if __name__ == "__main__":
    load_dotenv()
    app.run(debug=False, port=3000)
