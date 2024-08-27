#!/usr/bin/python3
#
# Simple script to display today's weather forecast and a weather-appropriate Pokemon
# Requires installation of "pokemon-colorscripts" first
#
import requests
import random
from PIL import Image, ImageEnhance
import geocoder
from io import BytesIO
from colored import stylize, fg, attr
import colorama
from colorama import init
import subprocess
import re

def is_internet_available():
    try:
        requests.get("https://api.openweathermap.org", timeout=5)
        return True
    except requests.ConnectionError:
        return False

# Example usage:
if not is_internet_available():
    print("Hey!  Wait!  Don't go out!  It's unsafe!")
    quit()

# Initialize colorama
init()


def reformat_description(description):
    # Remove line breaks and odd spacing
    description = description.replace('\n', ' ').strip()
    description = re.sub(r'\s+', ' ', description)
    
    # Split the description into words
    words = description.split(' ')
    
    # Format the description into lines
    lines = []
    current_line = ''
    for word in words:
        if len(current_line) + len(word) + 1 <= 40:  # Add 1 for the space between words
            current_line += ' ' + word if current_line else word
        else:
            lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    # Join the lines with line breaks
    formatted_description = '\n'.join(lines)
    
    return formatted_description


# Weather API to get current weather
weather_api_key = "6e47cb90e902cd66b74ba857bf19e67b"
weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={{location}}&appid={weather_api_key}&units=metric"

# Pokémon API to get Pokémon data
pokemon_url = "https://pokeapi.co/api/v2/type/"

# Get user location or detect automatically
user_location = "" # input("Enter your location (or leave blank to detect automatically): ")
if not user_location:
    g = geocoder.ip('me')
    user_location = g.city

# Get weather information for the location
weather_response = requests.get(weather_url.format(location=user_location)).json()
weather_condition = weather_response["weather"][0]["main"]
weather_temperature = weather_response["main"]["temp"]

# Define the weather-to-type mapping
weather_to_type = {
    "rain": "water",
    "snow": "ice",
    "drizzle": "dark",
    "thunderstorm": "electric",
    "clear": "flying",
    "sun": "fire",
}

# limit pokemon to what pokemon-colorscripts can provide
pokemon_image_list=subprocess.check_output(["pokemon-colorscripts","--list"]).decode("utf-8")
pokemon_image_list=pokemon_image_list.splitlines()
# print(pokemon_image_list)

# Determine Pokémon type based on weather condition
pokemon_types=["normal", "grass", "electric", "rock", "ground", "ice", "steel", "fairy", "dragon", "bug"]
pokemon_type = weather_to_type.get(weather_condition.lower(), random.choice(pokemon_types))

# Get Pokémon of the chosen type
type_response = requests.get(pokemon_url + pokemon_type).json()
pokemon_list = type_response["pokemon"]

# Randomly select a Pokémon from the list, making sure the name is in pokemon-colorscripts
random_pokemon=""
while random_pokemon not in pokemon_image_list:
    random_pokemon = random.choice(pokemon_list)["pokemon"]["name"]
    #print(random_pokemon)
    #quit()

# Did we find a shiny?
shiny=False
if random.randrange(1000)==1:
    shiny=True

# Get Pokémon details including the description and image
pokemon_response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{random_pokemon}").json()
pokemon_species_url = pokemon_response["species"]["url"]
pokemon_species_response = requests.get(pokemon_species_url).json()
pokemon_description = next(
    (
        entry["flavor_text"]
        for entry in pokemon_species_response["flavor_text_entries"]
        if entry["language"]["name"] == "en"
    ),
    ""
)
pokemon_description=reformat_description(pokemon_description)
pokemon_image_url = pokemon_response["sprites"]["front_default"]

# Display location, weather forecast, and temperature
print(f"Location: {user_location}")
print(f"Weather Forecast: {weather_condition}")
print(f"Temperature: {weather_temperature}°C")

# Display Pokémon name and description
if shiny:
    print(f"Weather-appropriate Pokémon: Shiny {random_pokemon.capitalize()}")
else:
    print(f"Weather-appropriate Pokémon: {random_pokemon.capitalize()}")
print(f"Description: {pokemon_description}")

if shiny:
    subprocess.call(["pokemon-colorscripts", "--no-title", "-s", "--name", random_pokemon])
else:
    subprocess.call(["pokemon-colorscripts", "--no-title", "--name", random_pokemon])
