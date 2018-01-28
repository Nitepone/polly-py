#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 nitepone <luna@moon>

"""
Collect MACs in regex
"""

import re
import subprocess
from time import sleep

targetSSID = "RIT"

with open(input("Output file: "), "r+") as outfile:
    outputRegex = "|"+outfile.read()
    rawdata = subprocess.getoutput("iw dev wlp4s0 scan")
    macRegex = re.compile(r"(?<=BSS )[0-9a-fA-F].+?(?=\()")
    ssidRegex = re.compile(r"(?<=SSID: ).+?(?=\n)")
    for i in range(1):
        for ap in rawdata.split("Extended capabilities:"):
            currMac = macRegex.search(ap)
            currSSID = ssidRegex.search(ap)
            if currMac != None and currSSID != None:
                if currSSID.group(0) == targetSSID and\
                   re.search(currMac.group(0),outputRegex) == None:
                    print("Target found")
                    print(currMac.group(0) + currSSID.group(0))
                    outputRegex+=("|"+currMac.group(0))
    outputRegex = outputRegex[1:]
    outfile.write(outputRegex)
print(outputRegex)
