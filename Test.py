from flask import Flask, request, jsonify
#import psycopg2
import requests
from datetime import datetime

app = Flask(__name__)

# Database connection parameters
#DB_PARAMS = {
#    "dbname": "coderpad",
#    "user": "coderpad",
#    "host": "/tmp/postgresql/socket"
#}

# Weather API URL
WEATHER_API_POINTS = "https://api.weather.gov/points/{lat},{lon}"
WEATHER_API_FORECAST = "https://api.weather.gov/gridpoints/{gridId}/{gridX},{gridY}/forecast"

#def get_db_connection():
#    return psycopg2.connect(**DB_PARAMS)

"""def get_user_info(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT subscriber_id, phone_number, last_payment_time FROM subscribers WHERE subscriber_id = %s",
            (user_id,)
        )
        result = cursor.fetchone()
        conn.close()
        if result:
            return {
                "subscriber_id": result[0],
                "phone_number": result[1],
                "last_payment_time": result[2].strftime("%Y-%m-%d %H:%M:%S")  # User-readable format
            }
        return None
    except Exception as e:
        return {"error": str(e)}"""

def get_weather_info(lat, lon):
    try:
        # Translate longitude and latitude into grid coordinates
        print(f"Fetch grid Coordinates for lat and lon: {lat}, {lon}")
        response = requests.get(WEATHER_API_POINTS.format(lat=lat, lon=lon))
        response.raise_for_status()
        gridData = response.json()
        gridId = gridData["properties"]["gridId"]
        gridX = gridData["properties"]["gridX"]
        gridY = gridData["properties"]["gridY"]
        print(f"gridId: {gridId}")
        print(f"gridX: {gridX}")

        # Call weather API
        print(f"Fetching weather data for coordinates: {gridX}, {gridY}")
        response2 = requests.get(WEATHER_API_FORECAST.format(gridId=gridId, gridX=gridX, gridY=gridY))
        response2.raise_for_status()
        weather_data = response2.json()

        # Return user-readable weather info
        return {
            "period": weather_data["properties"]["periods"][0]["name"],
            "temperature": weather_data["properties"]["periods"][0]["temperature"],
            "temperatureUnit": weather_data["properties"]["periods"][0]["temperatureUnit"],
            "shortForecast": weather_data["properties"]["periods"][0]["shortForecast"]
        }
    except Exception as e:
        print(f"Exception: {str(e)}")
        return {"error": str(e)}

@app.route('/user-info', methods=['GET'])
def user_info():
    #user_id = request.args.get('user_id')
    lat = request.args.get('lat')
    lon = request.args.get('lon')

    #if not user_id:
    #    return jsonify({"error": "Missing user_id parameter"}), 400
    if not lat:
        return jsonify({"error": "Missing lat parameter"}), 400
    if not lon:
        return jsonify({"error": "Missing lon parameter"}), 400
    
    # Fetch user info from database
    #user_data = get_user_info(user_id)
    #if not user_data:
    #    return jsonify({"error": "User not found"}), 404

    # Fetch weather info
    weather_data = get_weather_info(lat, lon)
    print(f"Weather Data: {weather_data}")

    if "error" in weather_data:
        return jsonify({"error": "Failed to fetch weather information"}), 500

    # Combine and return response
    #return jsonify({
    #    "subscriber_id": user_data["subscriber_id"],
    #    "phone_number": user_data["phone_number"],
    #    "weather": weather_data,
    #    "last_payment_time": user_data["last_payment_time"]
    #})
    return jsonify(weather_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
