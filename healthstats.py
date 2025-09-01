from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Base WHO API URL
WHO_API_BASE = "https://ghoapi.azureedge.net/api/"

# Mapping of Dialogflow indicator/disease to WHO API indicator codes
WHO_INDICATOR_MAP = {
    "life_expectancy": "WHOSIS_000001",
    "hiv_cases": "HIV_000001",
    "tb_deaths": "TB_000001",
    "malaria_deaths": "MALARIA_000001",
    "covid19_cases": "COVID19_000001"
    # Add more mappings here
}

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()
    
    intent_name = req["queryResult"]["intent"]["displayName"]
    parameters = req["queryResult"]["parameters"]
    
    places = parameters.get("places") or ""
    disease = parameters.get("disease") or ""
    indicator = parameters.get("indicator") or ""
    year = parameters.get("year") or ""

    
    # If year comes as full date, extract year only
    if year:
        year = year[:4]

    response_text = ""

    if intent_name == "get_life_expectancy":
        indicator_code = WHO_INDICATOR_MAP.get("life_expectancy")
        response_text = fetch_who_data(indicator_code, places, year)

    elif intent_name == "get_hiv_cases":
        indicator_code = WHO_INDICATOR_MAP.get("hiv_cases")
        response_text = fetch_who_data(indicator_code, places, year)

    elif intent_name == "get_tb_deaths":
        indicator_code = WHO_INDICATOR_MAP.get("tb_deaths")
        response_text = fetch_who_data(indicator_code, places, year)

    elif intent_name == "get_indicator_data":
        if indicator:
            indicator_code = WHO_INDICATOR_MAP.get(indicator)
            response_text = fetch_who_data(indicator_code, places, year)
        else:
            response_text = "Sorry, I could not find the indicator."

    elif intent_name == "get_disease_overview":
        if disease:
            response_text = f"{disease} is a disease. WHO provides detailed statistics for it."
        else:
            response_text = "Please provide the disease name."

    else:
        response_text = "Sorry, I don't understand your request."

    return jsonify({"fulfillmentText": response_text})


def fetch_who_data(indicator_code, places, year):
    if not indicator_code or not places or not year:
        return "Missing parameters to fetch WHO data."

    url = f"{WHO_API_BASE}{indicator_code}?$filter=SpatialDim eq '{places}' and TimeDim eq {year}"
    try:
        r = requests.get(url)
        data = r.json()
        if "value" in data and len(data["value"]) > 0:
            result = data["value"][0]
            val = result.get("NumericValue") or result.get("Display")
            return f"The value for {indicator_code} in {places} for {year} is {val}."
        else:
            return f"No data found for {indicator_code} in {places} for {year}."
    except Exception as e:
        return f"Error fetching data: {str(e)}"


if __name__ == '__main__':
    app.run(debug=True)
