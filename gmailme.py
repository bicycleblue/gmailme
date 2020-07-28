#!/usr/bin/env python3

import os
import sys
import logging
import argparse
import json
import smtplib
import time


class GMailMe:
    def __init__(self):
        if not hasattr(self, 'name'):
            self.name = "gmailme"

        self.__start_logger()
        logging.info("=" * 24)
        logging.info("starting {}".format(self.name))
        logging.info(time.strftime("%a %d %b %Y"))
        logging.info("{} starting".format(sys.argv[0]))

        self.parser = argparse.ArgumentParser(description="notify me",
                                              formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        self.parser.add_argument('-n', '--nope', action='store_true',
                                 help="test, do everything but don't send email")
        self.parser.add_argument('-g', '--gmail_file', type=str,
                                 help="JSON file with gmail account info",
                                 default=os.path.expanduser("~/.gmail.json"))


    def go(self):
        self.check_args()
        self.generate_subject()
        self.generate_message_body()
        self.send_message()


    def check_args(self):
        self.args = self.parser.parse_args()

        #for a in vars(self.args):
        #    logging.debug("{} {}".format(a, getattr(self.args, a)))

        self.__get_gmail_info()


    def generate_subject(self):
        self.message = "default subject. override generate_subject() to customize"


    def generate_message(self):
        self.message = "default message. override generate_message() to customize"


    def send_message(self):
        self.__send_email()

        logging.info("{} ending".format(sys.argv[0]))


    def __is_cron_job(self):
        if os.isatty(sys.stdin.fileno()):
            logging.debug("not cron job")
            return(False)

        logging.debug("am cron job")
        return(True)


    def __start_logger(self):
        print("setting logfile name with {}".format(self.name))
        logfile = "{}.log".format(self.name)

        logging.basicConfig(filename=logfile,
                            level=logging.DEBUG,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        if not self.__is_cron_job():
            logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

        self.logger = logging.getLogger()  # for subclass to reference


    def __get_gmail_info(self):
        with open(self.args.gmail_file) as f:
            self.gmail = json.load(f)


    def __send_msg(self):
        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.ehlo()
            server.login(self.gmail['user'], self.gmail['passwd'])
            server.sendmail(self.gmail['from'], self.gmail['to'], self.full_msg)
            server.close()

        except Exception as e:
            print('Something went wrong...' + str(e))


    def __send_email(self):
        headers = "From: {}\nTo: {}\nSubject: {}\n\n".format(self.gmail['from'], self.gmail['to'], self.subject)

        logging.info("message = " + self.message)

        self.full_msg = headers + self.message

        if not self.args.nope:
            self.__send_msg()


def main():
    print("testing class")
    gmailme = GMailMe()
    gmailme.check_args()
    gmailme.generate_message()
    gmailme.send_message()


if __name__ == "__main__":
    main()

