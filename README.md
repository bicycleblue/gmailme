# gmailme
Send an email via gmail and an application key.

The idea is my Raspberry Pi is sitting idle most of the time, might as well have it kick off small jobs (from cron) to email me about things.

# setup
Check out the gmailme project, drop it on the Raspberry Pi. In my case I'm using the defauilt "pi" user, I put the code under pi's home directory.

Then setup the gmail info file. I keep mine in $HOME/.gmail.json. That's hard-coded, need to make that an option in a future version.
{
    "user": "rasp.pi.username",                   # my Pi has its own gmail account, put the username here
    "passwd": "gmail.application.key",            # the Pi's gmail account has an application key to access the account
    "to": "destination.user.name@gmail.com",      # my email, the destination of the emails it is sending here
    "from": "rasp.pi.username@gmail.com"          # and the full Pi gmail address to send from
}
