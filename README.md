# gmailme
A Raspberry Pi (or other *nix computer) sends emails via its own gmail account.

It is all coded in a Python class that you can subclass and fill out some methods to send custom emails about whatever you're monitoring.

# setup
Check out this repo, drop it on the Raspberry Pi. In my case I'm using the defauilt "pi" user, I put the code under pi's home directory.

Then setup the gmail info file. I keep mine in $HOME/.gmail.json. You can override the location withe the -g/--gmail_file option.
```
{
    "user": "rasp.pi.username",                   # my Pi has its own gmail account, put the username here
    "passwd": "gmail.application.key",            # the Pi's gmail account has an application key to access the account
    "to": "destination.user.name@gmail.com",      # my email, the destination of the emails it is sending here
    "from": "rasp.pi.username@gmail.com"          # and the full Pi gmail address to send from
}
```

Lastly, setup any scripts you want run and when in the pi user's crontab.

```
$ crontab -e         # launches editor to modify pi's cron entries

# every day near 11 check on COVID in MD stats
50 10 * * * /home/pi/gmailme/coronacheck.py

# Wed 4AM tell me how long I've been home
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
* -g/--gmail_file lets you specify where to find the JSON file with gmail information as described above. Used to override the default location.

# writing new scripts
gmailme is written with Python 3, intended for running on my Raspberry Pi. It should work on other *nix systems without any problems.

bootnotice.py is a very simple example of how to write a script using gmailme. It sends an email to me every time the Pi reboots. See the crontab example above for how to set it to run every time the device boots.

All you have to do is create a class that inherits from GMailMe, put its name in the __init__ (it uses this name to name the logfile it generates). Then override generate_subject() and generate_message_body() to compute anything needed, fetch web files, etc, and fill in self.subject and self.message with the message information. Invoking the go() method causes it to do all the work to call those methods, do the logging, handle arguments, and send the email.

If you look at the go() method you'll see it just calls a series of other methods to do all the right steps.

In the coronacheck.py example script, in __init__, there is an example of how to add addtitional options to the script, beyond -n and -g. It adds -d/--days to let the user specify how many days of COVID data to pull from the Maryland stats.

# references
A writeup on how to [send email with gmail and python](https://stackabuse.com/how-to-send-emails-with-gmail-using-python/)

Some info on [gmail application passwords](https://support.google.com/mail/answer/185833).

# todo
Send fancier email, HTML formatted or what have you, with proper MIME header.

