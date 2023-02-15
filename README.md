# tidetimes
A simple Python script that updates a [Pimoroni Inky wHAT](https://shop.pimoroni.com/products/inky-what?variant=13590497624147) with the local sea and weather information.
## What is shown?

 - The current date
 - A short forecast for the day
 - The sea and air temperture
 - Sunrise and sunset times
 - The tide high and lows
 - And a nice graph, showing the rise and fall of the tides

## How does it work?
The script uses Requests to do web scraping. It pulls data from the BBC (for the [weather forecast](https://www.bbc.co.uk/weather/), and the [tide times](https://www.bbc.co.uk/weather/coast-and-sea/tide-tables/) - where the graph comes from), Sea Temperature (for the sea temperatures!) It then creates an image and displays it on the eInk screen. It is designed to run every day in a cronjob.

## How do I make it work?
The code is very thrown together. :) It is written for me, you *will* need to make changes. If nothing else, you'll need to edit the URLs to change the locations so the weather is right. :)

One day I may refactor it, but today is not that day. Use it as a starting point.
