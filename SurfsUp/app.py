#Import dependencies
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

# Create engine to database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the database
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

#Define homepage route
@app.route("/")
def index():
    return (
        f"Welcome to the climate analysis of Hawaii<br/><br/>"
        f"All Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
        f"'start' and 'end' date should be in the YYYY-MM-DD format.</p>"
    )

#####################
# Precipitation Route
#####################

#Define precipitation route, display date and precipitation of the last 12 months of data
@app.route("/api/v1.0/precipitation")
def precipitation():
    #First get the last 12 months
    most_recent = dt.datetime(2017, 8, 23)
    one_year_before = most_recent - dt.timedelta(days=365)

    #Get precipitation data for last 12 months
    precipitation = session.query(measurement.date, measurement.prcp).\
                    filter(measurement.date >= one_year_before).all()
    
    #Create dictionary with date as the key and prcp as the value
    prcp = {}
    for date, value in precipitation:
        prcp[date] = value

    #Close session
    session.close()


    # Return the JSON representation of the precipitation data
    return jsonify(prcp)

################
# Stations Route
################



@app.route("/api/v1.0/stations")
def stations():
    #Get stations
    all_stations = session.query(station.station).all()
    

    #Convert all_stations query reults to list using numpy
    station_list = list(np.ravel(all_stations))

    #Close session
    session.close()
    
    #Return JSON representation
    return jsonify(station_list)

###################
# Temperature Route
###################
    
@app.route("/api/v1.0/tobs")
def tobs():
    #First get the initial date to look at
    most_recent = dt.datetime(2017, 8, 23)
    one_year_before = most_recent - dt.timedelta(days=365)

    #Find the active stations
    active_stations = session.query(measurement.station, func.count(measurement.station)).\
        group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()
    
    #Get the most active station
    most_active = active_stations[0][0]

    #Get dates and temperature observations for the most-active station during last 12 months
    most_active_12_months = session.query(measurement.date, measurement.tobs).filter(measurement.date >= one_year_before, measurement.station == most_active).all()
    

    #Convert most_active_12_months query reults to list using numpy
    most_active_list = list(np.ravel(most_active_12_months))

    #Close session
    session.close()
    
    #Return JSON representation
    return jsonify(most_active_list)

###############################
# Temperature for Start and End
###############################

# Create routes where you either input a specific start date or start and end date 
# Input date as YYYY-MM-DD
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")

def temperature_final(start=None, end=None):
    # Use a select statement which will query min, max and avg temp
    select = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]

    # Use an if-not statement to get 1 of 2 options: 1) a date range with a specific start date which will calculate a date range from the start-date to the latest date in the dataset
    # 2) get a specific date range after inputting a start and end-date
    if end is None:
        outputs = session.query(*select).filter(measurement.date >= start).all()
        start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    else:
        outputs = session.query(*select).filter(measurement.date >= start, measurement.date <= end).all()

    # Use np.ravel function to convert tuples to a regular flattened one-dimensional list 
    temp_final = list(np.ravel(outputs))

    session.close()  # Close the session

    return jsonify(temp_final=temp_final)

if __name__ == "__main__":
    app.run(debug=True)