import requests, json
from flask import Flask, render_template, request
from collections import OrderedDict

app = Flask(__name__)

def getCities():
    # Get cities from the Goldstar API
    cities = {}
    headers = {}
    headers["user-agent"] = "Mozilla/5.0"
    url = "https://www.goldstar.com/api/territories.json"
    json = requests.get(url, headers=headers).json()

    for i in json:
        cityUrl = i["slug"].lower()
        cities[cityUrl] = i["name"]

    # Sort the cities alphabetically
    cities = OrderedDict(sorted(cities.items()))

    return cities

def getCityId(cityName):
    # Get city ID from the Goldstar API, given city name
    headers = {}
    headers["user-agent"] = "Mozilla/5.0"
    url = "https://www.goldstar.com/api/territories.json"
    json = requests.get(url, headers=headers).json()
    cityId = next(i for i in json if i["name"] == cityName)["id"]

    return str(cityId)

# ========== HOMEPAGE ==========
@app.route("/")
def index():
    # Get the list of cities
    cities = getCities()
    print(cities)

    return render_template("index.html", cities=cities)


# ========== RESULTS PAGE ==========
@app.route("/results", methods=["GET", "POST"])
def results():
    # Redirect to index page if results page is accessed directly
    if request.method == "GET":
        return index()

    # Get data from user inputs in form fields
    cities = getCities()
    city = request.form["city"]
    cityName = request.form["cityName"]
    fromDate = request.form["startDate"]
    toDate = request.form["endDate"]
    free = request.form.getlist("free")

    # Get events data from the Goldstar API
    cityId = getCityId(cityName)
    url = "https://www.goldstar.com/api/listings.json?territory_id=" + cityId

    # Filter events by date
    if fromDate and toDate:
        url += "&from_date=" + fromDate + "&to_date=" + toDate

    # Get the json list of events
    headers = {}
    headers["user-agent"] = "Mozilla/5.0"
    json = requests.get(url, headers=headers).json()

    # Filter the listings to show only the FREE events
    if free:
        json = [
            i
            for i in json
            if "FREE" in i["our_price_range"] or "COMP" in i["our_price_range"]
        ]

    # Edit json to reduce images to thumbnail size and replace all FREE prices to 0
    for i in json:
        i["image"] += "&h=100&w=100&c=1"
        i["our_price_range"] = (
            i["our_price_range"].replace("FREE", "$0").replace("COMP", "$0")
        )

    return render_template(
        "results.html", url=url, cities=cities, cityName=cityName, items=json
    )


if __name__ == "__main__":
    app.run()