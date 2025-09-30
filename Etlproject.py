import requests
import mysql.connector
from datetime import datetime, timedelta

# ====== CONFIGURATION ====== #
API_KEY = "c3a925d18a4d4cb39a8173626253105"
CITIES = [
    "Portland", "Eugene", "Corvallis", "Bend", "Medford",
    "Ashland", "Beaverton", "Hillsboro", "Albany",
    "Gresham", "Astoria", "Sisters", "Woodburn"
]
DAYS = 7
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '*******',
    'database': 'weather_db'
}
END_DATE = datetime(2025, 2, 28)
# ============================ #

# Step 1: Connect to MySQL
try:
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    print("✅ Connected to MySQL database.")
except mysql.connector.Error as err:
    print(f"❌ Database connection error: {err}")
    exit()

# Step 2: Define SQL Insert Query for 30 fields
INSERT_QUERY = """
INSERT INTO weather_forecast (
    city, country, state, forecast_date, forecast_hour,
    time_epoch, temp_c, feelslike_c, humidity, dewpoint_c,
    precip_mm, chance_of_rain, will_it_rain, wind_kph, gust_kph,
    wind_dir, wind_degree, cloud, vis_km, uv_index,
    pressure_mb, condition_text, is_day, data_source_time,
    windchill_c, heatindex_c, snow_cm, chance_of_snow,
    sunrise, sunset
) VALUES (
    %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s
)
"""

# Step 3: Loop through cities and days
for city in CITIES:
    print(f"\n📍 Collecting data for: {city}")
    for day_offset in range(DAYS):
        date = END_DATE - timedelta(days=day_offset)
        date_str = date.strftime("%Y-%m-%d")
        url = f"http://api.weatherapi.com/v1/history.json?key={API_KEY}&q={city}&dt={date_str}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"⚠️ API error for {city} on {date_str}: {e}")
            continue

        if "forecast" not in data:
            print("⚠️ No forecast data found.")
            continue

        country = data["location"]["country"]
        data_source_time = datetime.now()

        # Sunrise and sunset come from astro object once per day
        astro = data["forecast"]["forecastday"][0]["astro"]
        try:
            sunrise = datetime.strptime(astro["sunrise"], "%I:%M %p").time()
            sunset = datetime.strptime(astro["sunset"], "%I:%M %p").time()
        except ValueError:
            sunrise = sunset = None

        for hour in data['forecast']['forecastday'][0]['hour']:
            forecast_date, forecast_hour = hour['time'].split(' ')

            record = (
                city, country, "Oregon", forecast_date, forecast_hour,
                hour['time_epoch'],
                hour['temp_c'], hour['feelslike_c'], hour['humidity'], hour['dewpoint_c'],
                hour['precip_mm'], hour.get('chance_of_rain', 0), hour.get('will_it_rain', 0),
                hour['wind_kph'], hour['gust_kph'],
                hour['wind_dir'], hour['wind_degree'], hour['cloud'], hour['vis_km'], hour['uv'],
                hour['pressure_mb'], hour['condition']['text'], hour['is_day'], data_source_time,
                hour.get('windchill_c'), hour.get('heatindex_c'), hour.get('snow_cm'), hour.get('chance_of_snow'),
                sunrise, sunset
            )

            cursor.execute(INSERT_QUERY, record)

        conn.commit()
        print(f"  ✅ {date_str} data inserted.")

# Step 4: Clean up
cursor.close()
conn.close()
print("\n🎉 All 30-column weather data successfully loaded into MySQL!")
