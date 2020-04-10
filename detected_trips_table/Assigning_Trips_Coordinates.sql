--TRIP Lab- March 2020
--Ali Yazdizadeh

--This file creates ''detected_trips_coordinates' table based on the ''detected_trips'' table
--It assigns all the GPS points along a trip a unique trip_id (i.e. 'detected_trip_id')
--It also generates a geometry for each GPS point
--At the end some indexes are generated based on the new ''detected_trips_coordinates'' table
DROP TABLE if EXISTS loop_trips;
CREATE TABLE loop_trips (id integer,
survey_id integer,
mobile_id integer,
latitude numeric,
longitude numeric,
altitude numeric,
speed numeric,
direction numeric,
h_accuracy double precision,
v_accuracy double precision,
acceleration_x numeric,
acceleration_y numeric,
acceleration_z numeric,
mode_detected integer,
timestamp timestamp with time zone,
point_type integer,
detected_trip_id INTEGER,
start_id INTEGER,
end_id INTEGER,
distancs real,
duration real,
start_timestamp timestamp with time zone,
end_timestamp timestamp with time zone,
trip_code integer,
geom geometry
);


CREATE OR REPLACE FUNCTION assign_trips_to_coordinates() returns setof loop_trips as
$$
--declaring the variable for looping through rows of a table
DECLARE
   r detected_trips%rowtype;
	 iterator float4 := 1;
   --t sample_prompt%rowtype;
--begining the definition of function
BEGIN
	FOR r IN SELECT * FROM detected_trips WHERE trip_code < 100
	LOOP
		--for t in select * from detected_trips
		RETURN QUERY
			SELECT
				a.*, r.id as detected_trips_id, r.start_id as start_id, r.end_id as end_id, r.distance as distance, r.duration as duration,
				r.start_timestamp as start_timestamp, r.end_timestamp as end_timestamp, r.trip_code as trip_code,
			  ST_Transform(ST_SetSRID(ST_MakePoint(a.longitude, a.latitude), 4326), 32618) as geom
			from (
				select
					*
				from
					mobile_coordinates b
				where
					b.mobile_id = r.mobile_id AND b.timestamp <= r.end_timestamp AND b.timestamp >= r.start_timestamp AND NOT (b.id = ANY (r.excluded_points))
				order by
					b.timestamp
				) a;

end loop;

--end of the definition of the function
END
--definition of the language used by postgis
$$LANGUAGE plpgsql;
--this query should be execute to return the content of the table related to the aboved defined function(It may takes more than one hour to execute)

--drop table if exists detected_trips_coordinates;
DROP TABLE IF EXISTS detected_trips_coordinates;
with s as(
select * from assign_trips_to_coordinates()
)
select *
into detected_trips_coordinates
from s;
------------
------------
--add primary key for the above table
ALTER TABLE detected_trips_coordinates ADD PRIMARY KEY (id,detected_trip_id);
CREATE UNIQUE INDEX detected_trips_coordinates_start_timestamp_key ON detected_trips_coordinates (mobile_id ASC, timestamp ASC);

CREATE INDEX detected_trips_coordinates_id_idx ON detected_trips_coordinates (id ASC);
CREATE INDEX detected_trips_coordinates_survey_timestamp_idx ON detected_trips_coordinates (survey_id ASC, timestamp ASC);
CREATE INDEX detected_trips_coordinates_mobile_timesetamp_idx ON detected_trips_coordinates (mobile_id ASC, timestamp ASC);
CREATE INDEX detected_trips_coordinates_id_mobile_id_idx ON  detected_trips_coordinates (mobile_id ASC, id ASC );