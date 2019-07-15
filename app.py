import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt
from dateutil.relativedelta import relativedelta

#################################################
# Database Setup
#################################################
# Reference - https://docs.python.org/3/library/sqlite3.html
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False}, echo=True)

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return"""
    <html>
    <h1>Surf's Up! Hawaii Climate API.</h1>
    <br><br>
    Precipitation:
    <br>
    <a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a>
    <br><br>
    All Stations: 
    <br>
    <a href="/api/v1.0/stations">/api/v1.0/stations</a>
    <br><br>
    Temperature Observations (tobs):
    <br>
    <a href="/api/v1.0/tobs">/api/v1.0/tobs</a>
    <br><br>
    TMIN, TAVG, and TMAX for 02/10/2017 - 02/23/17:
    <br>
    <a href="/api/v1.0/2017-02-10">/api/v1.0/2017-02-10</a>
    <br><br>
    TMIN, TAVG, and TMAX for 2/10/17 to 2/17/17:
    <br>
    <a href="/api/v1.0/2017-02-10/2017-02-17">/api/v1.0/2017-02-10/2017-02-17</a>
    </html>
    """


@app.route("/api/v1.0/precipitation")
def precipitation():

    # Convert the query results to a Dictionary using date as the key and prcp as the value.
    # Calculate the date 1 year ago from the last data point in the database
    #Reference for relativedelta
    #https://stackoverflow.com/questions/546321/how-do-i-calculate-the-date-six-months-from-the-current-date-using-the-datetime
    year_ago = dt.date(2017,8,23) - relativedelta(years=1)

    #Get last 12 months of precipitation data
    query = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).all()

    # Convert into list
    prcp = dict(query)

    #Return the JSON representation of the dictionary
    return jsonify(prcp)

@app.route("/api/v1.0/stations")
def stations(): 

    # Return a JSON list of stations from the dataset
    all_stations = session.query(Station.station, Station.name).all()
 
    # Convert into list
    stations_list = list(all_stations)

    # Return JSON list
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs(): 

    #Reference for relativedelta
    #https://stackoverflow.com/questions/546321/how-do-i-calculate-the-date-six-months-from-the-current-date-using-the-datetime
    year_ago = dt.date(2017,8,23) - relativedelta(years=1)

    #Query for the dates and temperature observations from a year from the last data point.
    tobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_ago).order_by(Measurement.date).all()

    # Convert into list
    tobs_list = list(tobs)

    # Return a JSON list of Temperature Observations (tobs) for the previous year.
    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")
def start_date(start):

    # When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    start_date = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()
    
    # Convert into list
    start_date_list=list(start_date)

    # Return a JSON list    
    return jsonify(start_date_list)
    

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
 
    # When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
    start_end = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()
    
    # Convert into list
    start_end_list = list(start_end)

    # Return a JSON list
    return jsonify(start_end_list)

if __name__ == '__main__':
    app.run(debug=True)