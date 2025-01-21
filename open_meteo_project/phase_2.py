# Author: <Jesubukade Emmanuel Ajakaye>

# Import neccessary libraries
import os
import matplotlib.pyplot as plt

import phase_1 as ph
import further_enhancements as fe


def plot_map_of_cities(connection):
    """
    This function plots the land map, fills with the location
    of city and the point of the city

    Args:
        connection: sqlite3 data base connection to the database

    Output:
        save and display the producded visual
    """

    # Call function from other scripts
    data = ph.select_all_cities(connection)
    world, cities, point = fe.map_plotting(data)

    try:

        # Plot Cities on their respective location
        fig, ax = plt.subplots(figsize=(12,8))
        world.plot(ax=ax, color="lightgrey")
        cities.plot(ax=ax, alpha = 1, color='red')
        point.plot(ax=ax, color='black')

        # This condition is added because of the error in Longitude and Latitude provide for the ICA
        if point['name'][0] == "Middlesbrough" and point['longitude'][0] > point['latitude'][0]:
            for i in range(len(point["name"])):
                ax.annotate(point["name"].iloc[i], xy=(point['latitude'].iloc[i], point['longitude'].iloc[i]), xytext=(4,4), textcoords='offset points')
        
        else:
            for i in range(len(point["name"])):
                ax.annotate(point["name"].iloc[i], xy=(point['longitude'].iloc[i], point['latitude'].iloc[i]), xytext=(4,4), textcoords='offset points')
        
        ax.set_title('Cities over Filled Continent Background')
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')


        fig.savefig("ICA_Visual_01.png")
        plt.show()

    except Exception as ex:
        return f"The following error occur: {ex}"


def plot_average_annual_temperature(connection):
    """
    This function plots a grouped bar chart of the 
    average temperature of each city in each year

    Args:
        connection: sqlite3 data base connection to the database

    Output:
        save and display the producded visual
    """

    # Call and Iterate over Cities in the database
    cities_id = ph.select_all_cities(connection)["id"]
    cities = ph.select_all_cities(connection)["name"]
    years = ph.get_distinct_year(connection)

    # Declare a empty dictionary to take input
    year_annual_mean = {}

    try:
        # Iterate over the average_annual_temperature(connection, city_id, year) to generate values and update dictionary
        for city_id in cities_id:
            for year in years:
                data = ph.average_annual_temperature(connection, city_id, year)
                if year not in year_annual_mean.keys():
                    year_annual_mean[year] = [float(data["Annual_Mean"][0])]
                else:
                    year_annual_mean[year].append(float(data["Annual_Mean"][0]))

        
        # Bar Plot of Yearly Average by Year for each City
        bar_width = 0.25 # bar width
        spacing = 0.2
        bar_num = len(years)
        x_positions = [i * (bar_width * bar_num + spacing) for i in range(len(cities))]
        fig, ax = plt.subplots(figsize=(20,16))
        for index, year in enumerate(years):
            ax.bar_label(ax.bar([x + index * bar_width for x in x_positions], year_annual_mean[year], bar_width, label=year), padding=3)
        
        # Adding labels to the chart
        ax.set_xticks([x + ((bar_width * bar_num) / 2) for x in x_positions], cities)
        ax.set_xlabel("City")
        ax.set_ylabel("Annual Mean Temperature")
        ax.set_title(f"Annual Mean Temperature by City for {years[0]} - {years[-1]}")
        ax.legend()


        fig.savefig("ICA_Visual_02.png")
        plt.show()

    except Exception as ex:
        return f"There was an error {ex}"


def plot_average_seven_day_precipitation(connection):
    """
    This function plots line charts of the 
    average seven day precipitation of each city in each year

    Args:
        connection: sqlite3 data base connection to the database

    Output:
        save and display the producded visual
    """

    # Declare variables
    # Call and Iterate over Cities in the database
    city_ids = ph.select_all_cities(connection)["id"]
    cities = ph.select_all_cities(connection)["name"]

    start_date = input("Please input a start date in the follow format YYYY-MM-DD: ")
    end_date = input("Please in put a end date in the follow format YYYY-MM-DD: ")

    list_of_dates = fe.get_date_range(start_date, end_date, interval="weekly")

    # Declare a empty dictionary to take input
    weekly_prep_data = {
        "Date" : []
    }

    try:
        # Iterate over the average_annual_temperature(connection, city_id, year) to generate values and update dictionary
        for city_id in city_ids:
            for strt_date in list_of_dates:
                data = ph.average_seven_day_precipitation(connection, city_id, strt_date)
                if data["City"][0] is None:
                    continue

                else:
                    if data["date"][0] not in weekly_prep_data["Date"]:
                        weekly_prep_data["Date"].append(data["date"][0])
                    if data["City"][0] not in weekly_prep_data.keys():
                        weekly_prep_data[data["City"][0]] = [float(data["Prep_Week_Avg"][0])]
                    else:
                        weekly_prep_data[data["City"][0]].append(float(data["Prep_Week_Avg"][0]))


        # Line Plot of Average precipation every 7 days
        fig, ax = plt.subplots(figsize=(12,8))

        for city in cities:
            ax.plot(weekly_prep_data["Date"], weekly_prep_data[city], label=city)

        ax.set_xticks(weekly_prep_data["Date"], weekly_prep_data["Date"], rotation='vertical')
        ax.set_xlabel("Date")
        ax.set_ylabel("Average Precipitation in 7-Days")
        ax.set_title(f"Average 7-days Preciptation from {start_date} to {end_date}")
        ax.legend()

        fig.savefig("ICA_Visual_03.png")
        plt.show()
        

    except Exception as ex:
        return f"The following error occur: {ex}"


def plot_average_mean_temp_by_city(connection):
    """
    This function plots a bar chart of the 
    average mean temperature of each city in each between the day range

    Args:
        connection: sqlite3 data base connection to the database

    Output:
        save and display the producded visual
    """

    # Get input for date from and to
    date_from = input("Please input a start date in the follow format YYYY-MM-DD: ")
    date_to = input("Please in put a end date in the follow format YYYY-MM-DD: ")


    try:
        # Get data from database
        avg_mean_temp = ph.average_mean_temp_by_city(connection, date_from, date_to)

        # Calculate average for axhline
        aggregate_mean = sum(avg_mean_temp["Mean_Temp_Avg"]) / len(avg_mean_temp["Mean_Temp_Avg"])

        # Creating the bar plot
        fig, ax = plt.subplots(figsize=(12,8))

        ax.bar_label(ax.bar(avg_mean_temp["City"], avg_mean_temp["Mean_Temp_Avg"], label = "Mean Temp"), padding=3)

        # Plotting the Mean line
        ax.axhline(y=aggregate_mean, color = 'r', label = f'Aggregate Mean @ {aggregate_mean:.2f}', linestyle = '--', linewidth = 1)
        # ax.text(x=1, y=aggregate_mean, s=f"Aggregate Mean: {aggregate_mean:.2f}", c="k", ha="left")

        ax.set_ylim(0, (max(avg_mean_temp["Mean_Temp_Avg"])+1))
        ax.set_xlabel("City")
        ax.set_ylabel("Average Mean")
        ax.set_title(f"Average Mean Temprature by City {date_from} to {date_to}")
        ax.legend()


        fig.savefig("ICA_Visual_04.png")
        plt.show()

    except Exception as ex:
        return f"The following error occur: {ex}"


def plot_average_annual_precipitation_by_country(connection):
    """
    This function plots a grouded bar chart of the 
    average annual precipitation of countries in each year

    Args:
        connection: sqlite3 data base connection to the database

    Output:
        save and display the producded visual
    """

    # Call and Iterate over Cities in the database
    years = ph.get_distinct_year(connection)
    countries = ph.select_all_countries(connection)['name']

    # Declare a empty dictionary to take input 
    country_annual_avg = {}
    
    max_prep = 0 # Get the heighest to set ylim on chat

    try:
        for year in years:
            data = ph.average_annual_precipitation_by_country(connection, year)
            for num in range(len(data["Country"])):
                if data["Country"][num] not in country_annual_avg.keys():
                    country_annual_avg[data["Country"][num]] = [data["Annual_Prep_Avg"][num]]
                    if data["Annual_Prep_Avg"][num] > max_prep:
                        max_prep = data["Annual_Prep_Avg"][num]
                else:
                    country_annual_avg[data["Country"][num]].append(data["Annual_Prep_Avg"][num])
                    if data["Annual_Prep_Avg"][num] > max_prep:
                        max_prep = data["Annual_Prep_Avg"][num]


        # Bar Plot of Annual Precipitation Average by Country for each Year
        bar_width = 0.25 # bar width
        spacing = 0.2
        bar_num = len(countries)
        x_positions = [i * (bar_width * bar_num + spacing) for i in range(len(years))]

        fig, ax = plt.subplots(figsize=(12,8))
        for index, ctry in enumerate(countries):
            ax.bar_label(ax.bar([x + index * bar_width for x in x_positions], country_annual_avg[ctry], bar_width, label=ctry), padding=3)
        

        ax.set_ylim(0, (max_prep + 0.5))
        ax.set_xticks([x + ((bar_width * bar_num) / 2) for x in x_positions], years)
        ax.set_xlabel("Year")
        ax.set_ylabel("Annual Mean Precipitation")
        ax.set_title(f"Annual Mean Precipitation by Year for {countries}")
        ax.legend()


        fig.savefig("ICA_Visual_05.png")
        plt.show()

    except Exception as ex:
        return f"The following error occur: {ex}"


def plot_city_histogram(connection):
    """
    This function plots a Histogram of the 
    min_temp, max_temp, mean_temp and precipitation
    of selected city and year

    Args:
        connection: sqlite3 data base connection to the database

    Output:
        save and display the producded visual
    """

    city_names = ph.select_all_cities(connection)["name"]
    years = ph.get_distinct_year(connection)
    # city = input(f"Please enter city name from the following list {city_names}: ")
    # year = input(f"Please enter year to plot from the following list {years}: ")

    try:
    
        # Importing data from database
        data = ph.all_database_data(connection)

        city = input(f"Please enter city name from the following list {city_names}: ")
        year = input(f"Please enter year to plot from the following list {years}: ")
        city_found = False

        for country, cities in data.items():
            if city in [ct for ct, years in cities.items()]:
                city_found = True
                if year in [yr for yr in cities[city].keys()]:
                    
                    # Ploting the Histogram
                    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, figsize=(12, 8))
                    axs = [ax1, ax2, ax3, ax4]
                    n = 0
                    while n < len(axs):
                        for key in cities[city][year].keys():
                            axs[n].hist(cities[city][year][key], bins=10)

                            # Adding Average line
                            axs_avg = (sum(cities[city][year][key]) / len(cities[city][year][key]))
                            axs[n].axvline(x=axs_avg, color = 'r', label = 'Average ', linestyle = '--', linewidth = 2)

                            # Adding Labels and Titles
                            axs[n].set_xlabel("Value")
                            axs[n].set_ylabel("Frequency")
                            axs[n].set_title(f"Distribution of {key} in {city} for year {year}")

                            # Adding text to the mean line
                            min_ylim, max_ylim = axs[n].set_ylim()
                            axs[n].text(axs_avg*1.1, max_ylim*0.9, f'Mean: {axs_avg:.2f}')

                            axs[n].grid(True)
                            axs[n].legend()

                            n += 1
                  
                    
                    fig.tight_layout()
                    fig.savefig("ICA_Visual_06.png")
                    plt.show()

                else:
                    print("You've entered an invalid year")

        if not city_found:
            print("The City you entered is not in the database")
    
    except Exception as ex:
        return f"The following error occur: {ex}"


def plot_city_scatter(connection):
    """
    This function plots a scatter plot of the 
    mean_temp and precipitation of selected city and year

    Args:
        connection: sqlite3 data base connection to the database

    Output:
        save and display the producded visual
    """
    # Declare variables
    city_names = ph.select_all_cities(connection)["name"]
    years = ph.get_distinct_year(connection)

    try:
    
        # Collect data from database
        data = ph.all_database_data(connection)

        city = input(f"Please enter city name from the following list {city_names}: ")
        year = input(f"Please enter year to plot from the following list {years}: ")
        city_found = False

        for country, cities in data.items():
            if city in [ct for ct, years in cities.items()]:
                city_found = True
                if year in [yr for yr in cities[city].keys()]:
                    
                    # Ploting the Scatter
                    fig, ax = plt.subplots(figsize=(12, 8))
                    ax.scatter(cities[city][year]["mean_temp"], cities[city][year]["precipitation"], s=100.0, alpha=0.3, edgecolors=None)


                    # Adding Regression line
                    avg_mean_temp = (sum(cities[city][year]["mean_temp"]) / len(cities[city][year]["mean_temp"]))
                    avg_prep = (sum(cities[city][year]["precipitation"]) / len(cities[city][year]["precipitation"]))

                    avg_mean_temp_diff = sum([x - avg_mean_temp for x in cities[city][year]["mean_temp"]])
                    avg_prep_diff = sum([y - avg_prep for y in cities[city][year]["precipitation"]])

                    numerator = avg_mean_temp_diff * avg_prep_diff
                    denominator = (sum([x - avg_mean_temp for x in cities[city][year]["mean_temp"]]) ** 2)

                    slope = numerator / denominator
                    y_intercept = avg_prep - slope * avg_mean_temp

                    regression_line = [slope * x + y_intercept for x in cities[city][year]["mean_temp"]]

                    ax.plot(cities[city][year]["mean_temp"], regression_line, color='r', label=f'Fit Line: y = {y_intercept:.2f} + {slope:.2f}X')


                    # Adding Labels and Titles
                    ax.set_xlabel("Mean Temperature")
                    ax.set_ylabel("Precipitation")
                    ax.set_title(f"Mean Temperature against Preciptation in {city} for year {year}")
                    ax.legend()


                    fig.tight_layout()
                    fig.savefig("ICA_Visual_07.png")
                    plt.show()

                else:
                    print("You've entered an invalid year")

        if not city_found:
            print("The City you entered is not in the database")


    except Exception as ex:
        return f"The following error occur: {ex}"


def plot_city_data_by_year(connection):
    """
    This function plots a line plot of the 
    Min_temo, mean_temp and max_temp of selected city and year

    Args:
        connection: sqlite3 data base connection to the database

    Output:
        save and display the producded visual
    """

    city_names = ph.select_all_cities(connection)["name"]
    years = ph.get_distinct_year(connection)

    try:
    
        data = ph.all_database_data(connection)

        city = input(f"Please enter city name from the following list {city_names}: ")
        year = input(f"Please enter year to plot from the following list {years}: ")
        city_found = False

        for country, cities in data.items():
            if city in [ct for ct, years in cities.items()]:
                city_found = True
                if year in [yr for yr in cities[city].keys()]:
                    
                    # Plotings
                    fig, ax = plt.subplots(figsize=(12, 8))
                    # ax.bar(data["Date"][year], cities[city][year]["precipitation"], label="precipitation")
                    ax.plot(data["Date"][year], cities[city][year]["min_temp"], label="min_temp")
                    ax.plot(data["Date"][year], cities[city][year]["max_temp"], label="max_temp")
                    ax.plot(data["Date"][year], cities[city][year]["mean_temp"], label="mean_temp")


                    # Adding Labels and Titles
                    ax.set_xticks(data["Date"][year], data["Date"][year], rotation='vertical')
                    ax.set_xlabel("Date")
                    ax.set_ylabel("Value")
                    ax.set_title(f"Daily Temperature in {city} for year {year}")
                    ax.legend()


                    fig.tight_layout()
                    fig.savefig("ICA_Visual_08.png")
                    plt.show()

                else:
                    print("You've entered an invalid year")

        if not city_found:
            print("The City you entered is not in the database")


    except Exception as ex:
        return f"The following error occur: {ex}"


def plot_average_seven_day_data(connection):
    """
    This function plots a line chart and bar plot of the 
    min_temp, max_temp, mean_temp and precipitation of selected city and year

    Args:
        connection: sqlite3 data base connection to the database

    Output:
        save and display the producded visual
    """

    # Declare variables
    # Call and Iterate over Cities in the database
    city_ids = ph.select_all_cities(connection)["id"]
    cities = ph.select_all_cities(connection)["name"]

    

    # Declare a empty dictionary to take input
    weekly_data = {
        "date" : [],
        "Min_Temp_Week_Max" : [],
        "Max_Temp_Week_Max" : [],
        "Mean_Temp_Week_Max" : [],
        "Prep_Week_Avg" : []
    }

    # print(weekly_data)

    try:

        # Collect user input
        city = input(f"Please enter city name from the following list {cities}: ")
        start_date = input("Please input a start date in the follow format YYYY-MM-DD: ")
        end_date = input("Please in put a end date in the follow format YYYY-MM-DD: ")

        list_of_dates = fe.get_date_range(start_date, end_date, interval="weekly")

        # Iterate over the average_annual_temperature(connection, city_id, year) to generate values and update dictionary
        city_index = cities.index(city)
        city_id = city_ids[city_index]
        for strt_date in list_of_dates:
            data = ph.average_seven_day_data(connection, city_id, strt_date)
            if data["City"][0] is None:
                continue

            else:
                # weekly_data["City"].extend(data["City"])
                weekly_data["date"].append(strt_date)
                weekly_data["Min_Temp_Week_Max"].append(float(data["Min_Temp_Week_Max"][0]))
                weekly_data["Max_Temp_Week_Max"].append(float(data["Max_Temp_Week_Max"][0]))
                weekly_data["Mean_Temp_Week_Max"].append(float(data["Mean_Temp_Week_Max"][0]))
                weekly_data["Prep_Week_Avg"].append(float(data["Prep_Week_Avg"][0]))

        # Plotings
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.bar(weekly_data["date"], weekly_data["Prep_Week_Avg"], label="Avg Weekly Precipitation")
        ax.plot(weekly_data["date"], weekly_data["Min_Temp_Week_Max"], label="Max Weekly min_temp")
        ax.plot(weekly_data["date"], weekly_data["Max_Temp_Week_Max"], label="Max Weekly max_temp")
        ax.plot(weekly_data["date"], weekly_data["Mean_Temp_Week_Max"], label="Max Weekly mean_temp")


        # Adding Labels and Titles
        ax.set_xticks(weekly_data["date"], weekly_data["date"], rotation='vertical')
        ax.set_xlabel("Date")
        ax.set_ylabel("Value")
        ax.set_title(f"Daily Temperature and Precipitation in {city} from {start_date} to {end_date}")
        ax.legend()

        fig.tight_layout()
        fig.savefig("ICA_Visual_09.png")
        plt.show()
        

    except Exception as ex:
        return f"The following error occur: {ex}"


def main():
    """
    The fuction connects to the database and calls all the fuction
    output of each function is displayed in plot screen.
    """

    # Connect to database
    conn = ph.database_connection("db/CIS4044-N-SDI-OPENMETEO-PARTIAL.db")

    # Calling all functions in this script
    plot_map_of_cities(conn)

    plot_average_annual_temperature(conn)

    plot_average_seven_day_precipitation(conn)

    plot_average_mean_temp_by_city(conn)

    plot_average_annual_precipitation_by_country(conn)

    plot_city_histogram(conn)

    plot_city_scatter(conn)

    plot_city_data_by_year(conn)

    plot_average_seven_day_data(conn)


if __name__ == "__main__":
    ###############################################################
    # Change the CWD to the path where this script is located
    ###############################################################
    PATH_TO_THIS_FILE = os.path.dirname(__file__)
    os.chdir(PATH_TO_THIS_FILE)

    print("CURRENT WORKING DIRECTORY: ", os.getcwd())

    main()