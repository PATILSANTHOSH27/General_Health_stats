from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# -------- Static Mapping of Indicators --------
INDICATOR_MAP = {
    "malaria_cases": "MALARIA_000001",
    "malaria_deaths": "MALARIA_000002",
    "tb_cases": "TB_000001",
    "tb_deaths": "TB_000002",
    "dengue_cases": "DENGUE_000001",
    "dengue_deaths": "DENGUE_000002",
    "hiv_cases": "HIV_000001",
    "hiv_deaths": "HIV_000002",
    "life_expectancy": "WHOSIS_000001",
    "maternal_mortality": "MDG_0000000029",
    # Add more indicators as needed
}

# -------- Static Mapping of Countries --------
COUNTRY_MAP = {
    "india": "IND",
    "brazil": "BRA",
    "kenya": "KEN",
    "thailand": "THA",
    "united states": "USA",
    "nigeria": "NGA",
    "china": "CHN",
    "philippines": "PHL",
    "haiti": "HTI",
    "south africa": "ZAF",
    # Add more countries as needed
}

# Optional aliases for user input variations
COUNTRY_ALIASES = {
    "us": "united states",
    "america": "united states",
    "uk": "united kingdom",
    "uae": "united arab emirates",
}

# -------- WHO API Base --------
WHO_API_BASE = "https://ghoapi.azureedge.net/api/"

# -------- Helper Function --------
def fetch_who_data(indicator_code, country, year):
    if not indicator_code or not country or not year:
        return "Missing parameters to fetch WHO data."

    url = f"{WHO_API_BASE}{indicator_code}?$filter=SpatialDim eq '{country}' and TimeDim eq {year}"
    try:
        r = requests.get(url)
        print("DEBUG URL:", url)
        print("DEBUG STATUS:", r.status_code)
        print("DEBUG RESPONSE:", r.text[:500])

        if r.status_code != 200:
            return f"WHO API returned status {r.status_code}. URL: {url}"

        data = r.json()
        if "value" in data and len(data["value"]) > 0:
            result = data["value"][0]
            val = result.get("NumericValue") or result.get("Display")
            return f"The value for {indicator_code} in {country} for {year} is {val}."
        else:
            return f"No data found for {indicator_code} in {country} for {year}."
    except Exception as e:
        return f"Error fetching data: {str(e)}"


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()
    intent_name = req["queryResult"]["intent"]["displayName"]
    params = req["queryResult"].get("parameters", {})

    # Extract parameters
    country_input = params.get("geo-country", [None])[0] if params.get("geo-country") else None
    disease = params.get("disease") or ""
    data_type = params.get("data_type") or ""
    indicator = params.get("indicator") or ""
    year = params.get("year") or ""

    if year:
        year = year[:4]  # handle full date format

    # Normalize country name using aliases
    country_key = COUNTRY_ALIASES.get(country_input.lower(), country_input.lower()) if country_input else None
    country_code = COUNTRY_MAP.get(country_key) if country_key else None

    response_text = ""

    # -------- Get Disease Data --------
    if intent_name == "get_disease_data":
        if not disease or not data_type or not country_code or not year:
            response_text = "Please provide disease, data type, country, and year."
        else:
            key = f"{disease.lower()}_{data_type.lower()}"
            indicator_code = INDICATOR_MAP.get(key)
            if indicator_code:
                response_text = fetch_who_data(indicator_code, country_code, year)
            else:
                response_text = f"No indicator found for {key}."

    # -------- Get General Indicator Data --------
    elif intent_name == "get_indicator_data":
        if not indicator or not country_code or not year:
            response_text = "Please provide indicator, country, and year."
        else:
            indicator_code = INDICATOR_MAP.get(indicator.lower())
            if indicator_code:
                response_text = fetch_who_data(indicator_code, country_code, year)
            else:
                response_text = f"No indicator found for {indicator}."

    # -------- Get Disease Overview --------
    elif intent_name == "get_disease_overview":
        if disease:
            response_text = f"{disease.capitalize()} is a disease. WHO provides detailed statistics and reports for it."
        else:
            response_text = "Please provide the disease name."

    else:
        response_text = "Sorry, I don't understand your request."

    return jsonify({"fulfillmentText": response_text})


if __name__ == '__main__':
    app.run(debug=True)
