import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()
    intent = req.get("queryResult").get("intent").get("displayName")

    if intent == "get_life_expectancy":
        # Extract parameters from Dialogflow
        country = req.get("queryResult").get("parameters").get("geo-country")
        year = req.get("queryResult").get("parameters").get("year")

        # WHO Indicator Code for Life Expectancy
        indicator_code = "WHOSIS_000001"

        url = f"https://ghoapi.azureedge.net/api/{indicator_code}?$filter=SpatialDim eq '{country.upper()}' and TimeDim eq {year}"
        response = requests.get(url)
        data = response.json()

        if "value" in data and len(data["value"]) > 0:
            value = data["value"][0]["NumericValue"]
            reply = f"According to WHO, the life expectancy in {country} in {year} was {value} years."
        else:
            reply = f"Sorry, I couldn’t find WHO data for {country} in {year}."

    else:
        reply = "I can fetch WHO data, but I need a valid intent."

    return jsonify({"fulfillmentText": reply})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
