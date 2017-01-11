#!/usr/bin/env python
from __future__ import print_function, unicode_literals

import argparse
import hashlib
import logging
import os
from urllib.parse import urljoin
import xml.etree.ElementTree as ET
from datetime import datetime

import requests
import dateutil.parser

log = logging.getLogger("addon-indexer")


class S3AddonsXML(object):
    """

    """

    def __init__(self, session, bucket):
        self.session = session
        self.bucket = bucket
        self.xmls = []
        self._last_updated = None

    @property
    def last_updated(self):
        return self._last_updated or datetime.now()

    @last_updated.setter
    def last_updated(self, value):
        if self._last_updated is None or value > self._last_updated:
            self._last_updated = value

    @property
    def bucket_url(self):
        return "https://{bucket}.s3.amazonaws.com/".format(bucket=self.bucket)

    def write(self, path):
        log.info("Writing addon index to {0}".format(path))
        with open(path, "w") as addons_xml:
            addons_xml.write("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n")
            addons_xml.write("<addons>\n")
            for addon in self.xmls:
                for line in addon:
                    if not line.startswith("<?xml"):
                        addons_xml.write(line)
            addons_xml.write("</addons>\n")

    def add(self, path, date):
        log.info("Reading addon.xml for {0}".format(path))
        res = self.session.get(path, verify=False)
        self.xmls.append(res.text)
        self.last_updated = date

    def write_last_updated(self, path):
        log.info("Writing last updated date to {0}".format(path))
        with open(path, "w") as out:
            out.write(self.last_updated.isoformat())

    def addons(self):
        res = self.session.get(self.bucket_url, verify=False)

        tree = ET.fromstring(res.text)
        for contents in tree.findall(".//{http://s3.amazonaws.com/doc/2006-03-01/}Contents"):
            key = contents.find("./{http://s3.amazonaws.com/doc/2006-03-01/}Key")
            if key.text.endswith("addon.xml"):
                log.info("Found addon: {0}".format(key.text))

                date = contents.find("./{http://s3.amazonaws.com/doc/2006-03-01/}LastModified")
                dt = dateutil.parser.parse(date.text)
                yield urljoin(self.bucket_url, key.text), dt


if __name__ == "__main__":
    # start
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Index Kodi addons stored in an S3 bucket")
    parser.add_argument("--out-dir", default=".")
    parser.add_argument("bucket")

    args = parser.parse_args()

    session = requests.Session()

    indexer = S3AddonsXML(session, args.bucket)

    for url, last_updated in indexer.addons():
        indexer.add(url, last_updated)

    indexer.write(os.path.join(args.out_dir, "addons.xml"))
    indexer.write_last_updated(os.path.join(args.out_dir, "last_updated"))
