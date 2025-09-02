from flask import Flask, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

# WHO OData base URL
BASE_URL = "https://ghoapi.azureedge.net/api/"

def fetch_from_who(indicator, place=None, year=None):
    """
    Fetch data dynamically from WHO OData API.
    Only applies filters if user provided place/year.
    """
    url = f"{BASE_URL}{indicator}"
    filters = []

    if place:
        filters.append(f"SpatialDim eq '{place}'")
    if year:
        filters.append(f"TimeDim eq {year}")

    params = {}
    if filters:
        params["$filter"] = " and ".join(filters)

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return {
            "error": f"WHO OData API returned status {response.status_code}",
            "url": url,
            "filters": params
        }

    return response.json()


@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json(silent=True, force=True)

    # Extract intent name
    intent_name = req.get("queryResult", {}).get("intent", {}).get("displayName", "")

    if intent_name != "get_health_data":
        return jsonify({"fulfillmentText": "Intent not supported."})

    # Extract parameters
    params = req.get("queryResult", {}).get("parameters", {})
    indicator = params.get("indicator", "")
    disease = params.get("disease", "")
    place = params.get("place", "")
    year = params.get("year", "")

    # Validate indicator
    if not indicator:
        return jsonify({"fulfillmentText": "Please specify what health indicator you want (e.g., deaths, cases)."})

    # Call WHO API
    data = fetch_from_who(indicator, place, year)

    # Check for errors
    if "error" in data:
        return jsonify({
            "fulfillmentText": (
                f"Sorry, I couldn’t fetch the data. {data['error']} "
                f"(Query tried: {data['url']} with {data.get('filters', {})})"
            )
        })

    # Extract results
    values = data.get("value", [])
    if not values:
        return jsonify({
            "fulfillmentText": (
                f"No data found for {indicator} "
                f"{'in ' + place if place else ''} "
                f"{'for ' + str(year) if year else ''}."
            )
        })

    # Pick first result (can be extended for multiple)
    record = values[0]
    value = record.get("NumericValue", "N/A")

    # Build response
    response_text = (
        f"According to WHO, the {indicator.replace('_', ' ')} "
        f"{'for ' + disease if disease else ''} "
        f"{'in ' + place if place else ''} "
        f"{'during ' + str(year) if year else ''} "
        f"is {value}."
    )

    # Add metadata for debugging
    metadata = {
        "query": req.get("queryResult", {}).get("queryText", ""),
        "indicator": indicator,
        "place": place,
        "year": year,
        "disease": disease,
        "source": "WHO OData API",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    return jsonify({
        "fulfillmentText": response_text,
        "source": "webhook",
        "metadata": metadata
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
