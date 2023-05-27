#!/usr/bin/python3
import requests, re, json, time, argparse, sys, arrow, os

from dotenv import load_dotenv

load_dotenv()


parser = argparse.ArgumentParser(description='Display tide times')
parser.add_argument('--no-image', dest='no_image', action='store_true', help="Don't try to generate an image. Just grab data and exit.")
parser.set_defaults(no_image=False)

args = parser.parse_args()



today = time.strftime("%Y-%m-%d")


def get_data(url, regex):
    r = requests.get(url)
    result = re.search(regex, r.text)
    
    return result.group(1)


# tides
all_tide_data = json.loads(
    get_data(
        "https://www.bbc.co.uk/weather/coast-and-sea/tide-tables/10/29",
        r"data-data-id=\"tides\">([^<]+)</script>",
    )
)
today_tide = [a for a in all_tide_data["tides"] if a["date"] == today][0]

print ('today_tide', today_tide)

# weather
all_forecast_data = json.loads(
    get_data(
        "https://www.bbc.co.uk/weather/2654726",
        r"data-state-id=forecast>([^<]+)</script>",
    )
)
print ('all_forecast_data', all_forecast_data)

today_forecast = [
    a["summary"]["report"]
    for a in all_forecast_data["data"]["forecasts"]
    if a["summary"]["report"]["localDate"] == today
][0]

print ('today_forecast', today_forecast)


# sea temperature
response = requests.get(
  'https://api.stormglass.io/v2/weather/point',
  params={
    'lat': 50.695538,
    'lng': -2.731526,
    'params': ','.join(['waveHeight', 'waterTemperature']),
    'start': arrow.now().replace(hour=12).floor('hour').to('UTC').timestamp(),  # Start at midday
    'end': arrow.now().replace(hour=12).ceil('hour').to('UTC').timestamp()  
  },
  headers={
    'Authorization': os.getenv('STORMGLASS_API')
  }
)
stormglass_data = response.json()
print (stormglass_data)

# request_json = "{'hours': [{'time': '2023-05-27T12:00:00+00:00', 'waterTemperature': {'meto': 15.1, 'noaa': 12.24, 'sg': 15.1}, 'waveHeight': {'dwd': 0.2, 'icon': 0.87, 'meteo': 0.73, 'meto': 0.23, 'noaa': 0.8, 'sg': 0.23}}], 'meta': {'cost': 1, 'dailyQuota': 10, 'end': '2023-05-27 12:59', 'lat': 50.695538, 'lng': -2.731526, 'params': ['waveHeight', 'waterTemperature'], 'requestCount': 4, 'start': '2023-05-27 12:00'}}".replace("\'", "\"")

# stormglass_data = json.loads(request_json)

sea_temp = round(stormglass_data['hours'][0]['waterTemperature']['sg']);

print ('sea_temp', sea_temp)

if args.no_image:
  print ('Got data, now quitting')
  sys.exit(0)



import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as tick
import datetime as dt
import dateutil
import pandas as pd


df = pd.DataFrame(today_tide["heightAboveChartDatum"])

df.time = pd.to_datetime(df.time, format="%Y-%m-%dT%H:%M%z")

plt.rc("ytick", labelsize=8)
plt.rc("xtick", labelsize=8)
fig, ax = plt.subplots(figsize=(4.0, 1.4))
ax.plot(df.time, df.mm)

# ax.set_xlabel('Time')
ax.xaxis.set_major_formatter(
    mdates.DateFormatter("%H:%M", tz=dateutil.tz.gettz("Europe/London"))
)
ax.xaxis.set_major_locator(mdates.HourLocator(interval=4))


# ax.set_ylabel('Height')
ax.yaxis.set_major_formatter(tick.FuncFormatter(lambda y, _: y / 1000))

# plt.gca().xaxis.set_minor_locator(mdates.HourLocator())
# current time line
# ax.axvline(dt.datetime.now(dateutil.tz.gettz('Europe/London')), color='r')
ax.margins(x=0)
ax.grid(True)


ax.spines["top"].set_visible(False)
# ax.spines['right'].set_visible(False)
ax.spines["bottom"].set_visible(False)
ax.spines["left"].set_visible(False)


from PIL import Image, ImageFont, ImageDraw

fig.tight_layout()
fig.canvas.draw()

# Turn graph into an image
graph_image = Image.frombytes(
    "RGB", fig.canvas.get_width_height(), fig.canvas.tostring_rgb()
)


import font_source_sans_pro
import font_font_awesome
from inky import InkyWHAT

# Set up the correct display and scaling factors
inky_display = InkyWHAT("red")
inky_display.set_border(inky_display.WHITE)
# inky_display.set_rotation(180)

w = inky_display.WIDTH
h = inky_display.HEIGHT

# Create a new canvas to draw on

img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))
draw = ImageDraw.Draw(img)

# Date
draw.multiline_text(
    (30, 10),
    time.strftime("%A, %e %B %Y"),
    fill=inky_display.BLACK,
    font=ImageFont.truetype(font_source_sans_pro.SourceSansProSemibold, 28),
    align="left",
)


# Forecast
draw.multiline_text(
    (30, 45),
    today_forecast["enhancedWeatherDescription"],
    fill=inky_display.BLACK,
    font=ImageFont.truetype(font_source_sans_pro.SourceSansPro, 18),
    align="left",
)
draw.multiline_text(
    (30, 62),
    today_forecast["precipitationProbabilityText"],
    fill=inky_display.BLACK,
    font=ImageFont.truetype(font_source_sans_pro.SourceSansPro, 18),
    align="left",
)


def text_grid(arr, position):
    for i, item in enumerate(arr):
        # icon
        draw.text(
            (i * 95 + position[0], position[1] + 12),
            item[0],
            fill=inky_display.BLACK,
            anchor="mm",
            font=ImageFont.truetype(font_font_awesome.FontAwesome5FreeSolid, 20),
        )
        # value
        draw.text(
            (i * 95 + position[0] + 12, position[1]),
            item[1],
            fill=inky_display.BLACK,
            font=ImageFont.truetype(font_source_sans_pro.SourceSansPro, 20),
        )


# Temp
temps = [
    ("\uF043", "{}°C".format(sea_temp)),
    ("\uF2C7", "{}°C".format(today_forecast["mostLikelyHighTemperatureC"])),
    ("\uF185", today_forecast["sunrise"]),
    ("\uF186", today_forecast["sunset"]),
]
text_grid(temps, (33, 100))


# Tide times
extremes = [
    (
        "\uF107" if t["type"] == "Low" else "\uF106",
        dateutil.parser.parse(t["timestamp"]).strftime("%H:%M"),
    )
    for t in today_tide["extremes"]
]
text_grid(extremes, (33, 135))


# Convert the image to use a white / black / red colour palette


pal_img = Image.new("P", (1, 1))
pal_img.putpalette((255, 255, 255, 0, 0, 0, 255, 0, 0) + (0, 0, 0) * 252)
graph_image = graph_image.convert("RGB").quantize(palette=pal_img)


img.paste(graph_image, (0, 170))


inky_display.set_image(img)
inky_display.show()
