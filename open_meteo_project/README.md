# ICA Historical Weather Data Application

## This is an assessment project.
## Author: [Jesubukade Emmanuel Ajakaye](https://github.com/ajabuka)

### Description
This is a project is an individual in-course assignment (ICA) that assess:
- Personal and Transferable Skills Development
- Research, Knowledge and Cognitive Skills
- Professional Skills

### Modules
The goal of the project was to:
- Phase_1: complete function that queries the local database and prints results
- Phase_2: develop visualizations based on the queries data
- Phase_3: update local database from the [Open Meteo Historical data](https://open-meteo.com/)
- further_enhancement: enhance the developments for user interactions.
- project_app: develops a simple FastApi app

### Installations
If not installed before, the following library/packages will be required to successful run these moudules.
* matplotlib
* pandas
* geopandas
* geopy
* timezonefinder
* "fastapi[standard]" (ensure to put in quotes)
* pydantic

Open your command propmt as the case maybe and type the following:

    pip install package

### Description/Instructions
#### Phase_1: Local Database Query
This moudule has 10 functions quering the database, 1 function to establish connection and the main function where all of these functions are called.
The function names are self decriptives, documentation has been provided for each to understand the agruements and what is been returned.

#### Phase_2: Visualization
Only matplotlib was used in this module and 9 charts were developed:
1. **plot_map_of_cities:** This shows the geographical position of the cities in the local database on earth map. It uses the latitude and logitude to find the cordinates on shapefiles linked to an enhancement feature.
2. **plot_average_annual_temperature:** This chart is a grouped barchart of average annual temperature over all years and cities in the database.
3. **plot_average_seven_day_precipitation:** This chart is a line chart of average seven day preciptation over in all cities in the database over a specified period of time (best to check over a year duration).
4. **plot_average_mean_temp_by_city:** This chart is a bar chart of average mean temoerature by each city in the database over a specified period of time. The average line of all cities in this period is added.
5. **plot_average_annual_precipitation_by_country:** This chart is a grouped bar chart of average annual preciptation over all years and countries in the database.
6. **plot_city_histogram:** This chart display 4 histograms of min_temp, max_temp, mean_temp and precipitation of the inputed city and year.
7. **plot_city_scatter:** This chart scatter chart of mean_temp and precipitation of the inputed city and year. The regression line was added in this chart.
8. **plot_city_data_by_year:** This chart is a line chart of min_temp, max_temp and mean_temp of the inputed city and year over a specified period of time.
9. **plot_average_seven_day_data:** This chart is a line chart of min_temp, max_temp and mean_temp and bar chart of precipitation of averages over seven days (inspiration gotten from the open meteo website viualization).

#### Phase_3: External Database Query (Open Meteo)
This module uses a get request from open meteo historical data api and updates the local database. The module has 6 functions. 1 for fetching require data using api and 5 others to update the database.

**fetch_data_from_meteo_api** - take the city, start_date and end_date as arguments, automatically generates other parameters through geocoding enhancement feature and returns a list of lists

**Note:** check documentation for what functions does.

#### further_enhancement
This module is just to add extra feature to the other modules. 4 functions are developed here and most mentioned in other modules descriptions.

#### project_app: Intructions for FastApi
The fourth section under further_enhancement is a **Simple Web Micro-Service** using [**FastApi**](https://fastapi.tiangolo.com/). This is an interactive web service that can be used to query the database (get request) and has also be designed to update the local database from the open meteo database.

***Step 1***
Run the further_enhancement.py in your command prompt or bash to run the server

***Step 2***
Copy and paste http://127.0.0.1:8000/docs in your prefered broswer.

***Step 3***
For local database query click on [GET /get-ICA-weather-data](http://127.0.0.1:8000/docs#/default/read_item_get_ICA_weather_data_get)

***Step 4***
Click on "Try it out", fill required fields and Click "Execute" Data formats are specified and checked for my app.

***Step 5***
Under Responses, server response shows return returned. also, see Request URL, you can copy the link and paste in your browser to see the return JSON. This get request can also be created by building the url with the base url and parameters

    example: http://127.0.0.1:8000/get-ICA-weather-data?city=London&start_date=2020-01-01&end_date=2020-01-31

    base url = http://127.0.0.1:8000/get-ICA-weather-data

    params:
        city
        start_date
        end_date

***Step 6***
To update local database click on [PUT /update-from-meteo](http://127.0.0.1:8000/docs#/default/update_item_update_from_meteo_put)

***Step 7***
Click on "Try it out", fill required fields and Click "Execute" Data formats are specified and checked for my app.

**Note:**
You cannot copy the link here as it is not a get request. It will return error: Also at the Response view, you can see the time taken for the update to be complete, If there are any error please check your command prompt of bash for error information.