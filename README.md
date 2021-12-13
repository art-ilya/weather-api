# weather-api
Service getting weather data

# Setup
git clone https://github.com/art-ilya/weather-api.git

run "docker-compose up -d --build"

Open in browser http://localhost:8000/docs and try it!

# Testing and developing
For testing and developing you can use:
 - VSCode devcontainer (with "Remote - Containers" plugin)
 - Start it manually:
   
   1) run "docker-compose -f .devcontainer/docker-compose.debug.yml up -d --build"
   2) connect to container cli (via docker or vscode)
   3) on the first launch run "pipenv update -d"
   4) enter "pipenv shell" for activating venv
   5) to run tests: "pytest ./tests/"
   6) to run dev server: "python ./weather_api/main.py"

# Limitations
This service uses the openweathermap api and is limited to choosing a date +- 5 days from the current one (due to the limitations of the free plan) and do 60 calls/minute. See current Free plan limitations on https://openweathermap.org/price
