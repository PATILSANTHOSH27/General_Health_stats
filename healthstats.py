# from flask import Flask, request, jsonify
# import requests
# from bs4 import BeautifulSoup

# app = Flask(__name__)

# # -------- Static mapping of diseases to WHO fact sheet URLs --------
# DISEASE_OVERVIEWS = {
#     "malaria": "https://www.who.int/news-room/fact-sheets/detail/malaria",
#     "influenza": "https://www.who.int/news-room/fact-sheets/detail/influenza-(seasonal)",
#     "dengue": "https://www.who.int/news-room/fact-sheets/detail/dengue-and-severe-dengue",
#     "hiv": "https://www.who.int/news-room/fact-sheets/detail/hiv-aids",
#     "tuberculosis": "https://www.who.int/news-room/fact-sheets/detail/tuberculosis",
#     "covid-19": "https://www.who.int/news-room/fact-sheets/detail/coronavirus-disease-(covid-19)",
#     "cholera": "https://www.who.int/news-room/fact-sheets/detail/cholera",
#     "measles": "https://www.who.int/news-room/fact-sheets/detail/measles",
#     "ebola": "https://www.who.int/news-room/fact-sheets/detail/ebola-virus-disease",
#     "zika": "https://www.who.int/news-room/fact-sheets/detail/zika-virus",
#     "yellow fever": "https://www.who.int/news-room/fact-sheets/detail/yellow-fever",
#     "hepatitis b": "https://www.who.int/news-room/fact-sheets/detail/hepatitis-b",
#     "hepatitis c": "https://www.who.int/news-room/fact-sheets/detail/hepatitis-c",
#     "rabies": "https://www.who.int/news-room/fact-sheets/detail/rabies",
#     "meningitis": "https://www.who.int/news-room/fact-sheets/detail/meningitis",
#     "leprosy": "https://www.who.int/news-room/fact-sheets/detail/leprosy",
#     "schistosomiasis": "https://www.who.int/news-room/fact-sheets/detail/schistosomiasis",
#     "trypanosomiasis": "https://www.who.int/news-room/fact-sheets/detail/trypanosomiasis-(sleeping-sickness)",
#     "onchocerciasis": "https://www.who.int/news-room/fact-sheets/detail/onchocerciasis-(river-blindness)",
#     "lyme disease": "https://www.who.int/news-room/fact-sheets/detail/lyme-disease",
#     # Add more diseases here if needed
# }

# # -------- Helper function to fetch Overview section --------
# def fetch_overview(url):
#     try:
#         r = requests.get(url, timeout=10)
#         r.raise_for_status()
#         soup = BeautifulSoup(r.text, "html.parser")

#         # Find the heading containing "Overview" (h2 or h3)
#         heading = soup.find(lambda tag: tag.name in ["h2", "h3"] and "overview" in tag.get_text(strip=True).lower())
#         if not heading:
#             return None

#         # Collect all <p> paragraphs until next heading
#         paragraphs = []
#         for sibling in heading.find_next_siblings():
#             if sibling.name in ["h2", "h3"]:
#                 break
#             if sibling.name == "p":
#                 text = sibling.get_text(strip=True)
#                 if text:
#                     paragraphs.append(text)

#         if paragraphs:
#             return " ".join(paragraphs)
#         return None
#     except Exception as e:
#         return None

# # -------- Helper Function: Fetch Symptoms --------
# # def fetch_symptoms(url, disease):
# #     try:
# #         r = requests.get(url, timeout=10)
# #         r.raise_for_status()
# #         soup = BeautifulSoup(r.text, "html.parser")

# #         # Find the heading containing "Symptoms" or "Signs and symptoms"
# #         heading = soup.find(
# #             lambda tag: tag.name in ["h2", "h3"] 
# #             and ("symptoms" in tag.get_text(strip=True).lower() 
# #                  or "signs and symptoms" in tag.get_text(strip=True).lower())
# #         )
# #         if not heading:
# #             return None

# #         # Collect ONLY bullet points (<ul><li>)
# #         points = []
# #         for sibling in heading.find_next_siblings():
# #             if sibling.name in ["h2", "h3"]:
# #                 break
# #             if sibling.name == "ul":
# #                 for li in sibling.find_all("li"):
# #                     text = li.get_text(strip=True)
# #                     if text:
# #                         points.append(f"- {text}")

# #         if points:
# #             return f"The common symptoms of {disease.capitalize()} are:\n" + "\n".join(points)
# #         return None
# #     except Exception:
# #         return None


# # # -------- Helper Function: Fetch Treatment --------
# # def fetch_treatment(url, disease):
# #     try:
# #         r = requests.get(url, timeout=10)
# #         r.raise_for_status()
# #         soup = BeautifulSoup(r.text, "html.parser")

# #         # Find the heading containing "Treatment"
# #         heading = soup.find(
# #             lambda tag: tag.name in ["h2", "h3"] 
# #             and "treatment" in tag.get_text(strip=True).lower()
# #         )
# #         if not heading:
# #             return None

# #         # Collect ONLY bullet points (<ul><li>)
# #         points = []
# #         for sibling in heading.find_next_siblings():
# #             if sibling.name in ["h2", "h3"]:
# #                 break
# #             if sibling.name == "ul":
# #                 for li in sibling.find_all("li"):
# #                     text = li.get_text(strip=True)
# #                     if text:
# #                         points.append(f"- {text}")

# #         if points:
# #             return f"The common treatments for {disease.capitalize()} are:\n" + "\n".join(points)
# #         return None
# #     except Exception:
# #         return None

# # # -------- Helper Function: Fetch Prevention --------
# # def fetch_prevention(url, disease):
# #     try:
# #         r = requests.get(url, timeout=10)
# #         r.raise_for_status()
# #         soup = BeautifulSoup(r.text, "html.parser")

# #         # Find the heading containing "Prevention"
# #         heading = soup.find(
# #             lambda tag: tag.name in ["h2", "h3"] 
# #             and "prevention" in tag.get_text(strip=True).lower()
# #         )
# #         if not heading:
# #             return None

# #         # Collect only bullet points (unordered list) until next heading
# #         points = []
# #         for sibling in heading.find_next_siblings():
# #             if sibling.name in ["h2", "h3"]:
# #                 break
# #             if sibling.name == "ul":  # unordered list
# #                 for li in sibling.find_all("li"):
# #                     li_text = li.get_text(strip=True)
# #                     if li_text:
# #                         points.append(f"- {li_text}")

# #         if points:
# #             return f"The common prevention methods for {disease.capitalize()} are:\n" + "\n".join(points)
# #         return None
# #     except Exception as e:
# #         return None

# def fetch_symptoms(url, disease):
#     try:
#         r = requests.get(url, timeout=10)
#         r.raise_for_status()
#         soup = BeautifulSoup(r.text, "html.parser")

#         heading = soup.find(
#             lambda tag: tag.name in ["h2", "h3"] 
#             and ("symptoms" in tag.get_text(strip=True).lower() 
#                  or "signs and symptoms" in tag.get_text(strip=True).lower())
#         )
#         if not heading:
#             return None

#         # Try <ul> first
#         points = []
#         for sibling in heading.find_next_siblings():
#             if sibling.name in ["h2", "h3"]:
#                 break
#             if sibling.name == "ul":
#                 for li in sibling.find_all("li"):
#                     text = li.get_text(strip=True)
#                     if text:
#                         points.append(f"- {text}")

#         # Fallback to <p> if no <ul>
#         if not points:
#             paragraphs = []
#             for sibling in heading.find_next_siblings():
#                 if sibling.name in ["h2", "h3"]:
#                     break
#                 if sibling.name == "p":
#                     text = sibling.get_text(strip=True)
#                     if text:
#                         paragraphs.append(f"- {text}")
#             points = paragraphs

#         if points:
#             return f"The common symptoms of {disease.capitalize()} are:\n" + "\n".join(points)
#         return None

#     except Exception as e:
#         print(f"fetch_symptoms error: {e}")
#         return None


# def fetch_treatment(url, disease):
#     try:
#         r = requests.get(url, timeout=10)
#         r.raise_for_status()
#         soup = BeautifulSoup(r.text, "html.parser")

#         heading = soup.find(
#             lambda tag: tag.name in ["h2", "h3"] 
#             and ("treatment" in tag.get_text(strip=True).lower() 
#                  or "management" in tag.get_text(strip=True).lower())
#         )
#         if not heading:
#             return None

#         points = []
#         for sibling in heading.find_next_siblings():
#             if sibling.name in ["h2", "h3"]:
#                 break
#             if sibling.name == "ul":
#                 for li in sibling.find_all("li"):
#                     text = li.get_text(strip=True)
#                     if text:
#                         points.append(f"- {text}")

#         if not points:
#             paragraphs = []
#             for sibling in heading.find_next_siblings():
#                 if sibling.name in ["h2", "h3"]:
#                     break
#                 if sibling.name == "p":
#                     text = sibling.get_text(strip=True)
#                     if text:
#                         paragraphs.append(f"- {text}")
#             points = paragraphs

#         if points:
#             return f"The common treatments for {disease.capitalize()} are:\n" + "\n".join(points)
#         return None

#     except Exception as e:
#         print(f"fetch_treatment error: {e}")
#         return None


# def fetch_prevention(url, disease):
#     try:
#         r = requests.get(url, timeout=10)
#         r.raise_for_status()
#         soup = BeautifulSoup(r.text, "html.parser")

#         heading = soup.find(
#             lambda tag: tag.name in ["h2", "h3"] 
#             and "prevention" in tag.get_text(strip=True).lower()
#         )
#         if not heading:
#             return None

#         points = []
#         for sibling in heading.find_next_siblings():
#             if sibling.name in ["h2", "h3"]:
#                 break
#             if sibling.name == "ul":
#                 for li in sibling.find_all("li"):
#                     text = li.get_text(strip=True)
#                     if text:
#                         points.append(f"- {text}")

#         if not points:
#             paragraphs = []
#             for sibling in heading.find_next_siblings():
#                 if sibling.name in ["h2", "h3"]:
#                     break
#                 if sibling.name == "p":
#                     text = sibling.get_text(strip=True)
#                     if text:
#                         paragraphs.append(f"- {text}")
#             points = paragraphs

#         if points:
#             return f"The common prevention methods for {disease.capitalize()} are:\n" + "\n".join(points)
#         return None

#     except Exception as e:
#         print(f"fetch_prevention error: {e}")
#         return None



# # ---------- WHO Outbreak API ----------
# WHO_API_URL = (
#     "https://www.who.int/api/emergencies/diseaseoutbreaknews"
#     "?sf_provider=dynamicProvider372&sf_culture=en"
#     "&$orderby=PublicationDateAndTime%20desc"
#     "&$expand=EmergencyEvent"
#     "&$select=Title,TitleSuffix,OverrideTitle,UseOverrideTitle,regionscountries,"
#     "ItemDefaultUrl,FormattedDate,PublicationDateAndTime"
#     "&%24format=json&%24top=10&%24count=true"
# )

# # Cache for static JSON data
# data_cache = {}

# # ================== HELPERS ==================
# def get_who_outbreak_data():
#     """Fetch outbreak news directly from WHO API."""
#     try:
#         response = requests.get(WHO_API_URL, timeout=10)
#         response.raise_for_status()
#         data = response.json()

#         if "value" not in data or not data["value"]:
#             return None

#         outbreaks = []
#         for item in data["value"][:5]:  # only latest 5
#             title = item.get("OverrideTitle") or item.get("Title")
#             date = item.get("FormattedDate", "Unknown date")
#             url = "https://www.who.int" + item.get("ItemDefaultUrl", "")
#             outbreaks.append(f"🦠 {title} ({date})\n🔗 {url}")

#         return outbreaks
#     except Exception as e:
#         print(f"Error fetching WHO outbreak data: {e}")
#         return None

# # -------- Helper Function: Fetch Symptoms --------
# # def fetch_symptoms(url):
# #     try:
# #         r = requests.get(url, timeout=10)
# #         r.raise_for_status()
# #         soup = BeautifulSoup(r.text, "html.parser")

# #         # Find the heading containing "Symptoms" or "Signs and symptoms"
# #         heading = soup.find(
# #             lambda tag: tag.name in ["h2", "h3"] 
# #             and ("symptoms" in tag.get_text(strip=True).lower() 
# #                  or "signs and symptoms" in tag.get_text(strip=True).lower())
# #         )
# #         if not heading:
# #             return None

# #         # Collect all <p> or <li> until next heading
# #         points = []
# #         for sibling in heading.find_next_siblings():
# #             if sibling.name in ["h2", "h3"]:
# #                 break
# #             if sibling.name == "p":
# #                 text = sibling.get_text(strip=True)
# #                 if text:
# #                     points.append(text)
# #             elif sibling.name == "ul":  # bullet points
# #                 for li in sibling.find_all("li"):
# #                     li_text = li.get_text(strip=True)
# #                     if li_text:
# #                         points.append(f"- {li_text}")

# #         if points:
# #             return "\n".join(points)
# #         return None
# #     except Exception as e:
# #         return None

# # def fetch_symptoms(url, disease):
# #     try:
# #         r = requests.get(url, timeout=10)
# #         r.raise_for_status()
# #         soup = BeautifulSoup(r.text, "html.parser")

# #         # Find the heading containing "Symptoms" or "Signs and symptoms"
# #         heading = soup.find(
# #             lambda tag: tag.name in ["h2", "h3"] 
# #             and ("symptoms" in tag.get_text(strip=True).lower() 
# #                  or "signs and symptoms" in tag.get_text(strip=True).lower())
# #         )
# #         if not heading:
# #             return None

# #         # Collect all <p> or <li> until next heading
# #         points = []
# #         for sibling in heading.find_next_siblings():
# #             if sibling.name in ["h2", "h3"]:
# #                 break
# #             if sibling.name == "p":
# #                 text = sibling.get_text(strip=True)
# #                 if text:
# #                     points.append(f"- {text}")
# #             elif sibling.name == "ul":  # bullet points
# #                 for li in sibling.find_all("li"):
# #                     li_text = li.get_text(strip=True)
# #                     if li_text:
# #                         points.append(f"- {li_text}")

# #         if points:
# #             return f"The common symptoms of {disease.capitalize()} are:\n" + "\n".join(points)
# #         return None
# #     except Exception as e:
# #         return None

# # # -------- Helper Function: Fetch Treatment --------
# # def fetch_treatment(url, disease):
# #     try:
# #         r = requests.get(url, timeout=10)
# #         r.raise_for_status()
# #         soup = BeautifulSoup(r.text, "html.parser")

# #         # Find the heading containing "Treatment"
# #         heading = soup.find(
# #             lambda tag: tag.name in ["h2", "h3"]
# #             and "treatment" in tag.get_text(strip=True).lower()
# #         )
# #         if not heading:
# #             return None

# #         # Collect all <p> or <li> until next heading
# #         points = []
# #         for sibling in heading.find_next_siblings():
# #             if sibling.name in ["h2", "h3"]:
# #                 break
# #             if sibling.name == "p":
# #                 text = sibling.get_text(strip=True)
# #                 if text:
# #                     points.append(f"- {text}")
# #             elif sibling.name == "ul":  # bullet points
# #                 for li in sibling.find_all("li"):
# #                     li_text = li.get_text(strip=True)
# #                     if li_text:
# #                         points.append(f"- {li_text}")

# #         if points:
# #             return f"The common treatments for {disease.capitalize()} are:\n" + "\n".join(points)
# #         return None
# #     except Exception:
# #         return None


# # -------- Flask webhook route --------
# @app.route('/webhook', methods=['POST'])
# def webhook():
#     req = request.get_json()
#     intent_name = req["queryResult"]["intent"]["displayName"]
#     params = req["queryResult"].get("parameters", {})
#     disease = params.get("disease", "").lower()

#     # --------- Dynamic Data: WHO Outbreaks ---------
#     req = request.get_json(silent=True, force=True)
#     intent = req.get('queryResult', {}).get('intent', {}).get('displayName', '')
#     params = req.get('queryResult', {}).get('parameters', {})

#     response_text = "Sorry, I don't understand your request."

#     if intent_name == "get_disease_overview":
#         url = DISEASE_OVERVIEWS.get(disease)
#         if url:
#             overview = fetch_overview(url)
#             if overview:
#                 response_text = overview
#             else:
#                 response_text = f"Overview not found for {disease.capitalize()}. You can read more here: {url}"
#         else:
#             response_text = f"Disease not found. Make sure to use a valid disease name."

#     elif intent_name == "get_symptoms":
#         url = DISEASE_OVERVIEWS.get(disease)   # use same mapping
#         if url:
#             symptoms = fetch_symptoms(url, disease)
#             if symptoms:
#                 # response_text = f"Here are the symptoms of {disease.capitalize()}:\n{symptoms}"
#                 response_text = symptoms   # <-- FIXED (no duplicate intro)
#             else:
#                 response_text = f"Symptoms not found for {disease.capitalize()}. You can read more here: {url}"
#         else:
#             response_text = f"Sorry, I don't have a URL for {disease.capitalize()}."

#     # return jsonify({"fulfillmentText": response_text})
#     elif intent_name == "get_treatment":
#         url = DISEASE_OVERVIEWS.get(disease)
#         if url:
#             treatment = fetch_treatment(url, disease)
#             if treatment:
#                 response_text = treatment
#             else:
#                 response_text = f"Treatment details not found for {disease.capitalize()}. You can read more here: {url}"
#         else:
#             response_text = f"Sorry, I don't have a URL for {disease.capitalize()}."

#     # return jsonify({"fulfillmentText": response_text})
#     elif intent_name == "get_prevention":
#         url = DISEASE_OVERVIEWS.get(disease)
#         if url:
#             prevention = fetch_prevention(url, disease)
#             if prevention:
#                 response_text = prevention
#             else:
#                 response_text = f"Prevention methods not found for {disease.capitalize()}. You can read more here: {url}"
#         else:
#             response_text = f"Sorry, I don't have a URL for {disease.capitalize()}."
            
#     # return jsonify({"fulfillmentText": response_text})
#     # --------- Dynamic Data: WHO Outbreaks ---------
#     elif intent == 'disease_outbreak.general':
#         outbreaks = get_who_outbreak_data()
#         if not outbreaks:
#             response_text = "⚠️ Unable to fetch outbreak data right now."
#         else:
#             response_text = "🌍 Latest WHO Outbreak News:\n\n" + "\n\n".join(outbreaks)


#     return jsonify({"fulfillmentText": response_text})


# if __name__ == '__main__':
#     app.run(debug=True)


from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

# -------------------
# Devnagri API Key
# -------------------
DEVNAGRI_API_KEY = os.getenv("DEVNAGRI_API_KEY")
DEVNAGRI_API_URL = "https://api.devnagri.com/machine-translation/v2/translate"

# -------------------
# Translation Function (to English only)
# -------------------
def translate_to_english(disease_param):
    """
    Translate the disease name to English using Devnagri API.
    Returns the original text if API fails.
    """
    if not disease_param.strip():
        return disease_param
    data = {
        "key": DEVNAGRI_API_KEY,
        "sentence": disease_param,
        "src_lang": "auto",
        "dest_lang": "en",
        "industry": "5",
        "is_apply_glossary": "1"
    }
    try:
        response = requests.post(DEVNAGRI_API_URL, data=data, timeout=15)

        # Handle server errors gracefully
        if response.status_code >= 500:
            print(f"Devnagri server error {response.status_code}, returning original text.")
            return disease_param

        # Handle bad request (400)
        if response.status_code == 400:
            print(f"Devnagri bad request 400, returning original text. Response: {response.text}")
            return disease_param

        response.raise_for_status()
        return response.json().get("translated_sentence", disease_param)
    except Exception as e:
        print(f"Translation failed: {e}. Returning original text.")
        return disease_param

# -------------------
# Disease Data Mapping
# -------------------
DISEASE_OVERVIEWS = {
    "malaria": "https://www.who.int/news-room/fact-sheets/detail/malaria",
    "influenza": "https://www.who.int/news-room/fact-sheets/detail/influenza-(seasonal)",
    "dengue": "https://www.who.int/news-room/fact-sheets/detail/dengue-and-severe-dengue",
    "hiv": "https://www.who.int/news-room/fact-sheets/detail/hiv-aids",
    "tuberculosis": "https://www.who.int/news-room/fact-sheets/detail/tuberculosis",
}

# -------------------
# Fetch Helpers
# -------------------
def fetch_overview(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        heading = soup.find(lambda tag: tag.name in ["h2","h3"] and "overview" in tag.get_text(strip=True).lower())
        if not heading:
            return None
        paragraphs = []
        for sibling in heading.find_next_siblings():
            if sibling.name in ["h2","h3"]:
                break
            if sibling.name == "p":
                paragraphs.append(sibling.get_text(strip=True))
        return " ".join(paragraphs) if paragraphs else None
    except:
        return None

def fetch_content(url, disease_param, keyword):
    """
    Generic fetcher for symptoms, treatment, prevention.
    Tries <ul> first, then falls back to <p>.
    """
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        heading = soup.find(
            lambda tag: tag.name in ["h2","h3"] and keyword in tag.get_text(strip=True).lower()
        )
        if not heading:
            return None

        points = []
        for sibling in heading.find_next_siblings():
            if sibling.name in ["h2","h3"]:
                break
            if sibling.name == "ul":
                for li in sibling.find_all("li"):
                    text = li.get_text(strip=True)
                    if text:
                        points.append(f"- {text}")

        if not points:
            paragraphs = []
            for sibling in heading.find_next_siblings():
                if sibling.name in ["h2","h3"]:
                    break
                if sibling.name == "p":
                    text = sibling.get_text(strip=True)
                    if text:
                        paragraphs.append(f"- {text}")
            points = paragraphs

        if points:
            return f"The {keyword} of {disease_param.capitalize()} are:\n" + "\n".join(points)
        return None
    except Exception as e:
        print(f"fetch_content error ({keyword}): {e}")
        return None

# -------------------
# Webhook
# -------------------
@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()
    intent_name = req["queryResult"]["intent"]["displayName"]
    disease_param = req["queryResult"].get("parameters", {}).get("disease", "")

    # Translate disease to English (send original multilingual text to Devnagri)
    disease_en = translate_to_english(disease_param)

    # Use lowercase only for dictionary lookup
    url = DISEASE_OVERVIEWS.get(disease_en.lower())
    response_text = "Sorry, I don't understand your request."

    if not url:
        response_text = f"Disease '{disease_en}' not found in database."
    else:
        if intent_name == "get_disease_overview":
            overview = fetch_overview(url)
            response_text = overview or f"Overview not found for {disease_param}."
        elif intent_name == "get_symptoms":
            response_text = fetch_content(url, disease_en, "symptoms") or f"Symptoms not found for {disease_param}."
        elif intent_name == "get_treatment":
            response_text = fetch_content(url, disease_en, "treatment") or f"Treatment not found for {disease_param}."
        elif intent_name == "get_prevention":
            response_text = fetch_content(url, disease_en, "prevention") or f"Prevention not found for {disease_param}."

    # Return response as-is, no translation back
    return jsonify({"fulfillmentText": response_text})

if __name__ == '__main__':
    app.run(debug=True)

