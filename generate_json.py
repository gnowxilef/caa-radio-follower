#!/usr/bin/env python
import argparse
from bs4 import BeautifulSoup
import calendar
from datetime import datetime
import json
import requests
import sys


LAST_PLAYED_URL = 'http://nol888.com/~nlum/caa-radio.php'


if __name__ == '__main__':
    description = "Save the latest songs played on CAA radio to json"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'),
                        default=sys.stdout)
    args = parser.parse_args()

    r = requests.get(LAST_PLAYED_URL)

    if r.status_code != 200:
        sys.stderr.write(("Got HTTP status code {0}"
            "while fetching page {1}").format(r.status_code, LAST_PLAYED_URL))
        sys.exit(1)

    ret = dict()

    doc = BeautifulSoup(r.text)
    table = doc.find('table')
    rows = table.tbody.find_all('tr', recursive=False)
    ret['songs'] = list()
    for row in rows:
        cells = row.find_all('td', recursive=False)

        date_cell = cells[0]
        song_cell = cells[1]

        timestamp = datetime.strptime(date_cell.text,
                                      "%B %d, %Y %I:%M:%S%p %Z")

        if ' - ' in song_cell.text:
            (artist, title) = song_cell.text.split(' - ', 1)
        else:
            artist = None
            title = song_cell.text

        ret['songs'].append({
            'timestamp': calendar.timegm(timestamp.utctimetuple()),
            'artist': artist,
            'title': title,
        })
    json.dump(ret, args.outfile)
