#!/usr/bin/env python3

import gmailme
import time


class BootMessage(gmailme.GMailMe):
    def __init__(self):
        self.name = "bootnotice"
        super().__init__()

    def generate_subject(self):
        self.subject = "rasppi boot {}".format(time.strftime("%a %d %b %Y"))

    def generate_message_body(self):
        self.message = "I booted up at {}".format(time.strftime("%H:%M:%S on %a %d %b %Y"))


if __name__ == "__main__":
    bm = BootMessage()
    bm.go()

