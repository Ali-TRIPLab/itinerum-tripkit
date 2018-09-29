#!/usr/bin/env python
# Kyle Fitzsimmons, 2015-2018
import itertools
import math
import utm

from .models import GPSPoint, SubwayEntrance, TripSegment, Trip


## cast input data as objects
def generate_subway_entrances(coordinates):
    '''Find UTM coordinates for subway stations entrances from lat/lon
       and build structs'''
    entrances = []
    for c in coordinates:
        easting, northing, _, _ = utm.from_latlon(c.latitude, c.longitude)
        entrances.append(SubwayEntrance(latitude=c.latitude,
                                        longitude=c.longitude,
                                        northing=northing,
                                        easting=easting))
    return entrances

def generate_gps_points(coordinates):
    '''Find UTM coordinates for user GPS points from lat/lon
       and build structs'''
    for c in coordinates:
        easting, northing, _, _ = utm.from_latlon(c.latitude, c.longitude)
        yield GPSPoint(latitude=c.latitude,
                       longitude=c.longitude,
                       northing=northing,
                       easting=easting,
                       speed=c.speed,
                       h_accuracy=c.h_accuracy,
                       timestamp_UTC=c.timestamp_UTC)


## perform cleaning on points
def filter_by_accuracy(points, cutoff=30):
    '''Remove points that have worse reported accuracy than the
       cutoff value in meters'''
    for p in points:
        if p.h_accuracy <= cutoff:
            yield p


def filter_erroneous_distance(points, check_speed_kph=60):
    '''Remove points with unreasonably fast speeds where, in a series
       of 3 consecutive points (1, 2, and 3), point 3 is closer to point 1
       than point 2'''
    
    # create two copies of the points generator to compare against
    # and advance the copy ahead one point
    points, points_copy = itertools.tee(points)
    next(points_copy)

    last_p = None
    for p in points:
        next_p = next(points_copy)

        # always yield first point without filtering
        if not last_p:
            last_p = p
            yield p

        # find the distance and time passed since previous point was collected
        distance_from_last_point = distance_m(last_p, p)
        seconds_since_last_point = (p.timestamp_UTC - last_p.timestamp_UTC).total_seconds()

        # drop point if both speed and distance conditions are met
        if distance_from_last_point and seconds_since_last_point:
            kph_since_last_point = (distance_from_last_point / seconds_since_last_point) * 3.6
            distance_between_neighbor_points = distance_m(last_p,  next_p)
            
            if (kph_since_last_point >= check_speed_kph and 
                distance_between_neighbor_points < distance_from_last_point):
                    continue

        last_p = p
        yield p

## break gps points into atomic segments
def break_points_by_collection_pause(points, break_period=360):
    '''Break into trip segments when time recorded between points is
       greater than the specified break period'''
    segments = []
    last_p = None
    for p in points:
        # determine break periods and increment segment groups
        if not last_p:
            period = 0
            group = 0
        else:
            period = (p.timestamp_UTC - last_p.timestamp_UTC).total_seconds()
            if period > break_period:
                group += 1
        last_p = p

        # generate segments from determined groups
        p.period_before_seconds = period
        if segments and segments[-1].group == group:
            segments[-1].points.append(p)
        else:
            new_segment = TripSegment(group=group,
                                      period_before_seconds=period,
                                      points=[p])
            segments.append(new_segment)
    return segments


# begin by creating a trip for every segment
def initialize_trips(segments):
    trips = []
    for idx, segment in enumerate(segments):
        trips.append(Trip(num=idx, segments=[segment]))
    return trips


## stitch segments into longer trips if pre-determined conditions are met
def find_subway_connections(trips, subway_entrances, buffer_m=200):
    connected_trips = []
    last_trip = None
    for trip in trips:
        if not last_trip:
            last_trip = trip
            continue

        end_point = last_trip.last_segment.end
        start_point = trip.first_segment.start

        # Test whether the last point of the last segment and the first
        # point of the current segment intersect two different subway
        # station entrances. Uses elif so the same entrance is not caught
        # for both segments (when unrelated stops occur near subway entrances).
        end_intersects, start_intersects = False, False
        end_entrance, start_entrance = None, None
        for entrance in subway_entrances:
            if distance_m(entrance, end_point) <= buffer_m:
                end_intersects = True
                end_entrance = entrance
            elif distance_m(entrance, start_point) <= buffer_m:
                start_intersects = True
                start_entrance = entrance

        if start_intersects and end_intersects:
            interval = start_point.timestamp_UTC - end_point.timestamp_UTC
            subway_distance = distance_m(end_point, start_point)
            subway_speed = subway_distance / interval.total_seconds()
            last_trip.link_to(trip, 'subway')
        else:
            connected_trips.append(trip)
        last_trip = trip

    return connected_trips


def find_velocity_connections(trips):
    connected_trips = []
    last_trip = None
    for trip in trips:
        if not last_trip:
            last_trip = trip

        trip = last_trip


## helper functions
def distance_m(point1, point2):
    '''Returns the distance between two points in meters'''
    a = point2.easting - point1.easting
    b = point2.northing - point2.northing
    return math.sqrt(a**2 + b**2)


## main
def run(coordinates, parameters):
    # process points as structs and cast position from lat/lng to UTM    
    subway_entrances = generate_subway_entrances(parameters['subway_entrances'])
    gps_points = generate_gps_points(coordinates)

    # clean noisy and duplicate points
    high_accuracy_points = filter_by_accuracy(gps_points, cutoff=parameters['accuracy_cutoff_meters'])
    cleaned_points = filter_erroneous_distance(high_accuracy_points, check_speed_kph=60)

    # break trips into atomic trip segments
    segments = break_points_by_collection_pause(cleaned_points, break_period=parameters['break_interval_seconds'])

    # start by considering every segment a trip
    trips = initialize_trips(segments)

    # apply rules to reconstitute full trips from segments when possible ("stitching")
    subway_linked_trips = find_subway_connections(trips, subway_entrances,
                                                  buffer_m=parameters['subway_buffer_meters'])
    velocity_linked_trips = find_velocity_connections(subway_linked_trips)

    return segments

