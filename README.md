# Python URL Shorterner

This is a very simple and deployable link shortener deployed using Flask and Python. It takes in any URL (eg. www.youtube.com) and converts it into a shortened link like bit.ly (<domain>/r7ks) that can be easily sent.

It uses Hashids to generate unique and unpredictable strings for URLs. Data used by the application is stored in a SQLite file for convenience.

I might modify this in the future to allow customizable links (eg. <domain>/mywebsite) but for now this works well for a local link shortener.

<b>NOTE:</b> This repo is no longer maintained. The app still works but it wil no longer be updated.

## Installation

Pre-requisites:

- Python

Install dependencies, create the SQLite database and run the flask application

```
  pip install -r requirements.txt
  py init_db.py
  flask run
```

You can access the application at 127.0.0.1:5000 or <your_domain>:5000.

## Contributing

This is just a pet project but contributions are always welcome if you want to!

Just create a pull request and i'll add it in lol.

## Features

- Just input a link and have it automatically converted
- Enter shortened link into browser to go to original link
- Delete or view click frequency in the Links page
