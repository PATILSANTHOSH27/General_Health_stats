from flask import Flask, request, jsonify

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
    "life_expectancy": "SP.DYN.LE00.IN",
    "maternal_mortality": "SH.MMR.DTHS",
    # Add more indicators as needed
}

# -------- Static Mapping of Countries --------
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
    # Add more countries as needed
}

# Optional aliases for user input variations
COUNTRY_ALIASES = {
    "us": "united states",
    "america": "united states",
    "uk": "united kingdom",
    "uae": "united arab emirates",
}

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()
    intent_name = req["queryResult"]["intent"]["displayName"]
    params = req["queryResult"].get("parameters", {})

    # Adjust extraction
    disease = params.get("any", [None])[0] if params.get("any") else None
    data_type = params.get("any", [None])[1] if len(params.get("any", [])) > 1 else None
    country_input = params.get("geo-country", [None])[0] if params.get("geo-country") else None
    year = params.get("year", [None])[0] if params.get("year") else None

    #country_input = params.get("country") or ""
    #disease = params.get("disease") or ""
    #indicator = params.get("indicator") or ""
    #data_type = params.get("data_type") or ""
    #year = params.get("year") or ""

    if year:
        year = year[:4]

    # Normalize country name using aliases
    country_key = COUNTRY_ALIASES.get(country_input.lower(), country_input.lower())
    country_code = COUNTRY_MAP.get(country_key)

    response_text = ""

    # -------- Get Disease Data --------
    if intent_name == "get_disease_data":
        if not disease or not data_type or not country_code or not year:
            response_text = "Please provide disease, data type, country, and year."
        else:
            key = f"{disease.lower()}_{data_type.lower()}"
            indicator_code = INDICATOR_MAP.get(key)
            if indicator_code:
                response_text = f"The value for {key} in {country_code} for {year} is [sample data]."
            else:
                response_text = f"No indicator found for {key}."

    # -------- Get General Indicator Data --------
    elif intent_name == "get_indicator_data":
        if not indicator or not country_code or not year:
            response_text = "Please provide indicator, country, and year."
        else:
            indicator_code = INDICATOR_MAP.get(indicator.lower())
            if indicator_code:
                response_text = f"The value for {indicator} in {country_code} for {year} is [sample data]."
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
