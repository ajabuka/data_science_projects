# Author: <Jesubukade Emmanuel Ajakaye>

# Import need libraries
import os

# Enhancement 1
import pandas as pd
import geopandas as gpd

# Enhancement 2
from datetime import date, datetime
from dateutil import rrule

# Enhancement 3
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder


###############################################
# Enhancement 1: Creating data for map plotting
###############################################
def map_plotting(data):
    """
    This function helps to plot latitude and longitude of city on the world map

    Args:
        data (dictionary):  The data containing city name, longitude and latitude as keys

    Return:
        world (GeoDataFrame): For the map of Western Europe and U.K. of Great Britain and Northern Ireland
        cities (GeoDataFrame): For the maps of cities for plotting
        city_pointer (GeoDataFrame): For points of cities on the map
    """
    
    # Convert dictionary to dataframe and cast necessary columns
    df = pd.DataFrame(data)
    df['longitude'] = df['longitude'].astype(str).astype(float) 
    df['latitude'] = df['latitude'].astype(str).astype(float)


    # Import shapefiles for Countries and Cities into GeoDataFrame
    a_world = gpd.read_file("World_Cities/world-administrative-boundaries.shp")
    b_cities = gpd.read_file("World_Cities/yk247bg4748.dbf")

    # Find the geometry of cities
    try:
        # Extract Countries based on city in the dataframe
        world = a_world[(a_world["region"] == "Western Europe") | (a_world["name"] == "U.K. of Great Britain and Northern Ireland")]

        # Find the geometry of cities
        # This condition is added because of the error in Longitude and Latitude provide for the ICA
        if df['name'][0] == "Middlesbrough" and df['longitude'][0] > df['latitude'][0]:
            pointer = gpd.points_from_xy(df['latitude'], df['longitude'], crs="EPSG:4326")
            city_pointer = gpd.GeoDataFrame(df, geometry=pointer)

            # Join the city_geometry with cities of the world to extra polygon geometry
            location = gpd.sjoin(city_pointer, b_cities, how="left", predicate="dwithin", distance=0.02)
            location = location.dropna()

            # Get index and extra details from the cities GeoDataFrame
            # location["index_right"]

            cities = b_cities.iloc[[index for index in location["index_right"]]]
        else:
            pointer = gpd.points_from_xy(df['longitude'], df['latitude'], crs="EPSG:4326")
            city_pointer = gpd.GeoDataFrame(df, geometry=pointer)


            # Join the city_geometry with cities of the world to extra polygon geometry
            location = gpd.sjoin(city_pointer, b_cities, how="left", predicate="dwithin", distance=0.02)
            location = location.dropna()

            # Get index and extra details from the cities GeoDataFrame
            # location["index_right"]

            cities = b_cities.iloc[[index for index in location["index_right"]]]

        return world, cities, city_pointer
    
    except Exception as ex:
        return f"The following error occur: {ex}"


###############################################
# Enhancement 2: Creating date range function
###############################################
def get_date_range(start_date, end_date, interval="daily"):
    """
    This function calculate and return dates accorrding to intervals

    Args:
        start_date (str): the date of the day starting the query as YYYY-MM-DD
        end_date (str): the date of the day ending the query as YYYY-MM-DD
        interval (str): takes value such as "daily", "weekly" and "monthly". Default value = "daily"

    Return:
        Returns a list of date 

    """

    # convert date to usable formats
    start_date = date.fromisoformat(start_date)
    end_date = date.fromisoformat(end_date)

    list_of_dates = []

    try:
        if interval == "daily":
            for dat in rrule.rrule(rrule.DAILY, dtstart=start_date, until=end_date):
                 list_of_dates.append(dat.strftime("%Y-%m-%d"))

        elif interval == "weekly":
            for dat in rrule.rrule(rrule.WEEKLY, dtstart=start_date, until=end_date):
                 list_of_dates.append(dat.strftime("%Y-%m-%d"))

        elif interval == "monthly":
            for dat in rrule.rrule(rrule.MONTHLY, dtstart=start_date, until=end_date):
                 list_of_dates.append(dat.strftime("%Y-%m-%d"))

        # elif interval == "yearly":
        #     for dat in rrule.rrule(rrule.YEARLY, dtstart=start_date, until=end_date):
        #          list_of_dates.append(dat.strftime("%Y-%m-%d"))

        else:
            return "Invalid interval. Try ('daily', 'weekly' or 'monthly')"

        return list_of_dates

    except Exception as ex:
        return f"The following error occur: {ex}"


##################################################################################
# Enhancement 3: Getting longitudinal, latitudinal and timezone data for a request
##################################################################################
def get_lon_lat_tz(city):
    """
    This use city name to get the longitudinal, latitudinal and timezone data for a request

    Args:
        city (str):  The name of the city

    Return:
        country (str): the country which the city is located
        longitude (float): the logitudinal location of the city on map
        latitute (float): the latitudinal location of the city on map
        timezone (str): corresponding timezone of the city
    """
    try:
        # Initializing Nominatim for logitudinal and latitudinal information
        geolocator = Nominatim(user_agent="MyApp")
        location = geolocator.geocode(city)

        # Getting country, longitude and latitude
        country = location[0].split(",")[-1].lstrip()
        longitude = location.longitude
        latitude = location.latitude

        # Initializing TimezoneFinder for timezone information
        tzobj = TimezoneFinder()
        timezone = tzobj.timezone_at(lng=location.longitude, lat=location.latitude)

        return country, longitude, latitude, timezone

    except Exception as ex:
        return f"The following error occur: {ex}"


if __name__ == "__main__":
    # Create a SQLite3 connection and call the various functions
    # above, printing the results to the terminal.
    ###############################################################
    # Change the CWD to the path where this script is located
    ###############################################################
    PATH_TO_THIS_FILE = os.path.dirname(__file__)
    os.chdir(PATH_TO_THIS_FILE)

    print("CURRENT WORKING DIRECTORY: ", os.getcwd())

