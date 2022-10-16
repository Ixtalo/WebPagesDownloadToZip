#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""downloader.py - Downloads Web-pages and stores them into a ZIP file.

From a list of URLs download the web-pages and store the HTML into a ZIP file.

Usage:
  downloader.py [options] <config.json>
  downloader.py -h | --help
  downloader.py --version

Arguments:
  config.json       Configuration file, JSON format.

Options:
  -h --help         Show this screen.
  --logfile=FILE    Logging to FILE, otherwise use STDOUT.
  --no-color        No colored log output.
  --no-sleep        Do not sleep/wait randomly.
  -v --verbose      Be more verbose.
  --version         Show version.
"""
##
# LICENSE:
##
# Copyright (c) 2022 by Ixtalo, ixtalo@gmail.com
##
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
##
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
##
import sys
import time
import zipfile
import os.path
import urllib
import logging
import json
from pathlib import Path
from time import sleep
from random import randint
import requests     # https://pypi.org/project/requests/
import colorlog
from docopt import docopt


__appname__ = "WebPagesDownloadToZip"
__version__ = "1.1.0"
__date__ = "2022-10-03"
__updated__ = "2022-10-06"
__author__ = "Ixtalo"
__email__ = "ixtalo@gmail.com"
__license__ = "AGPL-3.0+"
__status__ = "Production"


LOGGING_STREAM = sys.stdout
DEBUG = bool(os.environ.get("DEBUG", "").lower() in ("1", "true", "yes"))
__script_dir = Path(__file__).parent


def __get_check_zipfilename(datadir):
    now = time.strftime("%Y-%m-%d_%H%M%S")
    filepath = datadir.joinpath("%s.zip" % now)
    logging.info("filepath: %s", filepath.resolve())
    assert not filepath.exists(), "target ZIP must not exist already!"
    return filepath


def __get_check_datadir(config):
    datadir = Path(config["datadir"])
    if not datadir.is_absolute():
        datadir = __script_dir.joinpath(datadir)
    logging.debug("datadir: %s", datadir.resolve())
    assert datadir.is_dir(), "datadir must be an existing directory!"
    return datadir


def __check_config(config):
    assert config["datadir"], "invalid configuration!"
    assert config["headers"], "invalid configuration!"
    assert config["urls"], "invalid configuration!"
    assert len(config["urls"]) > 0, "invalid configuration!"


def __setup_logging(log_file: str = None, verbose=False, no_color=False):
    stream = LOGGING_STREAM if not log_file else open(log_file, "a")
    handler = colorlog.StreamHandler(stream=stream)

    format_string = "%(log_color)s%(asctime)s %(levelname)-8s %(message)s"
    formatter = colorlog.ColoredFormatter(format_string, datefmt="%Y-%m-%d %H:%M:%S", no_color=no_color)
    handler.setFormatter(formatter)

    logging.basicConfig(level=logging.WARNING if not DEBUG else logging.DEBUG, handlers=[handler])
    if verbose:
        logging.getLogger("").setLevel(logging.INFO)


def run(config: dict, no_sleep=False):
    __check_config(config)
    datadir = __get_check_datadir(config)
    zipfilename = __get_check_zipfilename(datadir)

    urls = config["urls"]
    logging.info("#URLs: %d", len(urls))

    with zipfile.ZipFile(zipfilename, "w", zipfile.ZIP_DEFLATED) as zf:
        for url in urls:

            if not no_sleep:
                ## random sleep to masquerade script automatic downloading
                sleep_time_seconds = randint(35, 621)
                logging.info("random sleep for %d seconds ...", sleep_time_seconds)
                sleep(sleep_time_seconds)

            ## HTTP GET
            logging.info("HTTP GET '%s' ...", url)
            r = requests.get(url, headers=config["headers"])
            logging.debug("response status:%d", r.status_code)

            if r.ok:
                ## determine filename based on URL path
                u = urllib.parse.urlparse(url)
                basename = os.path.basename(u.path)
                logging.debug("basename: %s", basename)

                if not basename:
                    # no basename => most probably the root/homepage/index.html
                    basename = "index.html"

                logging.debug("writing %s bytes to ZIP ...", len(r.text))
                zf.writestr(basename, r.text)
            else:
                logging.error(r.reason)


def main():
    """Run main program entry.

    :return: exit/return code
    """
    version_string = f"WebPagesDownloadToZip {__version__} ({__updated__})"
    arguments = docopt(__doc__, version=version_string)
    # print(arguments)
    arg_logfile = arguments["--logfile"]
    arg_nocolor = arguments["--no-color"]
    arg_verbose = arguments["--verbose"]
    arg_config = arguments["<config.json>"]
    arg_nosleep = arguments["--no-sleep"]

    __setup_logging(arg_logfile, arg_verbose, arg_nocolor)
    logging.info(version_string)

    config_file = Path(arg_config)
    if not config_file.exists():
        # try config-file from script directory
        config_file = __script_dir.joinpath(arg_config)
    if not config_file.exists():
        # still no config!
        raise RuntimeError("No such config file: %s" % config_file.resolve())
    logging.info("loading config file '%s' ...", config_file.resolve())
    config = json.load(config_file.open())

    run(config, no_sleep=arg_nosleep)


if __name__ == '__main__':
    if DEBUG:
        # sys.argv.append('--verbose')
        pass
    if os.environ.get("PROFILE", "").lower() in ("true", "1", "yes"):
        import cProfile
        import pstats
        profile_filename = f"{__file__}.profile"
        cProfile.run('main()', profile_filename)
        with open(f'{profile_filename}.txt', 'w', encoding="utf8") as statsfp:
            profile_stats = pstats.Stats(profile_filename, stream=statsfp)
            stats = profile_stats.strip_dirs().sort_stats('cumulative')
            stats.print_stats()
        sys.exit(0)
    sys.exit(main())
