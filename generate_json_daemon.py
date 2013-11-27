#!/usr/bin/env python
import argparse
from bs4 import BeautifulSoup
import calendar
from collections import namedtuple
from contextlib import contextmanager
from datetime import datetime, timedelta
import json
import pytz
import requests
import sys
import time


# how many recently played songs we want to keep track of
ENTRY_BUFFER_SIZE = 50
LAST_PLAYED_URL = 'http://nol888.com/~nlum/caa-radio.php'
TIME_ZONES = {'PST': pytz.timezone('America/Los_Angeles'),
              'PDT': pytz.timezone('America/Los_Angeles')}
RadioEntry = namedtuple('RadioEntry', ['timestamp', 'artist', 'title'])


def get_radio_entries(url):
    entries = list()
    r = requests.get(url)

    if r.status_code != 200:
        sys.stderr.write(("Got HTTP status code {0}"
            "while fetching page {1}").format(r.status_code, LAST_PLAYED_URL))
        time.sleep(60)
        return entries

    doc = BeautifulSoup(r.text)
    table = doc.find('table')
    rows = table.tbody.find_all('tr', recursive=False)

    num_processed = 0
    for row in rows:
        cells = row.find_all('td', recursive=False)

        date_cell = cells[0]
        song_cell = cells[1]

        tz_abbrevation = date_cell.text.rsplit(' ', 1)[1]

        # strptime throws away the timezone information from %Z
        timestamp = datetime.strptime(date_cell.text,
                                      "%B %d, %Y %I:%M:%S%p %Z")

        timezone = TIME_ZONES[tz_abbrevation]
        if tz_abbrevation in TIME_ZONES:
            timezone = TIME_ZONES[tz_abbrevation]
            timestamp = timezone.localize(timestamp)

        if ' - ' in song_cell.text:
            (artist, title) = song_cell.text.split(' - ', 1)
        else:
            artist = None
            title = song_cell.text

        entries.append(RadioEntry(timestamp, artist, title))
        num_processed += 1
        if num_processed >= ENTRY_BUFFER_SIZE:
            break
    return entries


@contextmanager
def open_file_or_stream(filename, stream):
    if filename:
        f = open(filename, 'w')
        try:
            yield f
        finally:
            f.close()
    else:
        yield sys.stdout


if __name__ == '__main__':
    description = "Save the latest songs played on CAA radio to json"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('destination', nargs='?', default=None,
        help="Destination filename or, if left blank, stdout")
    args = parser.parse_args()

    previous_latest_entry = None
    while True:
        entries = get_radio_entries(LAST_PLAYED_URL)

        now = pytz.utc.localize(datetime.utcnow())
        latest_entry = entries[0]
        if latest_entry == previous_latest_entry:
            # once the entries haven't been updated for this threshold,
            # sleep for significantly longer periods of time
            unused_threshold = timedelta(minutes=10)

            if now > (latest_entry.timestamp + unused_threshold):
                print "The radio list hasn't been updated for", unused_threshold, "so sleep longer"
                print "Sleeping for 10 minutes"
                print
                time.sleep(10 * 60)
            else:
                print "Latest entry was the same as previous latest entry"
                print "Sleeping 30 seconds"
                print
                time.sleep(30)
        else:
            print "The latest song played has changed since the last run"
            output_dict = dict()
            output_songs = list()
            for entry in entries:
                d = {
                    'timestamp': calendar.timegm(entry.timestamp.utctimetuple()),
                    'artist': entry.artist,
                    'title': entry.title,
                }
                output_songs.append(d)
            output_dict['songs'] = output_songs

            with open_file_or_stream(args.destination, sys.stdout) as f:
                json.dump(output_dict, f)

            previous_latest_entry = latest_entry

            # by default (the song started greater than X minutes ago), we want to check
            # more often since there is a greater chance the song is ending sooner
            new_song_wait = timedelta(minutes=2)
            if now < (latest_entry.timestamp + new_song_wait):
                print "Latest song started less than", new_song_wait, "ago, so sleeping until that time has passed"
                time_difference = (latest_entry.timestamp + new_song_wait) - now
                seconds_to_sleep = time_difference.total_seconds()
                print "Sleeping", seconds_to_sleep, "seconds"
                print
                time.sleep(seconds_to_sleep)
            else:
                print "Latest song started over", new_song_wait, "ago, so sleep for normal 30 seconds"
                print
                time.sleep(30)
