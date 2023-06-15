import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, and_

from flask import Flask, jsonify

#Database Setup

engine = create_engine(r"sqlite:///C:\Users\polly\EdxDataAnalytics\ClonedRepos\Challenges\SQLalchemy_Challenge\SurfsUp\Resources\hawaii.sqlite")

#reflect the tables
Base = automap_base()
Base.prepare(autoload_with = engine)

#save reference to the tables
measurement = Base.classes.measurement
Station = Base.classes.station

#Flask Setup
app = Flask(__name__)

#Flask Routes

#_________________________________________
#homepage route
@app.route("/")
def homepage():
    #List all available routes
    return (
        f'Available Routes:<br/>'
        '<br/>'    
        f'View the most recent year of precipitation data:<br/>'          
        f'/api/v1.0/precipitation<br/>'
        '<br/>'
        f'View all station data:<br/>' 
        f'/api/v1.0/stations<br/>'
        '<br/>'
        f'View the most recent year of temperature observations for the most active station:<br/>' 
        f'/api/v1.0/tobs<br/>'
        '<br/>'
        f'View the min/max/avg temperatures from date chosen, date format shown below:<br/>' 
        f'/api/v1.0/yyyy-mm-dd<br/>'
        '<br/>'
        f'View the min/max/avg temperatures between dates chosen, date format shown below:<br/>' 
        f'/api/v1.0/yyyy-mm-dd/yyyy-mm-dd<br/>'
    )

#__________________________________________________________________________________________
#query to determine most recent year and the date one year from that
#to be used for multiple routes

#create session from Python to the DB
session = Session(engine)

#query to find most recent date
recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
#add most recent date to list
recent_date_list = [date for date in recent_date]

#list ready to add date from one year prior to most recent date
one_year = []

#calculate the date one year from most recent date
for date in recent_date_list:
    #format date ready for timedelta calc
    date_format = dt.datetime.strptime(date, '%Y-%m-%d').date()
    #timedelta calc
    recent_year = date_format - dt.timedelta(days=365)
    #add to list
    one_year.append(recent_year)

session.close()

#__________________________________________________________________________________________
#precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    #create session from Python to the DB
    session = Session(engine)

    #query to get all date&prcp data
    #use date from query outside app.route to capture the date 12mths from recent
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= recent_year).all()

    #create list for display
    precip = []
    for date, prcp in results:
        #create and add to dictionary
        rain_dict = {}
        rain_dict[date] = prcp
        #add results to list
        precip.append(rain_dict)

    session.close()

    return jsonify(precip)

#__________________________________________________________________________________________
#stations route
@app.route("/api/v1.0/stations")
def stations():
    #create session from Python to the DB
    session = Session(engine)

    #query to get all station details
    results = session.query(Station.id, Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

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

    session.close()    
    
    return jsonify(station_list)

#__________________________________________________________________________________________
# tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    #create session from Python to the DB
    session = Session(engine)

    #to find most active station count number of results for each station and order desc
    station_count = session.query(measurement.station, func.count(measurement.station)).\
        group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()
    
    most_active_station = station_count[0][0]
    
    #query to retrieve date and temperature for one year from most recent for the most active station
    #use date from query outside app.route to capture the date 12mths from recent 
    results = session.query(measurement.date, measurement.tobs).\
        filter(and_(measurement.date >= recent_year, measurement.station == most_active_station)).all()
    
    #save the query results as a list to return
    #although not required, include the station detail for visibility
    tobs = [{"Station": most_active_station, "Date": result[0], "Temperature": result[1]} for result in results]
    
    session.close()
    
    return jsonify(tobs)

#___________________________________________________________________________________________
# start route
@app.route("/api/v1.0/<start>")
def startdate(start):
    #create session from Python to the DB
    session = Session(engine)    
    
    #convert date given to required datetime format
    startdate = dt.datetime.strptime(start, '%Y-%m-%d').date()

    #functions to return for date range
    functions = [func.min(measurement.tobs),
                 func.avg(measurement.tobs),
                 func.max(measurement.tobs)]
    
    #query on date range to capture above function details
    function_results = session.query(*functions).filter(measurement.date >= startdate).all()

    #query results formatted for viewing
    #although not required start date included as first dictionary item for visibility
    temp_results = [{"1.Start Date": startdate, "Min": temp_results[0], "Avg": temp_results[1], "Max": temp_results[2]} for temp_results in function_results]
    
    session.close()

    return jsonify(temp_results)

#__________________________________________________________________________________________
# start/end route
@app.route("/api/v1.0/<start>/<end>")
def startend(start,end):
    #create session from Python to the DB
    session = Session(engine)
    
    #convert dates given to required datetime format
    firstdate = dt.datetime.strptime(start, '%Y-%m-%d').date()
    lastdate = dt.datetime.strptime(end, '%Y-%m-%d').date()

    #functions to return for date range
    functions = [func.min(measurement.tobs),
                 func.avg(measurement.tobs),
                 func.max(measurement.tobs)]
    
    #query on date range to capture above function details
    function_results = session.query(*functions).filter(and_(measurement.date >= firstdate, measurement.date <= lastdate)).all()

    #query results formatted for viewing
    #although not required start & end date included as first & second dictionary item for visibility
    temp_results = [{"1. Start Date": firstdate, "2. End Date": lastdate,"Min": temp_results[0], "Avg": temp_results[1], "Max": temp_results[2]} for temp_results in function_results]

    session.close()
    
    return jsonify(temp_results)
#__________________________________________________________________________________________ 

if __name__ == "__main__":
    app.run(debug=True)