from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# -------- Static mapping of diseases to WHO fact sheet URLs --------
DISEASE_OVERVIEWS = {
    "malaria": "https://www.who.int/news-room/fact-sheets/detail/malaria",
    "influenza": "https://www.who.int/news-room/fact-sheets/detail/influenza-(seasonal)",
    "dengue": "https://www.who.int/news-room/fact-sheets/detail/dengue-and-severe-dengue",
    "hiv": "https://www.who.int/news-room/fact-sheets/detail/hiv-aids",
    "tuberculosis": "https://www.who.int/news-room/fact-sheets/detail/tuberculosis",
    "covid-19": "https://www.who.int/news-room/fact-sheets/detail/coronavirus-disease-(covid-19)",
    "cholera": "https://www.who.int/news-room/fact-sheets/detail/cholera",
    "measles": "https://www.who.int/news-room/fact-sheets/detail/measles",
    "ebola": "https://www.who.int/news-room/fact-sheets/detail/ebola-virus-disease",
    "zika": "https://www.who.int/news-room/fact-sheets/detail/zika-virus",
    # Add more diseases here...
}

# -------- Helper function to fetch Overview section --------
def fetch_overview(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        # Find the heading containing "Overview" (h2 or h3)
        heading = soup.find(lambda tag: tag.name in ["h2", "h3"] and "overview" in tag.get_text(strip=True).lower())
        if not heading:
            return None

        # Collect all <p> paragraphs until next heading
        paragraphs = []
        for sibling in heading.find_next_siblings():
            if sibling.name in ["h2", "h3"]:
                break
            if sibling.name == "p":
                text = sibling.get_text(strip=True)
                if text:
                    paragraphs.append(text)

        if paragraphs:
            return " ".join(paragraphs)
        return None
    except Exception as e:
        return None

# -------- Flask webhook route --------
@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()
    intent_name = req["queryResult"]["intent"]["displayName"]
    params = req["queryResult"].get("parameters", {})
    disease = params.get("disease", "").lower()

    if intent_name == "get_disease_overview":
        url = DISEASE_OVERVIEWS.get(disease)
        if url:
            overview = fetch_overview(url)
            if overview:
                response_text = overview
            else:
                response_text = f"Overview not found for {disease.capitalize()}. You can read more here: {url}"
        else:
            response_text = f"Disease not found. Make sure to use a valid disease name."
    else:
        response_text = "Sorry, I don't understand your request."

    return jsonify({"fulfillmentText": response_text})

if __name__ == '__main__':
    app.run(debug=True)
