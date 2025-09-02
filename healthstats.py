from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Predefined metadata for indicators
indicator_metadata = {
    "covid_death_cases": {
        "description": "Number of confirmed deaths due to Covid-19",
        "unit": "People",
        "source": "World Health Organization (WHO)"
    },
    "tb_deaths": {
        "description": "Number of deaths due to Tuberculosis",
        "unit": "People",
        "source": "World Health Organization (WHO)"
    },
    "life_expectancy": {
        "description": "Average life expectancy at birth",
        "unit": "Years",
        "source": "World Health Organization (WHO)"
    }
}

# Function to fetch data from Athena API
def get_athena_data(indicator, place, year):
    url = f"https://apps.who.int/gho/athena/api/GHO/{indicator}/{place}/{year}?format=json&profile=simple"
    response = requests.get(url)
    data = response.json()
    try:
        value = data["fact"][0]["Value"]
        return value
    except:
        return None

# Function to fetch data from OData API (for multiple indicators / places / years)
def get_odata_data(indicators, places, years):
    results = []
    for ind in indicators:
        for pl in places:
            for yr in years:
                url = f"https://ghoapi.azureedge.net/api/{ind}?$filter=COUNTRY:{pl};YEAR:{yr}"
                response = requests.get(url)
                try:
                    data = response.json()
                    value = data['value'][0]['NumericValue']
                    results.append((ind, ind.split('_')[0], pl, yr, value))
                except:
                    results.append((ind, ind.split('_')[0], pl, yr, None))
    return results

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()
    parameters = req['queryResult']['parameters']
    
    # Extract parameters
    indicator = parameters.get('indicator')
    disease = parameters.get('disease')
    place = parameters.get('place')
    year = parameters.get('year')
    
    # If disease missing, extract from indicator
    if not disease:
        if isinstance(indicator, str):
            disease = indicator.split('_')[0]
        elif isinstance(indicator, list):
            disease = [ind.split('_')[0] for ind in indicator]
    
    response_text = ""
    
    # Determine single vs multiple query
    if isinstance(indicator, str) and isinstance(place, str) and isinstance(year, str):
        # Athena API for single query
        value = get_athena_data(indicator, place, year)
        if value:
            meta = indicator_metadata.get(indicator, {})
            response_text += f"{disease.title()} {indicator.replace(disease+'_','')} in {place} in {year}: {value}\n"
            if meta:
                response_text += f"Indicator: {meta.get('description','')}\n"
                response_text += f"Unit: {meta.get('unit','')}\n"
                response_text += f"Source: {meta.get('source','')}\n"
                response_text += f"Year: {year}"
        else:
            response_text = f"Sorry, data not found for {disease} in {place} for {year}."
    
    else:
        # OData API for multiple queries
        if isinstance(indicator, str):
            indicator = [indicator]
        if isinstance(place, str):
            place = [place]
        if isinstance(year, str):
            year = [year]
        
        results = get_odata_data(indicator, place, year)
        lines = []
        for ind, dis, pl, yr, val in results:
            meta = indicator_metadata.get(ind, {})
            if val:
                line = f"{dis.title()} {ind.replace(dis+'_','')} in {pl} in {yr}: {val}"
                if meta:
                    line += f"\nIndicator: {meta.get('description','')}\nUnit: {meta.get('unit','')}\nSource: {meta.get('source','')}\nYear: {yr}"
            else:
                line = f"Sorry, data not found for {dis} in {pl} for {yr}."
            lines.append(line)
        response_text = "\n\n".join(lines)
    
    return jsonify({"fulfillmentText": response_text})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
