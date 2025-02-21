""" Test for the intersector code """

import numpy as np
from numpy import datetime64 as dt64
import pandas as pd
import datetime
import time

EARTH_RADIUS = 6371.0  # kilometers

def load_ais(datapath: str):
    """ Returns a dict mapping years (int) to dataframes that have dtype
            mmsi_id               int64
            date_time    datetime64[ns]
            lat                 float32
            lon                 float32
    
    The dataframes are sorted by mmsi_id, and within each id, are sorted
    ascending by time.
    """
    pass


def make_test_data_1():
    """ This creates a satellite track that consists of two points, and
    a vessel track of four positions that cross the satellite track.
    """

    # The satellite is at 200km altitude, which implies a FOV circle
    # with radius ~1576 km, which is 14.1 deg when viewed from the 
    # center of the earth.
    sat_alt = 200 + EARTH_RADIUS
    #
    # For this test, we pick Latitude=40 deg North.
    # We also create contrived time points, for ease of debugging,
    # going from t=100 to t=200.
    sat = np.array([[100, 40, -150, sat_alt],
                    [200, 40, -110, sat_alt]], dtype=np.float64)
    satdf = pd.DataFrame(sat, columns=["date_time", "lat", "long", "alt"])

    # The first and last vessel point fall outside the satellite visibility,
    # and the middle two points fall inside.
    ship = np.array([[110.0, 1234, 10.0, -145.0],
                     [130.0, 1234, 35.0, -137.0],
                     [150.0, 1234, 45.0, -124.0],
                     [170.0, 1234, 70.0, -115.0]])
    shipdf = pd.DataFrame(ship, columns=["date_time", "MMSI", "lat", "long"])
    return satdf, shipdf


def make_ship_track(start: tuple, end: tuple, N:int=None, dt:int=None, 
        ds:float=None, velocity:int=20):
    """ Creates a geodesic ship track from **start** to **end**
    
    start, end: tuples of (time, lat, long) where time is in integer 
                seconds since UNIX epoch
        
    Only one of the following parameters can be provided:
        N: Number of points
        dt: Time interval in seconds
        ds: Distance in km

    velocity: float
        The speed of the ship.
    """


def test1():
    sat, ships = make_test_data_1()
    from intersect import compute_hits
    import intersect
    intersect.PRINT_INFO = True
    hits = compute_hits(sat, ships, workers=1)
    print(hits)

def create_dummy_sat_track():
    from skyfield.sgp4lib import EarthSatellite
    from skyfield.framelib import itrs
    from skyfield import api
    ts = api.load.timescale()

    tle1 = "1 07195U 73086FD  09365.98624744  .00000168  00000-0  31070-3 0  3918\\"
    tle2 = "2 07195 103.2086 165.3351 0336236 191.7936 167.5149 13.40434914746112"

    sat = EarthSatellite(tle1, tle2)
    jds = ts.tt_jd(np.linspace(sat.epoch.tt - 0.5, sat.epoch.tt +0.5, 24*60))
    np_times = pd.Series(jds.utc_datetime()).to_numpy(np.datetime64)
    
    lats, longs, dists = sat.at(jds).frame_latlon(itrs)
    return pd.DataFrame({"date_time": np_times, "lat": lats.degrees, 
        "lon": longs.degrees, "alt": dists.km})

df = create_dummy_sat_track()

def create_dummy_data(numsatpoints = 4000, numaispoints=1_000_000):
    # Create a simple West-East satellite track
    sat_time = np.linspace(dt64("2014-01-11T18:00:00").astype(int), 
                           dt64("2014-01-14T12:00:00").astype(int), numsatpoints)
    sat_lat = 30.0 + np.zeros(len(sat_time))
    sat_lon = np.linspace(-150.0, -100.0, numsatpoints)
    sat_alt = np.zeros(len(sat_time)) + EARTH_RADIUS + 200

    sat_track = pd.DataFrame({"date_time": sat_time, "lat": sat_lat,
        "lon": sat_lon, "alt": sat_alt})

    vessel_df = pd.DataFrame({
            "date_time": np.linspace(dt64("2014-01-12T00:00:00").astype(int),
                                     dt64("2014-01-13T11:59:00").astype(int), numaispoints),
            "mmsi_id": np.zeros(numaispoints,dtype=np.int64) + 3456,
            "lat": np.linspace(15.0, 50.0, numaispoints),
            "lon": np.linspace(-130.0, -120.0, numaispoints) })

    return sat_track, vessel_df

def check_values(sat, hits):
    # For each value in hits, look up the satellite time and location,
    # and manually do a calculation to compute FOV.
    pass

def orig_test():
    import intersect
    from intersect import compute_hits
    intersect.PRINT_INFO = True

    num_sat = 4000
    num_ais = 10_000_000

    print(f"Satellite track pts: {num_sat:,}; \tAIS points: {num_ais:,}")
    sat, vessels = create_dummy_data(num_sat, num_ais)
    start = time.time()
    hits = compute_hits(sat, vessels, start_time="2014-01-12T01:00:00", end_time="2014-01-12T09:00:00")
    delta = time.time() - start
    #print(hits)
    print(f"Found {len(hits)} hits.")
    print("Total Wall Clock Time:", delta)
    

if __name__ == "__main__":
    orig_test()
    #test1()



