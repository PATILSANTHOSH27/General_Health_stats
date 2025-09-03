from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# -------- Static Mapping of Diseases to WHO URLs --------
DISEASE_OVERVIEWS = {
    "influenza": "https://www.who.int/news-room/fact-sheets/detail/influenza",
    "malaria": "https://www.who.int/news-room/fact-sheets/detail/malaria",
    "tuberculosis": "https://www.who.int/news-room/fact-sheets/detail/tuberculosis",
    "hiv": "https://www.who.int/news-room/fact-sheets/detail/hiv-aids",
    "dengue": "https://www.who.int/news-room/fact-sheets/detail/dengue-and-severe-dengue",
    # add more diseases + URLs
}

# -------- Scraper Function --------
def fetch_disease_overview(url):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return f"WHO page returned {r.status_code}. Read more here: {url}"

        soup = BeautifulSoup(r.text, "html.parser")

        # WHO fact sheets usually have a <div class="sf-detail-body-wrapper"> with <p> paragraphs
        content_div = soup.find("div", class_="sf-detail-body-wrapper")
        if not content_div:
            return f"Overview not found. Read more here: {url}"

        # Extract all paragraphs in the div
        paragraphs = content_div.find_all("p")
        if paragraphs:
            # Join the first few paragraphs (e.g., first 3–5) for a concise overview
            overview_text = "\n\n".join(p.get_text(strip=True) for p in paragraphs[:5])
            return overview_text
        else:
            return f"Overview not found. Read more here: {url}"

    except Exception as e:
        return f"Error fetching overview: {str(e)}"


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()
    intent_name = req["queryResult"]["intent"]["displayName"]
    params = req["queryResult"].get("parameters", {})

    disease = params.get("disease")
    if isinstance(disease, list):
        disease = disease[0] if disease else None

    response_text = ""

    if intent_name == "get_disease_overview":
        if disease and disease.lower() in DISEASE_OVERVIEWS:
            url = DISEASE_OVERVIEWS[disease.lower()]
            response_text = fetch_disease_overview(url)
        else:
            response_text = "Sorry, I don’t have an overview for that disease."

    else:
        response_text = "Sorry, I don't understand your request."

    return jsonify({"fulfillmentText": response_text})


if __name__ == '__main__':
    app.run(debug=True)
