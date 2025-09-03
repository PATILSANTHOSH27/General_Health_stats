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
    "yellow fever": "https://www.who.int/news-room/fact-sheets/detail/yellow-fever",
    "hepatitis b": "https://www.who.int/news-room/fact-sheets/detail/hepatitis-b",
    "hepatitis c": "https://www.who.int/news-room/fact-sheets/detail/hepatitis-c",
    "rabies": "https://www.who.int/news-room/fact-sheets/detail/rabies",
    "meningitis": "https://www.who.int/news-room/fact-sheets/detail/meningitis",
    "leprosy": "https://www.who.int/news-room/fact-sheets/detail/leprosy",
    "schistosomiasis": "https://www.who.int/news-room/fact-sheets/detail/schistosomiasis",
    "trypanosomiasis": "https://www.who.int/news-room/fact-sheets/detail/trypanosomiasis-(sleeping-sickness)",
    "onchocerciasis": "https://www.who.int/news-room/fact-sheets/detail/onchocerciasis-(river-blindness)",
    "lyme disease": "https://www.who.int/news-room/fact-sheets/detail/lyme-disease",
    # Add more diseases here if needed
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

# -------- Helper Function: Fetch Symptoms --------
def fetch_disease_symptoms(disease):
    url = DISEASE_URLS.get(disease.lower())
    if not url:
        return f"No WHO fact sheet found for {disease}."

    try:
        r = requests.get(url)
        if r.status_code != 200:
            return f"Failed to fetch symptoms for {disease}. URL: {url}"

        soup = BeautifulSoup(r.text, "html.parser")

        # Look for "Symptoms" or "Signs and symptoms"
        symptoms_header = soup.find(lambda tag: tag.name in ["h2", "h3", "h4", "h5", "h6"] and ("symptoms" in tag.get_text(strip=True).lower()))
        if symptoms_header:
            symptoms_content = []
            for sib in symptoms_header.find_next_siblings():
                if sib.name in ["h2", "h3"]:  # Stop at the next section
                    break
                # Collect bullet points or text
                if sib.name == "ul":
                    for li in sib.find_all("li"):
                        symptoms_content.append(f"- {li.get_text(' ', strip=True)}")
                else:
                    symptoms_content.append(sib.get_text(" ", strip=True))
            return "\n".join(symptoms_content) if symptoms_content else f"Symptoms not found for {disease}. You can read more here: {url}"
        else:
            return f"Symptoms not found for {disease}. You can read more here: {url}"
    except Exception as e:
        return f"Error fetching symptoms: {str(e)}"

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

    if intent_name == "get_symptoms":
        if disease:
            response_text = fetch_disease_symptoms(disease)
        else:
            response_text = "Please provide a disease name."
    else:
        response_text = "Sorry, I don't understand your request."

    return jsonify({"fulfillmentText": response_text})

if __name__ == '__main__':
    app.run(debug=True)
