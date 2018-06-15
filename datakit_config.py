#!/usr/bin/env python
# Kyle Fitzsimmons, 2018


# filename for the itinerum-cli database
DATABASE_FN = 'itinerum.sqlite'

# path of raw data directory exported from Itinerum platform
INPUT_DATA_DIR = './input/cuf10-responses-1528306905'

# path of subway station entrances .csv for trip detection
SUBWAY_STATIONS_FP = './input/subway_stations/stm.csv'

# path of export data from itinerum-cli
OUTPUT_DATA_DIR = './output'

# trip detection parameters
TRIP_DETECTION_BREAK_INTERVAL_SECONDS = 360
TRIP_DETECTION_SUBWAY_BUFFER_METERS = 300
TRIP_DETECTION_COLD_START_DISTANCE_METERS = 750
TRIP_DETECTION_ACCURACY_CUTOFF_METERS = 50

# map matcher API URLs (development)
MAP_MATCHING_BIKING_API_URL = 'https://osrmserver.com/osrm/match/v1/biking/'
MAP_MATCHING_DRIVING_API_URL = 'https://osrmserver.com/osrm/match/v1/driving/'
MAP_MATCHING_WALKING_API_URL = 'https://osrmserver.com/osrm/match/v1/walking/'
