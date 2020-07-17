from flask import Flask, jsonify

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

import datetime as dt

import numpy as np

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station


app = Flask(__name__)

@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route('/api/v1.0/precipitation')
def precip():
    
    session = Session(engine)

    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    most_recent_date = dt.datetime.strptime(most_recent_date[0], '%Y-%m-%d').date()
    one_year_ago = most_recent_date - dt.timedelta(days=365)
    one_year_prcp = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).filter(Measurement.date <=most_recent_date).all()

    session.close()

    precip_dict = {date: precip for (date, precip) in one_year_prcp}
    
    return jsonify(precip_dict)

@app.route('/api/v1.0/stations')
def stations():

    session = Session(engine)
    all_stations = session.query(Station.station).all()

    session.close()

    return jsonify(all_stations)

@app.route('/api/v1.0/tobs')
def tobs():

    session = Session(engine)

    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    most_recent_date = dt.datetime.strptime(most_recent_date[0], '%Y-%m-%d').date()
    one_year_ago = most_recent_date - dt.timedelta(days=365)

    most_active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()


    one_year_temp_most_active = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station==most_active_stations[0][0])\
    .filter(Measurement.date >= one_year_ago).filter(Measurement.date <=most_recent_date).all()

    session.close()

    return jsonify(one_year_temp_most_active)

@app.route('/api/v1.0/<start>')
def data_from_start_date(start):

    session = Session(engine)

    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
    .filter(func.strftime("%Y-%m-%d", Measurement.date) >= start).all()

    temp_dict = {}
    for min, avg, max in temp_data:
        temp_dict['Minimum Temperature'] = round(min,2)
        temp_dict['Average Temperature'] = round(avg,2)
        temp_dict['Maximum Temperature'] = round(max,2)

    return jsonify(temp_dict)

@app.route('/api/v1.0/<start>/<end>')
def data_from_range(start, end):

    session = Session(engine)

    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
    .filter(func.strftime("%Y-%m-%d", Measurement.date) >= start).filter(func.strftime("%Y-%m-%d", Measurement.date) <=end).all()

    temp_dict = {}
    for min, avg, max in temp_data:
        temp_dict['Minimum Temperature'] = round(min,2)
        temp_dict['Average Temperature'] = round(avg,2)
        temp_dict['Maximum Temperature'] = round(max,2)

    return jsonify(temp_dict)

if __name__ == "__main__":
    app.run(debug=True)