# Author: <Jesubukade Emmanuel Ajakaye>

# Import neccessary libraries
import sqlite3
import os


# Phase 1 - Starter
# 
# Note: Display all real/float numbers to 2 decimal places.


def database_connection(filename):
    """This function connects to a database

    Args:
        filename: The name of the database and including path if not in same folder

    Return:
        Returns the connection to the database
    """
    try:
        with sqlite3.connect(filename) as connect:

            # Using Column names instead of indexing items 
            connect.row_factory = sqlite3.Row

            connect.commit()

            print("Connection Successful")

        return connect

    except Exception as ex:
        print(f"The following error occur: {ex}")


'''
Satisfactory
'''

def select_all_countries(connection):
    # Queries the database and selects all the countries 
    # stored in the countries table of the database.
    # The results are returned in a dictionary.
    try:

        # Define the query
        query = "SELECT * from [countries]"

        # Get a cursor object from the database connection
        # that will be used to execute database query.
        cursor = connection.cursor()

        # Execute the query via the cursor object.
        results = cursor.execute(query)

        # declare variable names
        col_names = ("id", "name", "timezone")

        # Declare Dictionary
        data = {
            "id": [],
            "name": [],
            "timezone": []
        }

        # Iterate over the results and display the results.
        for row in results:
            # print(f"Country Id: {row['id']} -- Country Name: {row['name']} -- Country Timezone: {row['timezone']}")
            for col_name in col_names:
                data[col_name].append(row[col_name])

        return data

    except sqlite3.OperationalError as ex:
        return ex


def select_all_cities(connection):
    """
    Queries the database and selects all the countries
    stored in the countries table of the database.
    Args:
        connection: sqlite3 data base connection to the database

    Return:
        Returns a dictionary when called
    """

    try:

        # Define the query
        query = "SELECT * from [cities]"

        # Get a cursor object from the database connection
        # that will be used to execute database query.
        cursor = connection.cursor()

        # Execute the query via the cursor object.
        results = cursor.execute(query)

        # declare variable names
        col_names = ("id", "name", "longitude", "latitude")

        data = {
            "id" : [],
            "name" : [],
            "longitude" : [],
            "latitude" : []
        }

        # Iterate over the results and display the results.
        for row in results:
            # print(f"City Id: {row['id']}\t City Name: {row['name']:15}\t City Longitude: {row['longitude']:10}\t City Latitude: {row['latitude']}")
            for col_name in col_names:
                data[col_name].append(row[col_name])

        return (data)

    except sqlite3.OperationalError as ex:
        return ex


'''
Good
'''
def average_annual_temperature(connection, city_id, year):
    """
    Queries the database and selects all the countries
    stored in the countries table of the database.
    Args:
        connection: sqlite3 data base connection to the database
        city_id: id of the city
        year: the year to be queried

    Return:
        Returns a dictionary when called
    """
    try:

        # Define the query
        query = """
            SELECT c.name as City, strftime("%Y", dwe.date) as Year, printf("%.2f", AVG(dwe.mean_temp)) as Annual_Mean
            FROM [daily_weather_entries] as dwe
            JOIN [cities] as c
            ON c.id = dwe.city_id
            WHERE dwe.city_id == ?
            AND strftime("%Y", dwe.date) like ?
        """

        # Get a cursor object from the database connection
        # that will be used to execute database query.
        cursor = connection.cursor()

        # Execute the query via the cursor object.
        results = cursor.execute(query, (city_id, year))

        # declare Column names
        col_names = ("City", "Year", "Annual_Mean")

        data = {
            "City" : [],
            "Year" : [],
            "Annual_Mean" : []
        }

        # Iterate over the results and display the results.
        for row in results:
            # print(f"The average annual temperature at {row['City']} in {row['Year']} = {row['Annual_Mean']}")
            for col_name in col_names:
                data[col_name].append(row[col_name])

        return data
            
    except sqlite3.OperationalError as ex:
        return ex


def average_seven_day_precipitation(connection, city_id, start_date):
    """
    Queries the database and selects all the countries
    stored in the countries table of the database.
    Args:
        connection: sqlite3 data base connection to the database
        city_id: id of the city
        start_date: the date of the day starting the query as YYYY-MM-DD

    Return:
        Returns a dictionary when called
    """
    try:

        # Define the query
        query = """
            SELECT c.name as City, dwe.date, printf("%.2f", AVG(dwe.precipitation)) as Prep_Week_Avg 
            FROM [daily_weather_entries] as dwe
            JOIN [cities] as c
            ON c.id = dwe.city_id
            WHERE dwe.city_id == ?
            AND dwe.date
            BETWEEN ?
            AND date(?, "+7 days", "-1 day")
        """

        # Get a cursor object from the database connection
        # that will be used to execute database query.
        cursor = connection.cursor()

        start_date 
        # Execute the query via the cursor object.
        results = cursor.execute(query, (city_id, start_date, start_date))

        # declare Column names
        col_names = ("City", "date", "Prep_Week_Avg")

        data = {
            "City" : [],
            "date" : [],
            "Prep_Week_Avg" : []
        }
        
        # Iterate over the results and display the results.
        for row in results:
            # print(f"The average seven-day precipitation at {row['name']} starting on {row['date']} = {row['Prep_Week_Avg']}")
            for col_name in col_names:
                data[col_name].append(row[col_name])

        return data
            
    except sqlite3.OperationalError as ex:
        return ex


'''
Very good
'''
def average_mean_temp_by_city(connection, date_from, date_to):
    """
    Queries the database and selects all the countries
    stored in the countries table of the database.
    Args:
        connection: sqlite3 data base connection to the database
        date_from: the date of the day starting the query as YYYY-MM-DD
        date_to: the date of the day ending the query as YYYY-MM-DD

    Return:
        Returns a dictionary when called
    """

    try:

        # Define the query
        query = """
            SELECT c.name as City, printf("%.2f", AVG(dwe.mean_temp)) as Mean_Temp_Avg 
            FROM [daily_weather_entries] as dwe
            JOIN [cities] as c
            ON c.id = dwe.city_id
            WHERE dwe.date
            BETWEEN ?
            AND ?
            GROUP BY c.name
        """

        # Get a cursor object from the database connection
        # that will be used to execute database query.
        cursor = connection.cursor()

        # Execute the query via the cursor object.
        results = cursor.execute(query, (date_from, date_to))

        # Declare dictionary to collect data
        data = {
            "City" : [],
            "Mean_Temp_Avg" : []
        }

        # Iterate over the results and display the results.
        for row in results:
            # print(f"The average mean temperature at {row['City']} from {date_from} to {date_to} = {row['Mean_Temp_Avg']}")
            data["City"].append(row["City"])
            data["Mean_Temp_Avg"].append(float(row["Mean_Temp_Avg"]))

        return data
            
    except sqlite3.OperationalError as ex:
        return ex


def average_annual_precipitation_by_country(connection, year):
    """
    Queries the database and selects all the countries
    stored in the countries table of the database.
    Args:
        connection: sqlite3 data base connection to the database
        year: the year to be queried

    Return:
        Returns a dictionary when called
    """
    try:

        # Define the query
        query = """
            SELECT ctry.name as Country, strftime("%Y", dwe.date) as Year, printf("%.2f", AVG(dwe.precipitation)) as Annual_Prep_Avg
            FROM [daily_weather_entries] as dwe
            JOIN [cities] as city ON city.id = dwe.city_id
            JOIN [countries] as ctry ON ctry.id = city.country_id
            WHERE strftime("%Y", dwe.date) like ?
            GROUP BY ctry.name
        """

        # Get a cursor object from the database connection
        # that will be used to execute database query.
        cursor = connection.cursor()

        # Execute the query via the cursor object.
        results = cursor.execute(query, (year,))

        # Declare dictionary to collect data
        data = {
            "Country" : [],
            "Year": [],
            "Annual_Prep_Avg" : []
        }

        # Iterate over the results and display the results.
        for row in results:
            # print(f"The average annual precipitation at {row['Country']} in {row['Year']} = {row['Annual_Prep_Avg']:.2f}")
            data["Country"].append(row["Country"])
            data["Year"].append(row["Year"])
            data["Annual_Prep_Avg"].append(float(row["Annual_Prep_Avg"]))

        return data
            
    except sqlite3.OperationalError as ex:
        return ex


'''
Excellent

You have gone beyond the basic requirements for this aspect.

'''
##################################
# Extra SQL Query Function
##################################
def get_distinct_year(connection):
    """
    Queries the database and selects all the countries
    stored in the countries table of the database.
    Args:
        connection: sqlite3 data base connection to the database

    Return:
        Returns a list when called
    """
    try:

        # Define the query
        query = """
            SELECT DISTINCT(strftime("%Y", dwe.date)) as Year
            FROM [daily_weather_entries] as dwe
        """

        # Get a cursor object from the database connection
        # that will be used to execute database query.
        cursor = connection.cursor()

        # Execute the query via the cursor object.
        results = cursor.execute(query)

        year = []

        # Iterate over the results and display the results.
        for row in results:
            year.append(row["Year"])

        return year
            
    except sqlite3.OperationalError as ex:
        return ex


def all_database_data(connection):
    """
    Queries the database and selects all the countries
    stored in the countries table of the database.
    Args:
        connection: sqlite3 data base connection to the database

    Return:
        Returns a dictionary when called
    """

    try:

        # Define the query
        query = """
            SELECT ctry.name as Country, ct.name as City, strftime("%Y", dwe.date) as Year, dwe.date as Date, min_temp, max_temp, mean_temp, precipitation
            FROM [daily_weather_entries] as dwe
            JOIN [cities] as ct ON ct.id = dwe.city_id
            JOIN [countries] as ctry ON ctry.id = ct.country_id
        """

        # Get a cursor object from the database connection
        # that will be used to execute database query.
        cursor = connection.cursor()

        # Execute the query via the cursor object.
        results = cursor.execute(query)

        # declare Column names
        col_names = ("Country", "City", "Year", "Date", "min_temp", "max_temp", "mean_temp", "precipitation")

        temp_data = {
            "Country" : [],
            "City" : [],
            "Year" : [],
            "Date" : [],
            "min_temp" : [],
            "max_temp" : [],
            "mean_temp" : [],
            "precipitation" : []
        }

        # Iterate over the results and display the results.
        for row in results:
            for col_name in col_names:
                temp_data[col_name].append(row[col_name])



        # Changing the dimension of my dictionary before return
        data = {}
        for index in range(len(temp_data["Country"])):
            country = temp_data["Country"][index]
            city = temp_data["City"][index]
            year = temp_data["Year"][index]

            if country not in data:
                data[country] = {}

            if city not in data[country]:
                data[country][city] = {}

            if year not in data[country][city]:
                data[country][city][year] = {
                    "min_temp" : [],
                    "max_temp" : [],
                    "mean_temp" : [],
                    "precipitation" : []
                }

            data[country][city][year]["min_temp"].append(float(temp_data["min_temp"][index]))
            data[country][city][year]["max_temp"].append(float(temp_data["max_temp"][index]))
            data[country][city][year]["mean_temp"].append(float(temp_data["mean_temp"][index]))
            data[country][city][year]["precipitation"].append(float(temp_data["precipitation"][index]))

        data["Date"] = {}
        for index in range(len(temp_data["Year"])):
            year = temp_data["Year"][index]
            if year not in data["Date"]:
                data["Date"][year] = []

            if temp_data["Date"][index] not in data["Date"][year]:
                data["Date"][year].append(temp_data["Date"][index])
            else:
                continue
        
        return data
 
    except sqlite3.OperationalError as ex:
        return ex


def average_seven_day_data(connection, city_id, start_date):
    """
    Queries the database and selects all the countries
    stored in the countries table of the database.
    Args:
        connection: sqlite3 data base connection to the database
        city_id: id of the city
        start_date: the date of the day starting the query as YYYY-MM-DD

    Return:
        Returns a dictionary when called
    """
    
    try:

        # Define the query
        query = """
            SELECT c.name as City, dwe.date, printf("%.2f", MAX(dwe.min_temp)) as Min_Temp_Week_Max,
            printf("%.2f", MAX(dwe.max_temp)) as Max_Temp_Week_Max,
            printf("%.2f", MAX(dwe.mean_temp)) as Mean_Temp_Week_Max,
            printf("%.2f", AVG(dwe.precipitation)) as Prep_Week_Avg 
            FROM [daily_weather_entries] as dwe
            JOIN [cities] as c
            ON c.id = dwe.city_id
            WHERE dwe.city_id == ?
            AND dwe.date
            BETWEEN ?
            AND date(?, "+7 days", "-1 day")
        """

        # Get a cursor object from the database connection
        # that will be used to execute database query.
        cursor = connection.cursor()

        start_date 
        # Execute the query via the cursor object.
        results = cursor.execute(query, (city_id, start_date, start_date))
        

        # declare Column names
        col_names = ("City", "date", "Min_Temp_Week_Max", "Max_Temp_Week_Max", "Mean_Temp_Week_Max", "Prep_Week_Avg")

        data = {
            "City" : [],
            "date" : [],
            "Min_Temp_Week_Max" : [],
            "Max_Temp_Week_Max" : [],
            "Mean_Temp_Week_Max" : [],
            "Prep_Week_Avg" : []
        }

        # Iterate over the results and display the results.
        for row in results:
            # print(f"The average seven-day precipitation at {row['City']} starting on {row['date']} = {row['Prep_Week_Avg']}")
            for col_name in col_names:
                data[col_name].append(row[col_name])

        return data
            
    except sqlite3.OperationalError as ex:
        return ex


def get_database_data_for_api(connection, city, start_date, end_date):
    """
    Queries the database for weather data queried from api.
    Args:
        connection: sqlite3 data base connection to the database
        city_name[str]: name of the city
        start_date[str]: the date of the day starting the query as YYYY-MM-DD
        end_date[str]: the date of the day ending the query as YYYY-MM-DD

    Return:
        Returns a dictionary when called
    """
    try:
        # Define the query
        query = """
            SELECT c.name as City, dwe.date, printf("%.2f", dwe.precipitation) as precipitation, printf("%.2f", dwe.min_temp) as min_temp,
            printf("%.2f", dwe.max_temp) as max_temp, printf("%.2f", dwe.mean_temp) as mean_temp
            FROM [daily_weather_entries] as dwe
            JOIN [cities] as c
            ON c.id = dwe.city_id
            WHERE c.name == ?
            AND dwe.date
            BETWEEN ?
            AND ?
        """

        # Get a cursor object from the database connection
        # that will be used to execute database query.
        cursor = connection.cursor()

        start_date 
        # Execute the query via the cursor object.
        results = cursor.execute(query, (city, start_date, end_date))
        

        # declare Column names
        col_names = ("date", "min_temp", "max_temp", "mean_temp", "precipitation")

        data = {
            "City" : [],
            "date" : [],
            "min_temp" : [],
            "max_temp" : [],
            "mean_temp" : [],
            "precipitation" : []
        }

        # Iterate over the results and display the results.
        for row in results:
            # print(f"The average seven-day precipitation at {row['City']} starting on {row['date']} = {row['Prep_Week_Avg']}")
            for col_name in col_names:
                data[col_name].append(row[col_name])
            if row['City'] not in data['City']:
                data['City'].append(row['City'])
            else:
                continue
            

        connection.commit()

        return data

    except sqlite3.OperationalError as ex:
        return ex


def main():
    """
    The fuction connects to the database and calls all the fuction
    output of each function is displayed through the print function.
    """

    connect = database_connection("db/CIS4044-N-SDI-OPENMETEO-PARTIAL.db")
        

    # Calling all functions and Display Output to Users
    print("*****Output a list of years in the database*****")
    year = get_distinct_year(connect)
    print(year)

    
    print("\n")
    print("*****Output of Countries in the Weather Database and their Locations*****")
    countries = select_all_countries(connect)
    for index in range(len(countries["id"])):
        print(f"Country Id: {countries['id'][index]} -- Country Name: {countries['name'][index]} -- Country Timezone: {countries['timezone'][index]}")
        

    print("\n")
    print("*****Output of Cities in the Weather Database and their Locations*****")
    cities = select_all_cities(connect)
    print("Note: I did not convert the Latitude and Longitude to 2 decimal places to ensure the geolocation is not disrupted")
    for index in range(len(cities["id"])):
        print(f"City Id: {cities['id'][index]}\t City Name: {cities['name'][index]:15}\t City Longitude: {cities['longitude'][index]:10}\t City Latitude: {cities['latitude'][index]}")
    
        
    print("\n")
    print("*****Output of Annual Mean Temperature in specific city*****")
    temp_data = average_annual_temperature(connect, 1, 2020)
    for index in range(len(temp_data["City"])):
        print(f"The average annual temperature at {temp_data['City'][index]} in {temp_data['Year'][index]} = {temp_data['Annual_Mean'][index]}")
    
    print("\n")
    print("*****Output of Average Seven Day Precipitation*****")
    prep_data = average_seven_day_precipitation(connect, 1, "2022-01-01")
    for index in range(len(prep_data["City"])):
        print(f"The average seven-day precipitation at {prep_data['City'][index]} starting on {prep_data['date'][index]} = {prep_data['Prep_Week_Avg'][index]}")

    print("\n")
    print("*****Output of Average Mean Temperature by City*****")
    date_from = "2022-01-01"
    date_to = "2022-01-31"
    avg_mean_temp = average_mean_temp_by_city(connect, date_from, date_to)
    for index in range(len(avg_mean_temp["City"])):
        print(f"The average mean temperature at {avg_mean_temp['City'][index]} from {date_from} to {date_to} = {avg_mean_temp['Mean_Temp_Avg'][index]}")

    print("\n")
    print("*****Output of Average Annual Precipitation by Country*****")
    avg_annual_prep = average_annual_precipitation_by_country(connect, 2021)
    for index in range(len(avg_annual_prep["Country"])):
        print(f"The average annual precipitation at {avg_annual_prep['Country'][index]} in {avg_annual_prep['Year'][index]} = {avg_annual_prep['Annual_Prep_Avg'][index]:.2f}")



if __name__ == "__main__":
    # Create a SQLite3 connection and call the various functions
    # above, printing the results to the terminal.
    ###############################################################
    # Change the CWD to the path where this script is located
    ###############################################################
    PATH_TO_THIS_FILE = os.path.dirname(__file__)
    os.chdir(PATH_TO_THIS_FILE)

    print("CURRENT WORKING DIRECTORY: ", os.getcwd())

    main()
