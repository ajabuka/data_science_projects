# Author: <Jesubukade Emmanuel Ajakaye>

# Import need libraries
import os

from typing import Optional
from datetime import date, datetime
import uvicorn
from fastapi import FastAPI, Query
from pydantic import BaseModel, Field


import phase_1 as ph1
import phase_3 as ph3


#####################################################################################
# Using FastApi Interactive App for request and upload in ICA database
#####################################################################################
app = FastAPI(
    title="API to Query and Update ICA Database",
    description="The GET generate min_temp, max_temp, mean_temp and precipitation, while PUT get data from open meteo and updates ICA database",
    version="ICA 0.0.1",
    contact={
        "name": "Jesubukade Ajakaye",
        "email": "ajakaye.bukade@gmail.com"
    }
)

class Item(BaseModel): # declaring data types of variables in the app with examples
    city: str = Field(examples=["Middlesbrough"])
    start_date: date
    end_date: date


@app.get("/")
def read_root():
    return {"error": "No parameter entered"}


@app.get("/get-ICA-weather-data")
def read_item(city: Optional[str] = Query(description ="Please input the name of City:"),
              start_date: Optional[date] = Query(description="Please input the starting the query as YYYY-MM-DD:"),
              end_date: Optional[date] = Query(description="Please input the ending the query as YYYY-MM-DD:")):
    """
    This queries the ICA database and get min_temp, max_temp, mean_temp and precipitation

    - **city**:  The name of the city
    - **start_date**:  the date of the day starting the query as YYYY-MM-DD
    - **end_date**:  the date of the day ending the query as YYYY-MM-DD
    """
    try:
        connection = ph1.database_connection("db/CIS4044-N-SDI-OPENMETEO-PARTIAL.db") # Connect to database

        data = ph1.get_database_data_for_api(connection, city, start_date, end_date) # Querying ICA Database

        return data
    
    except Exception as ex:
        return f"The following error occur: {ex}"


@app.put("/update-from-meteo")
def update_item(item:Item, city: Optional[str] = Query(description ="Please input the name of City:"),
              start_date: Optional[date] = Query(description="Please input the starting the query as YYYY-MM-DD:"),
              end_date: Optional[date] = Query(description="Please input the ending the query as YYYY-MM-DD:")):
    """
    This queries the Open meteo database updates the ICA Database

    - **city**:  The name of the city
    - **start_date**:  the date of the day starting the query as YYYY-MM-DD
    - **end_date**:  the date of the day ending the query as YYYY-MM-DD
    """
    try:
        connection = ph1.database_connection("db/CIS4044-N-SDI-OPENMETEO-PARTIAL.db") # Connecting to database

        start_time = datetime.now() # Saving time process started

        data = ph3.fetch_data_from_meteo_api(city, start_date, end_date) # Fetching data from Open Meteo

        ph3.modify_database_adding_columns(connection) # Check is needed to add columns

        ph3.update_database(connection, data) # Update data to added columns for existing data

        ph3.write_to_database(connection, data) # Inserts fresh data if doesn't exist in database

        end_time = datetime.now() # Saving time process ended

        process_time = end_time - start_time # Calculating time taken for process to be completed
        
        return f"Action Successful in {process_time}"
    
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
    
    uvicorn.run(app, host='127.0.0.1', port=8000)
