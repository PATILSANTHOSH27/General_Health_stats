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
# def fetch_symptoms(url):
#     try:
#         r = requests.get(url, timeout=10)
#         r.raise_for_status()
#         soup = BeautifulSoup(r.text, "html.parser")

#         # Find the heading containing "Symptoms" or "Signs and symptoms"
#         heading = soup.find(
#             lambda tag: tag.name in ["h2", "h3"] 
#             and ("symptoms" in tag.get_text(strip=True).lower() 
#                  or "signs and symptoms" in tag.get_text(strip=True).lower())
#         )
#         if not heading:
#             return None

#         # Collect all <p> or <li> until next heading
#         points = []
#         for sibling in heading.find_next_siblings():
#             if sibling.name in ["h2", "h3"]:
#                 break
#             if sibling.name == "p":
#                 text = sibling.get_text(strip=True)
#                 if text:
#                     points.append(text)
#             elif sibling.name == "ul":  # bullet points
#                 for li in sibling.find_all("li"):
#                     li_text = li.get_text(strip=True)
#                     if li_text:
#                         points.append(f"- {li_text}")

#         if points:
#             return "\n".join(points)
#         return None
#     except Exception as e:
#         return None

def fetch_symptoms(url, disease):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        # Find the heading containing "Symptoms" or "Signs and symptoms"
        heading = soup.find(
            lambda tag: tag.name in ["h2", "h3"] 
            and ("symptoms" in tag.get_text(strip=True).lower() 
                 or "signs and symptoms" in tag.get_text(strip=True).lower())
        )
        if not heading:
            return None

        # Collect all <p> or <li> until next heading
        points = []
        for sibling in heading.find_next_siblings():
            if sibling.name in ["h2", "h3"]:
                break
            if sibling.name == "p":
                text = sibling.get_text(strip=True)
                if text:
                    points.append(f"- {text}")
            elif sibling.name == "ul":  # bullet points
                for li in sibling.find_all("li"):
                    li_text = li.get_text(strip=True)
                    if li_text:
                        points.append(f"- {li_text}")

        if points:
            return f"The common symptoms of {disease.capitalize()} are:\n" + "\n".join(points)
        return None
    except Exception as e:
        return None

# -------- Helper Function: Fetch Treatment --------
def fetch_treatment(url, disease):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        # Find the heading containing "Treatment"
        heading = soup.find(
            lambda tag: tag.name in ["h2", "h3"]
            and "treatment" in tag.get_text(strip=True).lower()
        )
        if not heading:
            return None

        # Collect all <p> or <li> until next heading
        points = []
        for sibling in heading.find_next_siblings():
            if sibling.name in ["h2", "h3"]:
                break
            if sibling.name == "p":
                text = sibling.get_text(strip=True)
                if text:
                    points.append(f"- {text}")
            elif sibling.name == "ul":  # bullet points
                for li in sibling.find_all("li"):
                    li_text = li.get_text(strip=True)
                    if li_text:
                        points.append(f"- {li_text}")

        if points:
            return f"The common treatments for {disease.capitalize()} are:\n" + "\n".join(points)
        return None
    except Exception:
        return None



# -------- Flask webhook route --------
@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()
    intent_name = req["queryResult"]["intent"]["displayName"]
    params = req["queryResult"].get("parameters", {})
    disease = params.get("disease", "").lower()

    response_text = "Sorry, I don't understand your request."

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

    elif intent_name == "get_symptoms":
        url = DISEASE_OVERVIEWS.get(disease)   # use same mapping
        if url:
            symptoms = fetch_symptoms(url, disease)
            if symptoms:
                # response_text = f"Here are the symptoms of {disease.capitalize()}:\n{symptoms}"
                response_text = symptoms   # <-- FIXED (no duplicate intro)
            else:
                response_text = f"Symptoms not found for {disease.capitalize()}. You can read more here: {url}"
        else:
            response_text = f"Sorry, I don't have a URL for {disease.capitalize()}."

    # return jsonify({"fulfillmentText": response_text})
    elif intent_name == "get_treatment":
        url = DISEASE_OVERVIEWS.get(disease)
        if url:
            treatment = fetch_treatment(url, disease)
            if treatment:
                response_text = treatment
            else:
                response_text = f"Treatment details not found for {disease.capitalize()}. You can read more here: {url}"
        else:
            response_text = f"Sorry, I don't have a URL for {disease.capitalize()}."

    return jsonify({"fulfillmentText": response_text})


if __name__ == '__main__':
    app.run(debug=True)
