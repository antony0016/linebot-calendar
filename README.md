# Line Calendar

## Overview
This program is a group calendar for line, 
you can use this for reserve an event with your friend,
and share your event to your family.

## Setup
1. Clone this repository.
2. Run `pip install -r requirement.txt`
(if your platform is not windows, you should install other
lib for pyodbc, like [this](https://stackoverflow.com/questions/35991403/pip-install-unroll-python-setup-py-egg-info-failed-with-error-code-1)).
3. Run `python app.py`
4. Use ngrok or other reverse proxy service
to get a https URL.
5. Go to [Line Developer Console](https://developers.line.biz/console/)
6. Choose your linebot and change the web hook URL 
to your HTTPS URL.
7. Add this linebot as your line friend, and have fun with your linebot.
