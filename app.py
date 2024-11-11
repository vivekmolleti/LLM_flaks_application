from dotenv import load_dotenv
from flask import Flask
from flask import render_template
from flask import jsonify, request
import requests
from bs4 import BeautifulSoup
import test


load_dotenv()
app = Flask(__name__, static_folder='static')
cache = {}

@app.route('/')
def index():
    return render_template("home.html")

@app.route('/generate_response', methods=['POST'])
def generate_response():
    data = request.get_json()
    query = data.get('query')

    scraped_content = web_scrape(query)

    for result in scraped_content:
        test.scrape_and_embed_content(result["links"])

    best_response = test.get_best_match(query)

    return jsonify({"response":best_response})


def web_scrape(query):
    data = []
    params = {
        "q": query,  # query example
        "hl": "en",  # language
        "gl": "in",  # country of the search, UK -> United Kingdom
        "start": 0,  # number page by default up to 0
        "num": 20                     # parameter defines the maximum number of results to return.
    }
    headers = {
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }
    html = requests.get("https://www.google.com/search", params=params, headers= headers, timeout=30).text
    soup = BeautifulSoup(html, 'lxml')

    for result in soup.select(".tF2Cxc"):
        title = result.select_one(".DKV0Md").text
        try:
            snippet = result.select_one(".VwiC3b.yXK7lf.p4vkf.h1y5k.Hdw6tb span").text
        except AttributeError:
            snippet = None
        links = result.select_one(".yuRUbf a")["href"]
        data.append({
            "title": title,
            "snippet": snippet,
            "links": links
        })

        if soup.select_one(".d6cvqb a[id=pnnext]"):
            params["start"] += 10
        else:
            break
    return data


if __name__ == "__main__":
    app.run(debug=True)