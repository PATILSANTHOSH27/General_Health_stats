from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# WHO API Base
WHO_API_BASE = "https://ghoapi.azureedge.net/api/"

# -------- Indicator Mapping (diseases + health stats) --------
INDICATOR_MAP = {
    "malaria_cases": "MALARIA_000001",
    "malaria_deaths": "MALARIA_000002",
    "tb_cases": "TB_000001",
    "tb_deaths": "TB_000002",
    "dengue_cases": "DENGUE_000001",
    "dengue_deaths": "DENGUE_000002",
    "hiv_cases": "HIV_000001",
    "hiv_deaths": "HIV_000002",
    "life_expectancy": "WHOSIS_000001",   # WHO OData code
    "maternal_mortality": "MDG_0000000029"
    # Add more indicators as needed
}

# -------- Country Mapping (to WHO standard ISO2 codes) --------
COUNTRY_MAP = {
    "india": "IN",
    "brazil": "BR",
    "kenya": "KE",
    "thailand": "TH",
    "united states": "US",
    "nigeria": "NG",
    "china": "CN",
    "philippines": "PH",
    "haiti": "HT",
    "south africa": "ZA",
    "united kingdom": "GB",
    "united arab emirates": "AE"
    # Add more as needed
}

# -------- Aliases for user variations --------
COUNTRY_ALIASES = {
    "us": "united states",
    "america": "united states",
    "usa": "united states",
    "uk": "united kingdom",
    "uae": "united arab emirates",
    "sa": "south africa"
}


# --- Helper function to normalize parameters ---
def normalize_param(value):
    """Convert list -> first string, None -> empty string"""
    if isinstance(value, list):
        return value[0] if value else ""
    return value or ""


def normalize_country(country_name):
    """Normalize user country input into WHO's expected code"""
    if not country_name:
        return ""

    name = country_name.strip().lower()

    # Replace alias (e.g. 'us' -> 'united states')
    if name in COUNTRY_ALIASES:
        name = COUNTRY_ALIASES[name]

    # Map to ISO2 WHO code
    return COUNTRY_MAP.get(name, country_name)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()
    intent_name = req["queryResult"]["intent"]["displayName"]
    parameters = req["queryResult"]["parameters"]

    # Normalize params
    disease = normalize_param(parameters.get("disease"))
    data_type = normalize_param(parameters.get("data_type"))
    indicator = normalize_param(parameters.get("indicator"))
    country = normalize_param(parameters.get("geo-country"))
    year = normalize_param(parameters.get("year"))

    # Extract year if it's a full date
    if year and len(year) >= 4:
        year = year[:4]

    # Normalize country
    country_code = normalize_country(country)

    response_text = ""

    if intent_name == "get_disease_data":
        if disease and data_type and country_code and year:
            key = f"{disease.lower()}_{data_type.lower()}"
            indicator_code = INDICATOR_MAP.get(key)
            if indicator_code:
                response_text = fetch_who_data(indicator_code, country_code, year)
            else:
                response_text = f"Sorry, I don’t have data mapping for {disease} {data_type}."
        else:
            response_text = "Please provide disease, data type, country, and year."

    elif intent_name == "get_indicator_data":
        if indicator and country_code and year:
            indicator_code = INDICATOR_MAP.get(indicator.lower())
            if indicator_code:
                response_text = fetch_who_data(indicator_code, country_code, year)
            else:
                response_text = f"Sorry, I could not find the indicator {indicator}."
        else:
            response_text = "Please provide indicator, country, and year."

    elif intent_name == "get_disease_overview":
        if disease:
            response_text = f"{disease} is a disease. WHO provides detailed statistics for it."
        else:
            response_text = "Please provide the disease name."

    else:
        response_text = "Sorry, I don't understand your request."

    return jsonify({"fulfillmentText": response_text})


# --- Fetch WHO data ---
def fetch_who_data(indicator_code, country, year):
    if not indicator_code or not country or not year:
        return "Missing parameters to fetch WHO data."

    url = f"{WHO_API_BASE}{indicator_code}?$filter=SpatialDim eq '{country}' and TimeDim eq {year}"
    try:
        r = requests.get(url)
        data = r.json()
        if "value" in data and len(data["value"]) > 0:
            result = data["value"][0]
            val = result.get("NumericValue") or result.get("Display")
            return f"The value for {indicator_code} in {country} for {year} is {val}."
        else:
            return f"No data found for {indicator_code} in {country} for {year}."
    except Exception as e:
        return f"Error fetching data: {str(e)}"


if __name__ == '__main__':
    app.run(debug=True)
