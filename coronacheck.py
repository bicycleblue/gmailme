#!/usr/bin/env python3

import gmailme
import sys
import argparse
import requests
import time
import logging
import json


# MDCOVID19 TotalCasesStatewide
#json_total = "https://opendata.arcgis.com/datasets/18582de727934249b92c52542395a3bf_0.geojson"
# MDCOVID19 TotalCurrentlyHospitalizedAcuteAndICU
#json_hospital = "https://opendata.arcgis.com/datasets/bf3f201b056b4c488b5dac3441b7ac20_0.geojson"
# from:
# https://coronavirus.maryland.gov/datasets/
# https://coronavirus.maryland.gov/search?collection=Dataset
# click on the "I want to use this" at bottom left. then API Resources to find the JSON files

stats = [{'json_url': "https://opendata.arcgis.com/datasets/18582de727934249b92c52542395a3bf_0.geojson",
          'label': "Total Cases",
          'field': "Count_"},
         {'json_url': "https://opendata.arcgis.com/datasets/bf3f201b056b4c488b5dac3441b7ac20_0.geojson",
          'label': "Hospitalizations",
          'field': "Total"}]


class CoronaCheck(gmailme.GMailMe):
    def __init__(self):
        self.name = "coronacheck"
        super().__init__()

        self.parser.add_argument('-d', '--days', type=self.pos_int, help="how many days to display", default=7)
        self.parser.add_argument('-f', '--force', action='store_true', help="ignore date on data, just do it", default=False)


    def pos_int(self, value):
        ivalue = int(value)
        if ivalue < 1:
            raise argparse.ArgumentTypeError("{} require positive number".format(value))
        return(ivalue)


    def check_args(self):
        super().check_args()


    # assume if the last-modified includes today's date, the daily data is ready
    # yea, that's a lot of weird errors to check for. this function has seen some...
    def todays_data_ready(self, url):
        try:
            resp = requests.head(url)
            if resp.status_code != 200:    # seeing some days where one of them just doesn't exist for a while
                self.logger.debug("server returned non-200 OK status {}".format(resp.status_code))
                return(False)
            last_modified = resp.headers['last-modified']
        except KeyError as e:
            self.logger.debug("KeyError on last-modified header {}".format(str(e)))
            return(False)
        except:
            self.logger.debug("error checking headers")
            return(False)

        todays_date = time.strftime("%d %b %Y")   # ex: "19 June 2020"

        self.logger.debug("last-modified: {} todays_date: {}".format(last_modified, todays_date))

        if last_modified.find(todays_date) > -1:
            self.logger.debug("found it, good to go")
            return(True)

        return(False)


    def all_todays_data_ready(self):
        for stat in stats:
            if self.todays_data_ready(stat['json_url']):
                return(True)

        return(False)


    def get_stat(self, stat):
        resp = requests.get(stat['json_url']) # error checks? if head worked, get should.
        data = json.loads(resp.text)

        prev = 0
        first = True
        message = stat['label'] + "\n\n"

        for f in data['features'][-self.args.days-1:]:
            p = f['properties']
            date = p['DATE'].split('T')[0]
            value = p[stat['field']]
            delta = value - prev
            if first:
                first = False
            else:
                message += "{}: {} {}\n".format(date, value, delta)
            prev = value

        return(message)


    def generate_subject(self):
        self.subject = "MD COVID19 {}".format(time.strftime("%a %d %b %Y"))


    def generate_message_body(self):
        wait_times = [5, 5, 5, 15, 15, 30, 30, 60, 60, 60, 60, 120]  # sometimes they're late. check a few times fast, then throttle

        count = 0
        found = False
        if self.args.force:
            self.logger.debug("force option enabled, accepting data without checking date")
            found = True

        while not found and count < len(wait_times):
            if self.all_todays_data_ready():
                self.logger.debug("todays data is ready, breaking the loop with count {}".format(count))
                found = True
                break
            self.logger.debug("todays data not ready, sleeping for {} minutes".format(wait_times[count]))
            time.sleep(wait_times[count] * 60)
            count += 1

        if not found:
            self.logger.warning("failed to find todays data, timed out after {} tries".format(count))
            sys.exit(1)

        self.message = ""

        for stat in stats:
            self.message += self.get_stat(stat)
            self.message += "\n"

        self.message += "More Data: https://coronavirus.maryland.gov/\n"


if __name__ == "__main__":
    cc = CoronaCheck()
    cc.go()

