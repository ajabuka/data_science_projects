# Author: <Jesubukade Emmanuel Ajakaye>

# Import neccessary libraries and packages
import os
import requests
import sqlite3

import further_enhancements as fe


def fetch_data_from_meteo_api(city, start_date, end_date):
    """
    This function fetches daily weather data from the open meteo api

    Args:
        None

    Return:
        A list with 3 lists.
        List 0 contains the countries data
        List 1 contains the cities data
        List 2 contains the daily weather data
    """
    # Initialize variable names
    data = []
    country_data = []
    city_data = []
    daily_data = []

    try:
        params = {}

        # Get longitudinal, latitudinal and timezone data
        country, longitude, latitude, timezone = fe.get_lon_lat_tz(city)

        # Get nessecary params
        params["latitude"] = latitude
        params["longitude"] = longitude
            
        params["start_date"] = start_date
        params["end_date"] = end_date

        params["daily"] = "temperature_2m_max,temperature_2m_min,temperature_2m_mean,precipitation_sum,wind_speed_10m_max,shortwave_radiation_sum"
        
        params["timezone"] = timezone

        base_url = "https://archive-api.open-meteo.com/v1/archive"

        response = requests.get(base_url, params=params)
        if response.ok:
            historical_data = response.json()

        # Getting data for the country table
        if country == "United Kingdom":
            country = "Great Britain"
            country_data.append((country, historical_data['timezone']))
        else:
            country_data.append((country, historical_data['timezone']))

        # Getting data for the city table
        city_data.append((city, historical_data['latitude'], historical_data['longitude'], country))

        # Getting data for the daily weather tab;e
        for index in range(len(historical_data['daily']['time'])):
            daily_data.append((
                historical_data['daily']['time'][index],
                historical_data['daily']['temperature_2m_min'][index],
                historical_data['daily']['temperature_2m_max'][index],
                historical_data['daily']['temperature_2m_mean'][index],
                historical_data['daily']['precipitation_sum'][index],
                city,
                historical_data['daily']['wind_speed_10m_max'][index],
                historical_data['daily']['shortwave_radiation_sum'][index],
            ))

        data.append(country_data)
        data.append(city_data)
        data.append(daily_data)

        return data

    except Exception as ex:
        return f"The following error occur: {ex}"

    
def create_database_tables():
    """
    This function creates a new database in the same file path with this script

    Args:
        None

    Return:
        None
    """

    try:
        # Create a connection for the database
        with sqlite3.connect("db/ICA_database.db") as conn:
            cursor = conn.cursor()

            # Deletes table if already exist
            cursor.execute("DROP TABLE IF EXISTS countries;")
            conn.commit()

            cursor.execute("DROP TABLE IF EXISTS cities;")
            conn.commit()

            cursor.execute("DROP TABLE IF EXISTS daily_weather_entries;")
            conn.commit()

            # Creating the Countries Table
            cursor.execute("""CREATE TABLE IF NOT EXISTS "countries" (
                        "id" INTEGER NOT NULL,
                        "name" TEXT UNIQUE NOT NULL,
                        "timezone" TEXT UNIQUE NOT NULL,
                        PRIMARY KEY("id" AUTOINCREMENT)
                        );""")
            conn.commit()

            # Creating the Cities Table
            cursor.execute("""CREATE TABLE IF NOT EXISTS "cities" (
                        "id" INTEGER  NOT NULL,
                        "name" TEXT UNIQUE NOT NULL,
                        "latitude" TEXT UNIQUE NOT NULL,
                        "longitude" TEXT UNIQUE NOT NULL,
                        "country_id" INTEGER NOT NULL,
                        FOREIGN KEY("country_id") REFERENCES "countries"("id") ON DELETE SET NULL,
                        PRIMARY KEY("id" AUTOINCREMENT)
                        );""")
            conn.commit()

            # Creating the Daily Weather Table
            cursor.execute("""CREATE TABLE IF NOT EXISTS "daily_weather_entries" (
                        "id" INTEGER NOT NULL,
                        "date" TEXT UNIQUE NOT NULL,
                        "min_temp" REAL DEFAULT 0.0 NOT NULL,
                        "max_temp" REAL DEFAULT 0.0 NOT NULL,
                        "mean_temp" REAL DEFAULT 0.0 NOT NULL,
                        "precipitation" REAL DEFAULT 0.0 NOT NULL,
                        "city_id" INTEGER NOT NULL,
                        "wind_speed" REAL DEFAULT 0.0 NOT NULL,
                        "shortwave_radiation" REAL DEFAULT 0.0 NOT NULL,
                        PRIMARY KEY("id" AUTOINCREMENT),
                        FOREIGN KEY("city_id") REFERENCES "cities"("id") ON DELETE SET NULL
                        );""")
            conn.commit()

            # Create index for necessary Tables
            cursor.execute("""CREATE INDEX IF NOT EXISTS "cities_name_idx" ON "cities" (
                        "name"	ASC
                        );""")
            conn.commit()

            cursor.execute("""CREATE INDEX IF NOT EXISTS "countries_tz_idx" ON "countries" (
                        "timezone"	ASC
                        );""")
            conn.commit()

            cursor.execute("""CREATE INDEX IF NOT EXISTS "countries_name_idx" ON "countries" (
                        "name"	ASC
                        );""")
            conn.commit()

    except Exception as ex:
        return f"The following error occur: {ex}"


def modify_database_correcting_error(connection):
    """
    This is created specifically to fix some errors found
    on the errors database provide for the ICA.

    Args:
        connection: sqlite3 data base connection to the database

    Return:
        None
    """
    try:
        cursor = connection.cursor()

        # Changing name of column in a table
        cursor.execute("""
                       ALTER TABLE cities
                       RENAME COLUMN longitude TO temp_latitude
                       """)

        connection.commit()

        cursor.execute("""
                       ALTER TABLE cities
                       RENAME COLUMN latitude TO longitude
                       """)

        connection.commit()

        cursor.execute("""
                       ALTER TABLE cities
                       RENAME COLUMN temp_latitude TO latitude
                       """)

        connection.commit()

    except Exception as ex:
        return f"The following error occur: {ex}"


def modify_database_adding_columns(connection):
    """
    This is created specifically to adds new columns to the daily weather table

    Args:
        connection: sqlite3 data base connection to the database

    Return:
        None
    """
    try:
        cursor = connection.cursor()
        
        # Adding the columns to table
        cursor.execute("""
                       ALTER TABLE daily_weather_entries
                       ADD "wind_speed" REAL DEFAULT 0.0 NOT NULL;
                       """)

        connection.commit()

        cursor.execute("""
                       ALTER TABLE daily_weather_entries
                       ADD "shortwave_radiation" REAL DEFAULT 0.0 NOT NULL;
                       """)

        connection.commit()

    except Exception as ex:
        return f"The following error occur: {ex}"


def update_database(connection, data):
    """
    This is created specifically to update the new
    columns created in the database provide for the ICA.
    It also update the timezone of France on the countries table

    Args:
        connection: sqlite3 data base connection to the database
        data (list): list of data fetched from the database

    Return:
        None
    """
    try:
        cursor = connection.cursor()
        
        # Change Value in a particular row
        cursor.execute("""
                       UPDATE countries
                       SET timezone = "Europe/Paris"
                       WHERE name = "France"
                       """)
        
        connection.commit()

        # Adding values to columns
        cursor.executemany("""
                       UPDATE daily_weather_entries
                       SET wind_speed = ?, shortwave_radiation = ?
                       WHERE city_id = (SELECT id FROM cities WHERE name = ?) AND date = ?
                       """, [(d[6], d[7], d[5], d[0]) for d in data[2]])

        connection.commit()

        print("Update Successful")

    except Exception as ex:
        return f"The following error occur: {ex}"


def write_to_database(connection, data):
    """
    This function inserts new daily weather data on
    the weather table if not already in the database provide for the ICA.
    The new data is now till November 2024

    Args:
        connection: sqlite3 data base connection to the database
        data (list): list of data fetched from the database

    Return:
        None
    """
    try:
        cursor = connection.cursor()

        cursor.executemany("""
                           INSERT OR IGNORE INTO "countries" ("name", "timezone")
                           SELECT ?, ? WHERE NOT EXISTS (SELECT name FROM countries WHERE name = ?)
                           """, [(d[0], d[1], d[0]) for d in data[0]])

        connection.commit()
        
        cursor.executemany("""
                           INSERT OR IGNORE INTO "cities"
                           ("name", "latitude", "longitude", "country_id")
                           SELECT ?, ?, ?, ctry.id
                           FROM countries as ctry
                           WHERE ctry.name = ?
                           AND NOT EXISTS (SELECT name, country_id FROM cities WHERE cities.name = ? AND cities.country_id = ctry.id)
                           """, [(d[0], d[1], d[2], d[3], d[0]) for d in data[1]])

        connection.commit()
                
        cursor.executemany("""
                           INSERT OR IGNORE INTO "daily_weather_entries"
                           ("date", "min_temp", "max_temp", "mean_temp", "precipitation", "city_id", wind_speed, shortwave_radiation)
                           SELECT ?, ?, ?, ?, ?, cities.id, ?, ?
                           FROM cities
                           WHERE cities.name = ?
                           AND NOT EXISTS (SELECT date, city_id FROM daily_weather_entries as dwe WHERE dwe.date = ? AND dwe.city_id = cities.id)
                           """, [(d[0], d[1], d[2], d[3], d[4], d[6], d[7], d[5], d[0]) for d in data[2]])

        connection.commit()

        print("Insert Successful")
    
    except Exception as ex:
        return f"The following error occur: {ex}"


def main():
    """
    The fuction connects to the database and calls all the fuction
    output of each function is displayed in plot screen.
    """

    # Connecting to database
    with sqlite3.connect("db/CIS4044-N-SDI-OPENMETEO-PARTIAL.db") as conn:

        conn.commit()

    # Calling all functions in this script
    # Updating ICA Database
    # city = input("Please input the name of City: ") # ["Middlesbrough","London", "Paris", "Toulouse", "Lyon", "Vaduz"]
    # start_date = input("Please input a start date in the follow format YYYY-MM-DD: ") # "2020-01-01"
    # end_date = input("Please in put a end date in the follow format YYYY-MM-DD: ") # "2024-12-31"

    # data = fetch_data_from_meteo_api(city, start_date, end_date)


    # print(data)

    create_database_tables()

    modify_database_correcting_error(conn)

    # modify_database_adding_columns(conn)

    # update_database(conn, data)

    # write_to_database(conn, data)


if __name__ == "__main__":
    ###############################################################
    # Change the CWD to the path where this script is located
    ###############################################################
    PATH_TO_THIS_FILE = os.path.dirname(__file__)
    os.chdir(PATH_TO_THIS_FILE)

    print("CURRENT WORKING DIRECTORY: ", os.getcwd())

    main()