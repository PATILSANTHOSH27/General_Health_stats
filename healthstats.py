from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

WHO_API_BASE = "https://ghoapi.azureedge.net/api/"

# -------- Load WHO Indicators Dynamically --------
def load_who_indicators():
    url = WHO_API_BASE + "Indicators"
    try:
        r = requests.get(url)
        data = r.json()
        mapping = {}
        for item in data.get("value", []):
            key = item["IndicatorName"].lower().replace(" ", "_")
            mapping[key] = item["IndicatorCode"]
        return mapping
    except Exception as e:
        print(f"Error fetching WHO indicators: {str(e)}")
        return {}

WHO_INDICATOR_MAP = load_who_indicators()

# -------- Load WHO Countries Dynamically --------
def load_country_map():
    url = WHO_API_BASE + "Dimension/SpatialDim"
    try:
        r = requests.get(url)
        data = r.json()
        mapping = {}
        for item in data.get("value", []):
            name = item["Title"].lower()
            code = item["Code"]
            mapping[name] = code
        return mapping
    except Exception as e:
        print(f"Error fetching countries: {str(e)}")
        return {}

COUNTRY_CODE_MAP = load_country_map()

# Optional alias map for common variations
COUNTRY_ALIASES = {
    "us": "united states",
    "america": "united states",
    "uk": "united kingdom",
    "uae": "united arab emirates"
}

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()
    intent_name = req["queryResult"]["intent"]["displayName"]
    params = req["queryResult"].get("parameters", {})

    country_input = params.get("country") or ""
    disease = params.get("disease") or ""
    indicator = params.get("indicator") or ""
    data_type = params.get("data_type") or ""
    year = params.get("year") or ""

    if year:
        year = year[:4]

    # Normalize country name using aliases
    country_key = COUNTRY_ALIASES.get(country_input.lower(), country_input.lower())
    country_code = COUNTRY_CODE_MAP.get(country_key)

    response_text = ""

    # -------- Get Disease Data --------
    if intent_name == "get_disease_data":
        if not disease or not data_type or not country_code or not year:
            response_text = "Please provide disease, data type, country, and year."
        else:
            key = f"{disease.lower()}_{data_type.lower()}"
            indicator_code = WHO_INDICATOR_MAP.get(key)
            response_text = fetch_who_data(indicator_code, country_code, year)

    # -------- Get General Indicator Data --------
    elif intent_name == "get_indicator_data":
        if not indicator or not country_code or not year:
            response_text = "Please provide indicator, country, and year."
        else:
            indicator_code = WHO_INDICATOR_MAP.get(indicator.lower())
            response_text = fetch_who_data(indicator_code, country_code, year)

    # -------- Get Disease Overview --------
    elif intent_name == "get_disease_overview":
        if disease:
            response_text = f"{disease.capitalize()} is a disease. WHO provides detailed statistics and reports for it."
        else:
            response_text = "Please provide the disease name."

    else:
        response_text = "Sorry, I don't understand your request."

    return jsonify({"fulfillmentText": response_text})


def fetch_who_data(indicator_code, country_code, year):
    if not indicator_code or not country_code or not year:
        return "Missing parameters to fetch WHO data."

    url = f"{WHO_API_BASE}{indicator_code}?$filter=SpatialDim eq '{country_code}' and TimeDim eq {year}"
    try:
        r = requests.get(url)
        data = r.json()
        if "value" in data and len(data["value"]) > 0:
            val = data["value"][0].get("NumericValue") or data["value"][0].get("Display")
            return f"The value for {indicator_code} in {country_code} for {year} is {val}."
        else:
            return f"No data found for {indicator_code} in {country_code} for {year}."
    except Exception as e:
        return f"Error fetching data from WHO API: {str(e)}"


if __name__ == '__main__':
    app.run(debug=True)
