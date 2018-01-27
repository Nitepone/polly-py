#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 nitepone <luna@moon>

"""
This is a build of polly in python,  polling daemon that reacts to changes
in command outputs.
"""
import time
import threading
import re
import subprocess

class polling_thread(threading.Thread):

    def __init__(self, pollable, actions, time):
        threading.Thread.__init__(self)
        self.pollable = pollable
        self.actions = actions
        self.time = time
        self.stop = False

    def run(self):
        print("Thread up for " + str(self.pollable))
        lastResponse = None
        #main thread loop
        while(not self.stop):
            currResponse = self.pollable.execute()
            #Check if responce changed
            if (currResponse != lastResponse):
                #loop through matchables to see what action to take
                matchFound = False #Catch when we exit loop without match
                for key in self.actions:
                    if key.search(currResponse):
                        print("New response "+str(currResponse)+" replaces "+
                              str(currResponse)+" and we run "+str(actions(key)))
                        actions(key).execute()
                        matchFound = True
                        break
                if not matchFound:
                    print("New response "+str(currResponse)+". No match found...")
                lastResponse = currResponse
            time.sleep(self.time)

    def stop(self):
        self.stop = True


"""
A class to contain a runable external command
"""
class runable:

    def __init__(self, command):
        self.command = command

    """
    Run the external command and return output
    """
    def execute(self):
        return subprocess.getoutput(self.command)

    def __str__(self):
        return self.command


"""
A class to contain regex expressions
"""
class matchable:

    def __init__(self, regex):
        self.regexString = regex
        self.regexCompile = re.compile(regex)

    """
    Search the regex in the passed string
    """
    def search(self, string):
        return self.regexCompile.search(string) != None

    def match(self, string):
        return self.regexCompile.match(string) != None

    def __str__(self):
        return self.regexString

def read(filename):

    config = {}
    with open(filename, "r") as infile:
        currCommand = None
        currSearch = None
        for line in infile:
            line = line.strip()
            if line.startswith("#") or line == "":
                pass
            elif line.startswith("command:"):
                currCommand = runable(line.replace("command:", ""))
                config[currCommand] = {}
            elif line.startswith("search:"):
                currSearch = matchable(line.replace("match:", ""))
                config[currCommand][currSearch] = None
            elif line.startswith("action:"):
                currAction = runable(line.replace("action:", ""))
                if config[currCommand][currSearch] == None:
                    config[currCommand][currSearch] = currAction
                else:
                    print("A search may only have one action!")
    return config


def process(config):
    threads = []
    for key in config:
        print("Init: "+str(key)+" with "+str(config[key]))
        threads.append(polling_thread(key,config[key],5))
    for thread in threads:
        thread.start()
    return threads

def cli(threads):
    running = True
    while(running):
        userCommand = input()
        if userCommand == "h" or userCommand == "":
            print("[h]elp, [r]unning threads, [s]top")
        elif userCommand == "r":
            for thread in threads:
                print(thread)
        elif userCommand == "s":
            for thread in threads:
                thread.stop()
            for thread in threads:
                thread.join()

cli(process(read("example.conf")))

