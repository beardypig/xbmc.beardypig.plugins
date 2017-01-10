#!/usr/bin/env python
from __future__ import print_function, unicode_literals

import argparse
import os
import hashlib

import sys


class AddonsXML(object):
    """
        Generates a new addons.xml file from each addons addon.xml file
        and a new addons.xml.md5 hash file.
    """

    def __init__(self):
        # generate files
        self.addons = []

    def write(self, path):
        sys.stderr.write("Writing {0}\n".format(path))
        with open(path, "w") as addons_xml:
            addons_xml.write("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n")
            addons_xml.write("<addons>\n")
            for addon in self.addons:
                for line in addon:
                    if not line.startswith("<?xml"):
                        addons_xml.write(line)
            addons_xml.write("</addons>\n")

    def add_addon(self, path):
        sys.stderr.write("Reading addon.xml for {0}\n".format(path))
        addon_xml_path = os.path.join(path, "addon.xml")
        if os.path.exists(addon_xml_path):
            with open(addon_xml_path, "r") as addon_fd:
                self.addons.append(addon_fd.read())
        else:
            sys.stderr.write("Cannot find addon.xml for {0}\n".format(path))

    def write_md5(self, xml_path, md5_path):
        sys.stderr.write("Writing {0}\n".format(md5_path))
        # create a new md5 hash
        m = hashlib.new("md5")
        m.update(open(xml_path).read())
        # save file
        with open(md5_path, "w") as out:
            out.write(m.hexdigest())


if __name__ == "__main__":
    # start
    parser = argparse.ArgumentParser("Generate addons.xml file")
    parser.add_argument("addon_dir", nargs="+")

    args = parser.parse_args()

    xml = AddonsXML()
    for addon_dir in args.addon_dir:
        xml.add_addon(addon_dir)

    xml.write("addons.xml")
    xml.write_md5("addons.xml", "addons.xml.md5")
