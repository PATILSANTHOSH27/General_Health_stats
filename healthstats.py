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

# -------- Helper function to scrape Overview from WHO fact sheet --------
def fetch_disease_overview(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()  # raises HTTPError for bad responses
        soup = BeautifulSoup(r.text, "html.parser")

        # WHO pages usually have content inside this div
        content_div = soup.find("div", class_="sf-detail-body-wrapper")
        if not content_div:
            return None

        # Collect paragraphs until first <h2>
        overview_paragraphs = []
        for child in content_div.children:
            if child.name == "h2":  # stop at first subsection
                break
            if child.name == "p":
                text = child.get_text(strip=True)
                if text:
                    overview_paragraphs.append(text)

        if overview_paragraphs:
            return " ".join(overview_paragraphs)
        else:
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
            overview = fetch_disease_overview(url)
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
