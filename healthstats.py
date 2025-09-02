from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# -----------------------------------------
# Disease → WHO IndicatorCode mapping
# (placeholder codes – replace with actual ones from WHO API)
# -----------------------------------------
DISEASE_INDICATOR_MAP = {
    "dengue cases": "DENGUE_REPORTED_CASES",
    "malaria incidence": "MALARIA_REPORTED_CASES",
    "tuberculosis cases": "TB_REPORTED_CASES",
    "HIV cases": "HIV_REPORTED_CASES",
    "COVID-19 cases": "COVID19_CONFIRMED_CASES",
    "cholera cases": "CHOLERA_REPORTED_CASES",
    "measles cases": "MEASLES_REPORTED_CASES",
    "hepatitis cases": "HEPATITIS_REPORTED_CASES",
    "influenza cases": "INFLUENZA_REPORTED_CASES",
    "polio cases": "POLIO_REPORTED_CASES",
    "typhoid cases": "TYPHOID_REPORTED_CASES",
    "yellow fever cases": "YELLOW_FEVER_REPORTED_CASES",
    "rabies cases": "RABIES_REPORTED_CASES"
}

# -----------------------------------------
# Webhook endpoint
# -----------------------------------------
@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    # Extract parameters from Dialogflow request
    disease = req.get("queryResult", {}).get("parameters", {}).get("Disease")
    country = req.get("queryResult", {}).get("parameters", {}).get("Country")
    year = req.get("queryResult", {}).get("parameters", {}).get("Year")

    if not disease or not country or not year:
        return jsonify({"fulfillmentText": "Please provide disease, country, and year."})

    # Map disease to WHO IndicatorCode
    indicator_code = DISEASE_INDICATOR_MAP.get(disease.lower())
    if not indicator_code:
        return jsonify({"fulfillmentText": f"Sorry, I don’t have data mapping for {disease}."})

    # Build WHO API URL
    api_url = f"https://ghoapi.azureedge.net/api/{indicator_code}?$filter=SpatialDim eq '{country}' and TimeDim eq {year}"

    try:
        response = requests.get(api_url)
        if response.status_code != 200:
            return jsonify({"fulfillmentText": f"Sorry, WHO API returned {response.status_code} for {disease} in {country} {year}."})

        data = response.json().get("value", [])
        if not data:
            return jsonify({"fulfillmentText": f"No data found for {disease} in {country} for {year}."})

        # Get the numeric value
        numeric_value = data[0].get("NumericValue", "N/A")

        answer = f"The number of {disease} in {country} in {year} was {numeric_value}."
        return jsonify({"fulfillmentText": answer})

    except Exception as e:
        return jsonify({"fulfillmentText": f"Error fetching data: {str(e)}"})

# -----------------------------------------
# Run locally
# -----------------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
