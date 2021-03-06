#!/usr/bin/env python
# Kyle Fitzsimmons, 2018

# run from parent directory
import os
import sys

sys.path[0] = os.path.abspath(os.path.pardir)
os.chdir(os.path.pardir)

# begin
from datetime import datetime
from tripkit import Itinerum

import tripkit_config


itinerum = Itinerum(config=tripkit_config)
itinerum.setup(force=False)
users = itinerum.load_users()

uuids = []
all_trips1, all_trips2 = [], []
parameters = {
    'subway_stations': itinerum.database.load_subway_entrances(),
    'break_interval_seconds': tripkit_config.TRIP_DETECTION_BREAK_INTERVAL_SECONDS,
    'subway_buffer_meters': tripkit_config.TRIP_DETECTION_SUBWAY_BUFFER_METERS,
    'cold_start_distance': tripkit_config.TRIP_DETECTION_COLD_START_DISTANCE_METERS,
    'accuracy_cutoff_meters': tripkit_config.TRIP_DETECTION_ACCURACY_CUTOFF_METERS,
}
for test_user in sorted(users, key=lambda u: str(u.uuid).lower()):
    # updated version of tripbreaker to compare
    v1_algorithm = itinerum.process.trip_detection.triplab.v1.algorithm
    trips1, summaries1 = v1_algorithm.run(test_user.coordinates.dicts(), parameters=parameters)

    # legacy tripbreaker as control
    legacy_metro_stations = []
    for station in parameters['subway_stations']:
        legacy_metro_stations.append({'latitude': station.latitude, 'longitude': station.longitude})

    legacy_coordinates = []
    for c in test_user.coordinates.dicts():
        c['timestamp'] = c.pop('timestamp_UTC')
        legacy_coordinates.append(c)

    trips2, summaries2 = itinerum.process.trip_detection.triplab.legacy.algorithm.run(
        parameters, metro_stations=legacy_metro_stations, points=legacy_coordinates
    )

    # check whether the start and end points for matching trips by id are equal
    for trip_num1, summary1 in summaries1.items():
        starts_match = summary1['start'] == summaries2[trip_num1]['start']
        ends_match = summary1['end'] == summaries2[trip_num1]['end']
        try:
            assert all([starts_match, ends_match])
        except AssertionError as e:
            print(test_user.uuid, '-', trip_num1)
            print(summary1['start'], summaries2[trip_num1]['start'])
            print(summary1['end'], summaries2[trip_num1]['end'])
            raise e

    if trips1:
        all_trips1.extend(list(trips1.values()))
    if trips2:
        all_trips2.extend(list(trips2.values()))
    uuids.append(str(test_user.uuid))
    print(test_user.uuid, len(trips1), len(trips2))

print(len(all_trips1), len(all_trips2))
