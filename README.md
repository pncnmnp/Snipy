# Snipy
**A feature rich URL shortener**

Features:
* verify duplicate links
* auto expiry of url
* copy to clipboard
* spam detection
* number of views
* customize url

### In Action
![url_shorten_demo](https://github.com/pncnmnp/Snipy/blob/master/screenshots/url_shorten_demo.gif)

### How to run the code
sqlite3, termcolor and flask can be installed using:
```
python3 -m pip install sqlite3
python3 -m pip install flask
python3 -m pip install termcolor
```

If you are hosting the site, change the static variable `base` and configure `redirection.py` file accordingly.

To enable spam detection, you will need a valid API key.
I am using Google safe browsing API v4 : https://developers.google.com/safe-browsing/v4/get-started.

Once you get a valid API KEY, enter the key in `api_key.txt` file and change file path in `api_key_file` parameter, in `redirection.py`.

You can then use :
```
export FLASK_APP=redirection.py
flask run
```
To run flask server locally.

The `api` dir contains an implementation of Safe Browsing API using bloom filters, which can be used to temporarily block links causing unnecessary load on server, or some user requested malicious links.

This code was tested on Linux : Ubuntu ( 18.04 LTS ) 
