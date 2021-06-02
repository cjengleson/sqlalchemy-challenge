import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, MetaData

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to the table
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
def homepage():
    """List all available api routes"""
    
    return (
        f"Welcome to my API! Here are the available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/[start_date format:yyyy-mm-dd]<br/>"
        f"/api/v1.0/[start format:yyyy-mm-dd]/[end format:yyyy-mm-dd]<br/>")

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results to a dictionary using date as the key and prcp as the value; return the JSON representation of your dictionary"""
    
    session = Session(engine)
    
    year_before = dt.date(2017,8,23) - dt.timedelta(days = 365)
    most_recent = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > year_before).order_by(Measurement.date).all()
    
    precipitation_list = []
    for date, prcp in precipitation:
        dict = {}
        dict["date"] = date
        dict["prcp"] = prcp
        precipitation_list.append(dict)
    return jsonify(precipitation_list)
    
    session.close()

@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)

    """Return a list of station data"""
    active_stations = (session.query(Measurement.station, func.count(Measurement.station)).\
                   group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all())
                   
    return jsonify(active_stations)
    
    session.close()
    
@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)

    """Temperature for most active station in last 12 months of data"""
    active_stations = (session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all())
    most_active = active_stations[0][0]
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= "2016-08-24").\
        filter(Measurement.date <= "2017-08-23").\
        filter(Measurement.station == most_active).all()
    
    return jsonify(results)
    
    session.close()
    
@app.route("/api/v1.0/<start_date>")
def start(start_date):

    session = Session(engine)

    """ When given only start date, return temps greater than or equal to start date"""
    results = session.query(func.avg(Measurement.tobs), func.max(Measurement.tobs), func.min(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
    
    
    session.close()
        
    list = []
    for avg, max, min in results:
        dict = {}
        dict["avg_temp"] = avg
        dict["max_temp"] = max
        dict["min_temp"] = min
        list.append(dict)
        
    return jsonify(list)
    
@app.route("/api/v1.0/<start>/<end>")
def start_stop(start,end):

    session = Session(engine)

    """ When given start and end date, return dates between start and end date inclusively"""
    results = session.query(func.avg(Measurement.tobs), func.max(Measurement.tobs), func.min(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()
        
    list = []
    for avg, max, min in results:
        dict = {}
        dict["avg_temp"] = avg
        dict["max_temp"] = max
        dict["min_temp"] = min
        list.append(dict)
        
    return jsonify(list)
    
if __name__ == '__main__':
    app.run(debug=True)
