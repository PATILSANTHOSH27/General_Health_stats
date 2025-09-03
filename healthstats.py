from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# -------- Static Mapping of Diseases to WHO URLs --------
DISEASE_URLS = {
    "malaria": "https://www.who.int/news-room/fact-sheets/detail/malaria",
    "tuberculosis": "https://www.who.int/news-room/fact-sheets/detail/tuberculosis",
    "hiv": "https://www.who.int/news-room/fact-sheets/detail/hiv-aids",
    "aids": "https://www.who.int/news-room/fact-sheets/detail/hiv-aids",
    "influenza": "https://www.who.int/news-room/fact-sheets/detail/influenza-(seasonal)",
    "cholera": "https://www.who.int/news-room/fact-sheets/detail/cholera",
    "ebola": "https://www.who.int/news-room/fact-sheets/detail/ebola-virus-disease",
    "dengue": "https://www.who.int/news-room/fact-sheets/detail/dengue-and-severe-dengue",
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
}

# -------- Helper Function to Fetch Overview --------
def fetch_disease_overview(disease):
    disease = disease.lower()
    url = DISEASE_URLS.get(disease)

    if not url:
        return f"Sorry, I don’t have information about {disease}."

    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return f"WHO page for {disease} returned status {r.status_code}."

        soup = BeautifulSoup(r.text, "html.parser")

        # Grab the first paragraph inside the WHO content
        content_div = soup.find("div", {"class": "sf-detail-body-wrapper"})
        if not content_div:
            return f"Overview not found for {disease}. You can read more here: {url}"

        first_para = content_div.find("p")
        if first_para:
            return first_para.get_text(strip=True) + f" (Read more: {url})"
        else:
            return f"Overview not found for {disease}. See: {url}"

    except Exception as e:
        return f"Error fetching overview for {disease}: {str(e)}"


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()
    intent_name = req["queryResult"]["intent"]["displayName"]
    params = req["queryResult"].get("parameters", {})

    disease = params.get("disease") or ""

    response_text = ""

    if intent_name == "get_disease_overview":
        if disease:
            response_text = fetch_disease_overview(disease)
        else:
            response_text = "Please provide the disease name."

    else:
        response_text = "Sorry, I only handle disease overviews right now."

    return jsonify({"fulfillmentText": response_text})


if __name__ == '__main__':
    app.run(debug=True)
