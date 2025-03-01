import requests
import pandas as pd
import json
import time
import pycountry
import re
from unidecode import unidecode  # For transliteration


# File paths
input_file = "./radio_garden_places.txt"
output_file = "./RadioGarden_Complete_Data.xlsx"

# Base API URLs
location_api_url = "https://radio.garden/api/ara/content/page/"
channel_api_url = "https://radio.garden/api/ara/content/channel/"
stream_api_url = "https://radio.garden/api/ara/content/listen/{channel_id}/channel.mp3"

# Load and fix the places data
with open(input_file, "r", encoding="utf-8") as f:
    json_str = f.read().strip()

if not json_str.endswith("}}}"):
    last_valid = json_str.rfind("},")

if last_valid != -1:
    json_str = json_str[: last_valid + 1] + "]}}"

else:
    raise ValueError("Cannot find a valid JSON structure to fix")

places_data = json.loads(json_str)

# Initialize lists
names = []
latitudes = []
longitudes = []
station_names = []
stream_urls = []

# Counter for processed stations
station_count = 0


# Function to transliterate and clean text
def clean_text(text):
    # Transliterate non-Latin to Latin (e.g., "Русское" -> "Russkoe")
    transliterated = unidecode(text)

    # Keep only alphanumeric, spaces, commas, and hyphens
    cleaned = "".join(c for c in transliterated if c.isalnum() or c in " ,-")

    # Remove extra spaces and ensure not empty
    cleaned = cleaned.strip()
    return cleaned if cleaned else "Unknown Station"


# Function to get 2-letter country code
def get_country_code(country_name):
    try:
        country = pycountry.countries.search_fuzzy(country_name)[0]
        return country.alpha_2

    except LookupError:
        return "XX"


# Function to format the "Name" field
def format_name(place_title, country):
    country_code = get_country_code(country)
    if country_code == "US":
        match = re.search(r"\b([A-Z]{2})\b$", place_title)
        if match:
            state_code = match.group(1)
            city = place_title.replace(f" {state_code}", "").strip()
            formatted = f"{city},US-{state_code}"

        else:
            formatted = f"{place_title},US"

    else:
        formatted = f"{place_title},{country_code}"

    return clean_text(formatted)


# Function to save progress to Excel (overwrites each time)
def save_progress():
    combined_df = pd.DataFrame(
        {
            "Name": names,
            "Value.coords.n": latitudes,
            "Value.coords.e": longitudes,
            "Value.urls.name": station_names,
            "Value.urls.url": stream_urls,
        }
    )
    combined_df.to_excel(output_file, index=False)
    print(f"Saved {len(station_names)} stations to {output_file} (progress update)")


try:
    for place in places_data["data"]["list"]:
        location_code = place["id"]
        place_title = place.get("title", "Unknown Place")
        country = place.get("country", "Unknown Country")
        geo = place.get("geo", [None, None])
        longitude, latitude = geo[0], geo[1]
        name = format_name(place_title, country)
        location_url = f"{location_api_url}{location_code}"
        print(f"Processing: {name} ({location_code})")

        try:
            response = requests.get(location_url, timeout=10)
            response.raise_for_status()
            location_data = response.json()

            content = location_data.get("data", {}).get("content", [])
            stations_found = False
            for content_block in content:
                if content_block.get("itemsType") == "channel":
                    stations_found = True
                    for item in content_block.get("items", []):
                        station_title = item.get("title", "Unknown Station")
                        station_code = (
                            item.get("page", {}).get("url", "").split("/")[-1]
                        )

                        # Fetch station details
                        channel_url = f"{channel_api_url}{station_code}"
                        try:
                            channel_response = requests.get(channel_url, timeout=10)
                            channel_response.raise_for_status()
                            channel_data = channel_response.json()
                            station_name = channel_data.get("data", {}).get(
                                "title", station_title
                            )
                            station_name = clean_text(
                                station_name
                            )  # Clean station name

                        except requests.exceptions.RequestException as e:
                            print(f"  Failed details for {station_code}: {e}")
                            station_name = "Failed"

                        # Fetch stream URL
                        stream_url = stream_api_url.format(channel_id=station_code)
                        try:
                            stream_response = requests.head(
                                stream_url, allow_redirects=False, timeout=10
                            )
                            live_stream_url = (
                                stream_response.headers.get(
                                    "Location", "No Stream URL Found"
                                )
                                if stream_response.status_code == 302
                                else "No Stream URL Found"
                            )

                        except requests.exceptions.RequestException as e:
                            print(f"  Failed stream for {station_code}: {e}")
                            live_stream_url = "Failed"

                        # Store data
                        names.append(name)
                        latitudes.append(latitude)
                        longitudes.append(longitude)
                        station_names.append(station_name)
                        stream_urls.append(live_stream_url)

                        station_count += 1
                        print(f"  Added: {station_name} (Station #{station_count})")

                        # Save every 50 stations
                        if station_count % 50 == 0:
                            save_progress()

                        time.sleep(0.2)

            if not stations_found:
                print(f"  No stations found for {name}")

        except requests.exceptions.RequestException as e:
            print(f"Failed fetching stations for {location_code}: {e}")

        time.sleep(0.2)

except KeyboardInterrupt:
    print("\nInterrupted. Saving progress...")
    save_progress()

finally:
    save_progress()
