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

# -------- Helper Function: Fetch WHO Data --------
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

# -------- Helper Function: Dynamic Indicator Lookup --------
def get_indicator_code_from_disease(disease, data_type=None):
    """
    Search WHO Indicator API for the given disease name.
    Optionally filter further using data_type keyword.
    """
    try:
        url = f"{WHO_API_BASE}Indicator?$filter=contains(IndicatorName,'{disease}')"
        print("DEBUG LOOKUP URL:", url)
        r = requests.get(url)
        if r.status_code != 200:
            return None, f"WHO API returned {r.status_code} while searching for {disease}."

        data = r.json()
        indicators = data.get("value", [])
        if not indicators:
            return None, f"No indicators found for {disease}."

        # If data_type provided, filter by it
        if data_type:
            for ind in indicators:
                if data_type.lower() in ind.get("IndicatorName", "").lower():
                    print("DEBUG MATCHED INDICATOR:", ind)
                    return ind["IndicatorCode"], None

        # Otherwise return the first one
        print("DEBUG DEFAULT INDICATOR:", indicators[0])
        return indicators[0]["IndicatorCode"], None

    except Exception as e:
        return None, f"Error fetching indicator code: {str(e)}"


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()
    intent_name = req["queryResult"]["intent"]["displayName"]
    params = req["queryResult"].get("parameters", {})

    # -------- Helper to normalize params --------
    def normalize_param(value):
        if isinstance(value, list):
            return value[0] if value else ""
        return value or ""

    # Extract parameters safely
    country_input = normalize_param(params.get("geo-country"))
    disease = normalize_param(params.get("disease"))
    data_type = normalize_param(params.get("data_type"))
    indicator = normalize_param(params.get("indicator"))
    year = normalize_param(params.get("year"))

    if year:
        year = year[:4]  # handle full date format

    # Normalize country name using aliases
    country_key = COUNTRY_ALIASES.get(country_input.lower(), country_input.lower()) if country_input else None
    country_code = COUNTRY_MAP.get(country_key) if country_key else None

    # -------- Debug: Log extracted params --------
    print("DEBUG PARAMS:")
    print(f"  Intent: {intent_name}")
    print(f"  Disease: {disease}")
    print(f"  Data Type: {data_type}")
    print(f"  Indicator: {indicator}")
    print(f"  Country Input: {country_input} -> Country Code: {country_code}")
    print(f"  Year: {year}")

    response_text = ""

    # -------- Get Disease Data --------
    if intent_name == "get_disease_data":
        if not disease or not data_type or not country_code or not year:
            response_text = "Please provide disease, data type, country, and year."
        else:
            key = f"{disease.lower()}_{data_type.lower()}"
            indicator_code = INDICATOR_MAP.get(key)

            # If not in static map, try dynamic lookup
            if not indicator_code:
                print(f"DEBUG: Static map did not find key {key}. Trying dynamic lookup...")
                indicator_code, err = get_indicator_code_from_disease(disease, data_type)
                if not indicator_code:
                    response_text = err or f"No indicator found for {disease} ({data_type})."
                else:
                    print(f"DEBUG: Using dynamic indicator {indicator_code}")
                    response_text = fetch_who_data(indicator_code, country_code, year)
            else:
                print(f"DEBUG: Using static indicator {indicator_code}")
                response_text = fetch_who_data(indicator_code, country_code, year)

    # -------- Get General Indicator Data --------
    elif intent_name == "get_indicator_data":
        if not indicator or not country_code or not year:
            response_text = "Please provide indicator, country, and year."
        else:
            indicator_code = INDICATOR_MAP.get(indicator.lower())
            if not indicator_code:
                print(f"DEBUG: Static map did not find indicator {indicator}. Trying dynamic lookup...")
                indicator_code, err = get_indicator_code_from_disease(indicator)
                if not indicator_code:
                    response_text = err or f"No indicator found for {indicator}."
                else:
                    print(f"DEBUG: Using dynamic indicator {indicator_code}")
                    response_text = fetch_who_data(indicator_code, country_code, year)
            else:
                print(f"DEBUG: Using static indicator {indicator_code}")
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


if __name__ == '__main__':
    app.run(debug=True)
