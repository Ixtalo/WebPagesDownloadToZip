# Web-Pages Download to ZIP

From a list of URLs download the web-pages and store the HTML into a ZIP file.

## How-To Run

1. (preparation) `python3 -m pip install pipenv`
2. `pipenv sync`
3. create and adjust configuration file: `cp config.example.json config.json` ...
4. `pipenv run python downloader.py config.json`
