from flask import Flask, request, jsonify
import requests
import datetime

app = Flask(__name__)

# WHO OData API base URL
ODATA_API_URL = "https://ghoapi.azureedge.net/odata"

# Map indicators to default diseases if disease param is missing
INDICATOR_TO_DISEASE = {
    "death_cases": "covid",
    "confirmed_cases": "covid",
    "mortality_rate": "covid",
    "life_expectancy": "",
    "incidence_rate": ""
}

# Map indicators to WHO OData API endpoints
INDICATOR_TO_ODATA = {
    "death_cases": "GHO/DEATHS_COVID",
    "confirmed_cases": "GHO/CONFIRMED_COVID",
    "mortality_rate": "GHO/MORTALITY_RATE_COVID",
    "life_expectancy": "GHO/LIFE_EXPECTANCY",
    "incidence_rate": "GHO/INCIDENCE_RATE"
}

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
        query_text = data.get("queryResult", {}).get("queryText", "")

        # Extract only relevant parameters
        parameters = data.get("queryResult", {}).get("parameters", {})
        indicator = parameters.get("indicator", "").lower()
        place = parameters.get("place", "")
        year = parameters.get("year", "")
        disease = parameters.get("disease", "")

        # Ignore extra parameters
        # Automatically infer disease if missing
        if not disease:
            disease = INDICATOR_TO_DISEASE.get(indicator, "")
            if not disease and "covid" in query_text.lower():
                disease = "covid"

        # Map indicator to WHO OData endpoint
        odata_endpoint = INDICATOR_TO_ODATA.get(indicator, indicator)

        result_value = "Data not found"

        # Build OData API URL dynamically
        if indicator and year:
            filter_parts = []
            if place:
                filter_parts.append(f"SpatialDim eq '{place}'")
            if year:
                filter_parts.append(f"TimeDim eq '{year}'")
            filter_query = " and ".join(filter_parts)
            odata_url = f"{ODATA_API_URL}/{odata_endpoint}?$filter={filter_query}"

            # Debugging
            print("Fetching WHO OData:", odata_url)
            print("Indicator:", indicator, "Disease:", disease, "Place:", place, "Year:", year)

            # Fetch data
            try:
                response = requests.get(odata_url, timeout=5)
                if response.status_code == 200:
                    data_json = response.json()
                    if "value" in data_json and len(data_json["value"]) > 0:
                        result_value = data_json["value"][0].get("NumericValue", "Data not found")
                    else:
                        result_value = "No data available for given parameters"
                else:
                    result_value = f"WHO OData API returned status code {response.status_code}"
            except Exception as e:
                result_value = f"Error fetching data: {str(e)}"
        else:
            result_value = "Indicator or year missing in the query"

        # Add extra metadata
        metadata = {
            "query": query_text,
            "indicator": indicator,
            "place": place,
            "year": year,
            "disease": disease,
            "source": "WHO OData API",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        }

        # Construct dynamic response
        fulfillment_text = (
            f"Total {indicator.replace('_',' ')} for {disease.capitalize()} in {place} ({year}): {result_value}\n"
            f"(Metadata: {metadata})"
        )

        return jsonify({
            "fulfillmentText": fulfillment_text,
            "fulfillmentMessages": [
                {"text": {"text": [fulfillment_text]}}
            ],
            "source": "general-health-stats-1.onrender.com"
        })

    except Exception as e:
        error_text = f"Webhook error: {str(e)}"
        return jsonify({
            "fulfillmentText": error_text,
            "fulfillmentMessages": [{"text": {"text": [error_text]}}],
            "source": "general-health-stats-1.onrender.com"
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
