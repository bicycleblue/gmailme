#!/usr/bin/env python3

import gmailme
import datetime


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

        self.message = "Home since {}\n".format(start_date)
        self.message += "  {} days of isolation\n".format(delta_days.days)
        self.message += "  {} weeks of isolation\n".format(str(round(delta_days.days / 7, 2)))


if __name__ == "__main__":
    ww = WorkWeek()
    ww.go()

