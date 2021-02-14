#!/usr/bin/env python3

import gmailme
import sys
import argparse
import requests
import time
import logging
import json


json_total = "https://opendata.arcgis.com/datasets/18582de727934249b92c52542395a3bf_0.geojson"
json_hospital = "https://opendata.arcgis.com/datasets/bf3f201b056b4c488b5dac3441b7ac20_0.geojson"


class CoronaCheck(gmailme.GMailMe):
    def __init__(self):
        self.name = "coronacheck"
        super().__init__()

        self.parser.add_argument('-d', '--days', type=self.pos_int, help="how many days to display", default=7)
        self.parser.add_argument('-f', '--force', action='store_true', help="ignore date on data, just do it", default=7)


    def pos_int(self, value):
        ivalue = int(value)
        if ivalue < 1:
            raise argparse.ArgumentTypeError("{} require positive number".format(value))
        return(ivalue)


    def check_args(self):
        super().check_args()

        print("days = {}".format(self.args.days))


    # assume if the last-modified includes today's date, the daily data is ready
    def todays_data_ready(self, url):
        try:
            resp = requests.head(url)
            if resp.status_code != 200:    # getting some days where one of them just doesn't exist for a while
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


    def get_total(self):
        resp = requests.get(json_total)
        data = json.loads(resp.text)

        prev = 0
        objid = 0

        for f in data['features']:
            p = f['properties']
            count = p['Count_']
            objid = p['OBJECTID']

            #p['DATE'] = p['DATE'].split(' ')[0]
            p['DATE'] = p['DATE'].split('T')[0]

            if objid < 2:
                p['delta'] = 0
            else:
                p['delta'] = count - prev

            prev = count

        message = ""

        for f in data['features'][-self.args.days:]:
            date = f['properties']['DATE']
            count = f['properties']['Count_']
            delta = f['properties']['delta']

            message += "{}: {}\n".format(date, delta)

        return(message)


    def get_hospital(self):
        resp = requests.get(json_hospital)
        data = json.loads(resp.text)

        prev = 0
        objid = 0

        for f in data['features']:
            p = f['properties']
            count = p['Total']
            objid = p['OBJECTID']

            #p['DATE'] = p['DATE'].split(' ')[0]
            p['DATE'] = p['DATE'].split('T')[0]

            if count is None:
                p['delta'] = 0
                continue

            if objid < 2:
                p['delta'] = 0
            else:
                p['delta'] = count - prev

            prev = count

        message = ""

        for f in data['features'][-self.args.days:]:
            date = f['properties']['DATE']
            count = f['properties']['Total']
            delta = f['properties']['delta']

            message += "{}: {} {}\n".format(date, count, delta)

        return(message)


    def get_data(self):
        self.msg_total = self.get_total()
        self.msg_hospital = self.get_hospital()


    def generate_subject(self):
        self.subject = "MD COVID19 {}".format(time.strftime("%a %d %b %Y"))


    def generate_message_body(self):
        wait_times = [5, 5, 5, 15, 15, 30, 30, 60, 60, 60, 60, 120]  # sometimes they're late. check a few times fast, then throttle

        count = 0
        found = False
        if self.args.force:
            self.logger.debug("force option enabled, accepting data without checking date")
            found = True

        while not found and count < 12:
            if self.todays_data_ready(json_total) and self.todays_data_ready(json_hospital):
                self.logger.debug("todays data is ready, breaking the loop with count {}".format(count))
                found = True
                break
            self.logger.debug("todays data not ready, sleeping for {} minutes".format(wait_times[count]))
            time.sleep(wait_times[count] * 60)
            count += 1

        if not found:
            self.logger.warning("failed to find todays data, timed out after {} tries".format(count))
            sys.exit(1)

        self.get_data()

        self.message = "Total Cases\n\n" + self.msg_total + "\n"
        self.message += "Hospitalizations\n\n" + self.msg_hospital + "\n"
        self.message += "More Data: https://coronavirus.maryland.gov/\n"


if __name__ == "__main__":
    cc = CoronaCheck()
    cc.go()

