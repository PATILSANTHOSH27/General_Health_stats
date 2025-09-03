from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# -------- Static Mapping of Diseases to WHO URLs --------
DISEASE_OVERVIEWS = {
    # "influenza": "https://www.who.int/news-room/fact-sheets/detail/influenza",
    "malaria": "https://www.who.int/news-room/fact-sheets/detail/malaria",
    "tuberculosis": "https://www.who.int/news-room/fact-sheets/detail/tuberculosis",
    "hiv": "https://www.who.int/news-room/fact-sheets/detail/hiv-aids",
    "dengue": "https://www.who.int/news-room/fact-sheets/detail/dengue-and-severe-dengue",
    # "malaria": "https://www.who.int/news-room/fact-sheets/detail/malaria",
    # "tuberculosis": "https://www.who.int/news-room/fact-sheets/detail/tuberculosis",
    # "hiv": "https://www.who.int/news-room/fact-sheets/detail/hiv-aids",
    "aids": "https://www.who.int/news-room/fact-sheets/detail/hiv-aids",
    "influenza": "https://www.who.int/news-room/fact-sheets/detail/influenza-(seasonal)",
    "cholera": "https://www.who.int/news-room/fact-sheets/detail/cholera",
    "ebola": "https://www.who.int/news-room/fact-sheets/detail/ebola-virus-disease",
    # "dengue": "https://www.who.int/news-room/fact-sheets/detail/dengue-and-severe-dengue",
    "zika": "https://www.who.int/news-room/fact-sheets/detail/zika-virus",
    "covid-19": "https://www.who.int/news-room/fact-sheets/detail/coronavirus-disease-(covid-19)",
    "measles": "https://www.who.int/news-room/fact-sheets/detail/measles",
    "polio": "https://www.who.int/news-room/fact-sheets/detail/poliomyelitis",
    "rabies": "https://www.who.int/news-room/fact-sheets/detail/rabies",
    "yellow fever": "https://www.who.int/news-room/fact-sheets/detail/yellow-fever",
    "hepatitis": "https://www.who.int/news-room/fact-sheets/detail/hepatitis",
    "hepatitis a": "https://www.who.int/news-room/fact-sheets/detail/hepatitis-a",
    "hepatitis b": "https://www.who.int/news-room/fact-sheets/detail/hepatitis-b",
    "hepatitis c": "https://www.who.int/news-room/fact-sheets/detail/hepatitis-c",
    "leprosy": "https://www.who.int/news-room/fact-sheets/detail/leprosy",
    "typhoid": "https://www.who.int/news-room/fact-sheets/detail/typhoid"
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

        # Extract the first paragraph as summary
        first_para = content_div.find("p")
        if first_para:
            return first_para.get_text(strip=True)
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

