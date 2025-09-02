from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# -----------------------------
# Disease → WHO IndicatorCode mapping
# -----------------------------
DISEASE_INDICATOR_MAP = {
    "dengue cases": "DENGUE_REPORTED_CASES",
    "dengue": "DENGUE_REPORTED_CASES",
    "dengue infections": "DENGUE_REPORTED_CASES",
    
    "malaria incidence": "MALARIA_REPORTED_CASES",
    "malaria cases": "MALARIA_REPORTED_CASES",
    "malaria infections": "MALARIA_REPORTED_CASES",
    
    "tuberculosis cases": "TB_REPORTED_CASES",
    "tb": "TB_REPORTED_CASES",
    "tuberculosis": "TB_REPORTED_CASES",
    
    "hiv cases": "HIV_REPORTED_CASES",
    "hiv infections": "HIV_REPORTED_CASES",
    "hiv": "HIV_REPORTED_CASES",
    
    "covid-19 cases": "COVID19_CONFIRMED_CASES",
    "covid19 cases": "COVID19_CONFIRMED_CASES",
    "covid cases": "COVID19_CONFIRMED_CASES",
    "covid": "COVID19_CONFIRMED_CASES",
    
    "cholera cases": "CHOLERA_REPORTED_CASES",
    "cholera": "CHOLERA_REPORTED_CASES",
    "cholera infections": "CHOLERA_REPORTED_CASES",
    
    "measles cases": "MEASLES_REPORTED_CASES",
    "measles": "MEASLES_REPORTED_CASES",
    "rubeola": "MEASLES_REPORTED_CASES",
    
    "hepatitis cases": "HEPATITIS_REPORTED_CASES",
    "hepatitis": "HEPATITIS_REPORTED_CASES",
    "hepatitis infections": "HEPATITIS_REPORTED_CASES",
    
    "influenza cases": "INFLUENZA_REPORTED_CASES",
    "flu": "INFLUENZA_REPORTED_CASES",
    "influenza": "INFLUENZA_REPORTED_CASES",
    
    "polio cases": "POLIO_REPORTED_CASES",
    "poliomyelitis": "POLIO_REPORTED_CASES",
    "polio": "POLIO_REPORTED_CASES",
    
    "typhoid cases": "TYPHOID_REPORTED_CASES",
    "typhoid fever": "TYPHOID_REPORTED_CASES",
    "enteric fever": "TYPHOID_REPORTED_CASES",
    
    "yellow fever cases": "YELLOW_FEVER_REPORTED_CASES",
    "yellow fever": "YELLOW_FEVER_REPORTED_CASES",
    
    "rabies cases": "RABIES_REPORTED_CASES",
    "rabies infections": "RABIES_REPORTED_CASES",
    "rabies": "RABIES_REPORTED_CASES"
}

# -----------------------------
# Webhook endpoint
# -----------------------------
@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(force=True)

    # Step 1: Extract parameters from queryResult
    params = req.get("queryResult", {}).get("parameters", {})

    # Step 2: Fallback - check outputContexts if parameters missing
    if not params:
        contexts = req.get("queryResult", {}).get("outputContexts", [])
        for ctx in contexts:
            ctx_params = ctx.get("parameters", {})
            if ctx_params.get("disease"):
                params = ctx_params
                break

    # Step 3: Get disease, country, year
    disease = params.get("disease")
    country = params.get("country")
    year = params.get("year")

    # Step 4: Validate parameters
    if not disease or not country or not year:
        return jsonify({"fulfillmentText": "Please provide disease, country, and year."})

    # Step 5: Map disease to WHO IndicatorCode
    indicator_code = DISEASE_INDICATOR_MAP.get(disease.lower())
    if not indicator_code:
        return jsonify({"fulfillmentText": f"Sorry, I don’t have data mapping for {disease}."})

    # Step 6: Build WHO API URL
    api_url = f"https://ghoapi.azureedge.net/api/{indicator_code}?$filter=SpatialDim eq '{country}' and TimeDim eq {year}"

    try:
        # Step 7: Call WHO API
        response = requests.get(api_url)
        if response.status_code == 404:
            return jsonify({"fulfillmentText": f"No data found for {disease} in {country} for {year}."})
        elif response.status_code != 200:
            return jsonify({"fulfillmentText": f"WHO API returned {response.status_code} for {disease} in {country} {year}."})

        data = response.json().get("value", [])
        if not data:
            return jsonify({"fulfillmentText": f"No data found for {disease} in {country} for {year}."})

        # Step 8: Extract numeric value
        numeric_value = data[0].get("NumericValue", "N/A")

        # Step 9: Build fulfillment response
        answer = f"The number of {disease} in {country} in {year} was {numeric_value}."
        return jsonify({"fulfillmentText": answer})

    except Exception as e:
        return jsonify({"fulfillmentText": f"Error fetching data: {str(e)}"})

# -----------------------------
# Run Flask app
# -----------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
