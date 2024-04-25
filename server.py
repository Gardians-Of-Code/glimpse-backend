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
import time
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

global models
models = Models()

# url_regex = re.compile(r"/^(https?|http?):\/\/(www\.)?[a-zA-Z0-9]+\.[a-zA-Z0-9]+(\/[a-zA-Z0-9]+)*$/")


@app.route("/api/v1/get_tags", methods=["POST"])
async def get_tags():
    data = request.get_json()
    url = data["url"]
    name, tags = await models.get_tags_for_website(url)
    return jsonify({"name": name, "tags": tags})


@app.route("/api/v1/summary", methods=["POST"])
async def get_summary():
    data = request.get_json()
    url = data["url"]
    summary = models.summarize_website(url)
    return jsonify({"summary": summary})


@app.route("/api/v1/estimate_reading_time", methods=["POST"])
async def get_estimated_reading_time():
    data = request.get_json()
    url = data["url"]
    time = models.estimate_reading_time(url)
    return jsonify({"reading_time": time})


@app.route("/api/v1/urldata", methods=["POST"])
async def get_url_data():
    data = request.get_json()
    url = data["url"]
    print(url)
    # if not url_regex.match(url):
    #     return jsonify({"error": "Invalid URL"}), 400
    
    response = requests.get(url)
    
    # # fetch the icon of the website
    # icon = requests.get(f"https://logo.clearbit.com/${url}")
    # if icon.status_code == 404:
    #     icon = requests.get(f"https://www.google.com/s2/favicons?domain=${url}")
    # icon = icon.content
    
    # Parse the HTML content
    # soup = BeautifulSoup(response.content, 'html.parser')
    # description = soup.find("meta", {"name": "description"})
    # if not description:
    #     description = "No description found"
    # else:
    #     description = description.get("content", "No description found")
    
    # get ml tags
    name, tags = await models.get_tags_for_website(response.url)
    
    data = {
        # "title": soup.title.string,
        "title": name,
        "url": response.url,
        "mlTags": tags,
    }
    
    return jsonify(data), response.status_code
        


@app.route("/api/v1/proxy", methods=["POST"])
async def get_proxy():
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

# Load the cache from a file
try:
    with open('cache.json', 'r') as f:
        cache = json.load(f)
except FileNotFoundError:
    cache = {}

@app.route("/api/v1/weather", methods=["POST"])
def get_weather():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    units = request.args.get("units")

    # Convert lat and lon to float and round to 1 decimal place
    lat = round(float(lat), 1)
    lon = round(float(lon), 1)

    # Create a cache key from the lat, lon, and units parameters
    cache_key = f"{lat},{lon},{units}"

    # If the data is in the cache and it's less than 1 hour old, send it
    if cache_key in cache and time.time() - cache[cache_key]['timestamp'] < 60 * 60:
        return jsonify(cache[cache_key]['data'])

    # If the data is not in the cache or it's more than 1 hour old, fetch it and store it in the cache
    try:
        response = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units={units}&appid={os.environ['WEATHER_API_KEY']}"
        )
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching weather: {e}")
        return jsonify({"error": "Error fetching weather"}), 500

    cache[cache_key] = {
        "data": response.json(),
        "timestamp": time.time(),
    }

    # Save the cache to a file
    with open('cache.json', 'w') as f:
        json.dump(cache, f, indent=2)

    return jsonify(response.json())

if __name__ == "__main__":
    load_dotenv()
    app.run(debug=False, port=5000)
