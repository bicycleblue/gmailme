# gmailme
During the great isolation of 2020 I wrote some code for a Raspberry Pi to monitor some COVID stats that I care about. It emails me those stats from its own gmail account. I then fleshed it out into a more generic project that lets me quickly script up other things to monitor and send me emails about.

It is all coded in a Python class that you can subclass and fill out some methods to send custom emails about whatever you're monitoring.

# setup
Check out this repo, drop it on the Raspberry Pi. In my case I'm using the defauilt "pi" user, I put the code under pi's home directory.

Then setup the gmail info file. Copy the file .gmail.json.template to $HOME/.gmail.json or wherever you feel is safe to keep it. Make sure to chmod it so others can't see it. If you use an alternate location you can use the -g/--gmail_file option to identify it.
```
{
    "user": "rasp.pi.username",                   # my Pi has its own gmail account, put the username here
    "passwd": "gmail.application.key",            # the Pi's gmail account has an application key to access the account
    "to": "destination.user.name@gmail.com",      # my email, the destination of the emails it is sending here
    "from": "rasp.pi.username@gmail.com"          # and the full Pi gmail address to send from
}
```

Lastly, configure pi's crontab with times/dates and which scripts to run. The example scripts below are all included.

```
$ crontab -e         # launches editor to modify pi's cron entries

# every day near 11am check on COVID in MD stats
50 10 * * * /home/pi/gmailme/coronacheck.py

# Wed 4am tell me how long I've been home
0 4 * * 3 /home/pi/gmailme/workweek.py

# every reboot, let me know
@reboot /home/pi/gmailme/bootnotice.py
```

# usage
The base class for GMailMe implements a couple standard arguments for all instances.
```
$ gmailme.py -h
...
  -h, --help            show this help message and exit
  -n, --nope            nope, don't send email (default: False)
  -g GMAIL_FILE, --gmail_file GMAIL_FILE
                        JSON file with gmail account info (default:
                        /home/pi/.gmail.json)
...
```
* -n/--nope is for development and testing. It tells the script to do all the work to create a message to send, but not to send the email.
* -g/--gmail_file lets you specify where to find the JSON file with gmail information as described above.

# writing new scripts
gmailme is written with Python 3, intended for running on my Raspberry Pi. It should probably work on other *nix systems without any problems as long as you have the approrpriate python modules installed.

bootnotice.py is a very simple example of how to write a script using gmailme. It sends an email to me every time the Pi reboots. See the crontab example above for how to set it to run every time the device boots.

```python
#!/usr/bin/env python3

import gmailme
import time


class BootNotice(gmailme.GMailMe):
    def __init__(self):
        self.name = "bootnotice"
        super().__init__()

    def generate_subject(self):
        self.subject = "rasppi boot {}".format(time.strftime("%a %d %b %Y"))

    def generate_message_body(self):
        self.message = "I booted up at {}".format(time.strftime("%H:%M:%S on %a %d %b %Y"))


if __name__ == "__main__":
    bn = BootNotice()
    bn.go()
```

The important steps are:
* copy bootnotice.py to a new name, yourproject.py
* change the name in __init__ to yourproject, gmailme uses this to name the logfile it generates
* change generate_subject() to have an informative subject line
* change generate_message_body() to fill in the body of the email. plaintext only for now

In the coronacheck.py example script, in __init__, there is an example of how to add addtitional options to the script, beyond -n and -g. It adds -d/--days to let the user specify how many days of COVID data to pull from the Maryland stats.

When run from the commandline, the script will log to a file <yourprojectname>.log. If run from cron it will log to your user's home directory with the same name.

# references
A writeup on how to [send email with gmail and python](https://stackabuse.com/how-to-send-emails-with-gmail-using-python/)

Some info on [gmail application passwords](https://support.google.com/mail/answer/185833).

One set of examples on [how to write crontab entries](https://www.geeksforgeeks.org/crontab-in-linux-with-examples/)

Github docs on [README.md formatting](https://docs.github.com/en/github/writing-on-github/basic-writing-and-formatting-syntax), because I'm still learning that bit.

# todo
Send fancier email, HTML formatted or what have you, with proper MIME header.

