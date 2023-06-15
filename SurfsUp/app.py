import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, all_

from flask import Flask, jsonify

#_______________________________________________________________________
#Database Setup

engine = create_engine(r"sqlite:///C:\Users\polly\EdxDataAnalytics\ClonedRepos\Challenges\SQLalchemy_Challenge\SurfsUp\Resources\hawaii.sqlite")

#reflect the tables
Base = automap_base()
Base.prepare(autoload_with = engine)

#save reference to the tables
measurement = Base.classes.measurement
Station = Base.classes.station

#_________________________________________________________________________
#Flask Setup
app = Flask(__name__)

#_________________________________________________________________________
#Flask Routes

#homepage route
@app.route("/")
def homepage():
    #List all available routes
    return (
        f'Available Routes:<br/>'      
        f'/api/v1.0/precipitation<br/>'
        f'/api/v1.0/stations<br/>'
        f'/api/v1.0/tobs<br/>'
    )

#precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    #create session from Python to the DB
    session = Session(engine)
    #query to get all date.prcp data
    results = session.query(measurement.date, measurement.prcp).all()
    session.close()

    #create list for display
    precip = []
    for date, prcp in results:
        #create and add to dictionary
        rain_dict = {}
        rain_dict[date] = prcp
        #add results to list
        precip.append(rain_dict)
    
    return jsonify(precip)

#stations route
@app.route("/api/v1.0/stations")
def stations():
    #create session from Python to the DB
    session = Session(engine)
    #query to get all station details
    results = session.query(Station.id, Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()
    session.close()

    #create list for display
    station_list = []
    for id, station, name, latitude, longitude, elevation in results:
        #create and add to dictionary
        station_dict = {} 
        station_dict[f"{id} Station"] = station #use ID to keep station at top of dictionary
        station_dict["Name"] = name
        station_dict["Lat"] = latitude
        station_dict["Long"] = longitude
        station_dict["Elevation"] = elevation
        #add results to the list
        station_list.append(station_dict)
    
    return jsonify(station_list)
    
if __name__ == "__main__":
    app.run(debug=True)