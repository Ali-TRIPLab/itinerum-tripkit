#!/usr/bin/env python
# Kyle Fitzsimmons, 2018
import csv
import ciso8601
import logging
import os
import pytz
import time

# config
source_dir_name = 'mobilité-responses-2017'
output_dir = os.path.join('./cleaned', source_dir_name)

# init--create the new output dir and setup logging
if not os.path.exists(output_dir):
    os.mkdir(output_dir)
logging.basicConfig(level=logging.INFO)


def csv_rows_to_UTC(filename, dt_columns, expected_columns):
    '''
    Changes a localized datetime to its UTC equivalent and inserts blank
    columns for expected fields when necessary.
    '''
    source_csv_fn = os.path.join('./uncleaned', source_dir_name, filename)
    normalized = []
    normalized_headers = []
    with open(source_csv_fn, 'r', encoding='utf-8-sig') as csv_f:
        reader = csv.DictReader(csv_f)
        headers = reader.fieldnames
        
        # rename any datetime columns to `datetime_UTC`
        for h in headers:
            if h in dt_columns:
                normalized_headers.append(h + '_UTC')
            else:
                normalized_headers.append(h)

        # load datetime from string, convert to UTC format and replace as row entry
        for row in reader:
            for col in dt_columns:
                local_dt = row.pop(col)
                col_utc = col + '_UTC'
                row[col_utc] = ciso8601.parse_datetime(local_dt).astimezone(pytz.utc)
            normalized.append(row)

    # write new output .csv
    dest_csv_fn = os.path.join('./cleaned', source_dir_name, filename)
    with open(dest_csv_fn, 'w') as csv_f:
        writer = csv.DictWriter(csv_f, fieldnames=normalized_headers)
        writer.writeheader()
        writer.writerows(normalized)


if __name__ == '__main__':
    start = time.time()
    logging.info('Updating records to UTC for: {dir}/{fn}'.format(dir=source_dir_name,
                                                                  fn='survey_responses.csv'))
    csv_rows_to_UTC('survey_responses.csv', ['created_at'])


    logging.info('Updating records to UTC for: {dir}/{fn}'.format(dir=source_dir_name,
                                                                  fn='prompt_responses.csv'))
    csv_rows_to_UTC('prompt_responses.csv', ['displayed_at', 'recorded_at'])


    logging.info('Updating records to UTC for: {dir}/{fn}'.format(dir=source_dir_name,
                                                                  fn='coordinates.csv'))
    csv_rows_to_UTC('coordinates.csv', ['timestamp'])

    end = time.time()
    logging.info('Processing finished in {%.3f} seconds.'.format(end - start))