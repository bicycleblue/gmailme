#!/usr/bin/env python3

import gmailme
import datetime
from bingeclock import bingeclock_series
import random


series_list = [{"title": "Breaking Bad",
                "url": "breaking-bad"},
               {"title": "Avatar: The Last Airbender",
                "url": "avatar-the-last-airbender"},
               {"title": "It\'s Always Sunny in Philadelphia",
                "url": "its-always-sunny-in-philadelphia"},
               {"title": "Seinfeld",
                "url": "seinfeld"},
               {"title": "Friends",
                "url": "friends-1994"},
               {"title": "Veep",
                "url": "veep"}
              ]


class WorkWeek(gmailme.GMailMe):
    def __init__(self):
        self.name = "workweek"
        super().__init__()

    def generate_subject(self):
        self.subject = "How long gone?"

    def generate_message_body(self):
        start_date = datetime.date(2020, 3, 18)

        today = datetime.date.today()

        delta_days = today - start_date

        self.message = "Home since {}\n\n".format(start_date)
        self.message += "  {} days of isolation\n".format(delta_days.days)
        self.message += "  {} weeks of isolation\n\n".format(str(int(round(delta_days.days / 7, 2))))

        series = random.choice(series_list)
        self.logger.debug("chose series {}".format(series['title']))

        clock = bingeclock_series(series['url'], hours=8)
        if clock:
            binge_days = clock[0]
            times = int(round(delta_days.days / binge_days))
            self.message += "If you had spent 8 hours a day binging on {},\nyou could have watched the entire series {} times!\n".format(series['title'], times)
        else:
            self.logger.debug("failed to get bingeclock for series {}".format(series['title']))

if __name__ == "__main__":
    ww = WorkWeek()
    ww.go()

