# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base
import datetime as dt

################################################
# Database setup
################################################
#create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
#Reflect the existing database into a new model 
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save reference to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Flask setup
app = Flask(__name__)

# Define routes
@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

# Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    most_recent_date = session.query(func.max(measurement.date)).first()[0]
    most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')
    one_year_ago = most_recent_date - dt.timedelta(days=365)

    precipitation_data = session.query(measurement.date, measurement.prcp).filter(
        measurement.date >= one_year_ago
    ).all()

    precipitation_dict = {date: prcp for date, prcp in precipitation_data}

    return jsonify(precipitation_dict)

# stations route
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(station.station).all()
    stations = [result[0] for result in results]

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    most_active_station = session.query(
        measurement.station,
        func.count(measurement.station).label('count')
    ).group_by(measurement.station).order_by(func.count(measurement.station).desc()).first().station

    most_recent_date = session.query(func.max(measurement.date)).first()[0]
    most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')
    one_year_ago = most_recent_date - dt.timedelta(days=365)

    temperature_data = session.query(measurement.date, measurement.tobs).filter(
        measurement.station == most_active_station,
        measurement.date >= one_year_ago
    ).all()

    temperature_list = [{date: tobs} for date, tobs in temperature_data]

    return jsonify(temperature_list)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_range(start, end=None):
    if end:
        results = session.query(
            func.min(measurement.tobs),
            func.avg(measurement.tobs),
            func.max(measurement.tobs)
        ).filter(measurement.date >= start).filter(measurement.date <= end).all()
    else:
        results = session.query(
            func.min(measurement.tobs),
            func.avg(measurement.tobs),
            func.max(measurement.tobs)
        ).filter(measurement.date >= start).all()

    temps = list(results[0])
    return jsonify(temps)

################################################
# Flask Routes
################################################

if __name__ == "__main__":
    app.run(debug=True)