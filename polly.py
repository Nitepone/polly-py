#! /usr/bin/env python3
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
import sys

#I AM SORRY!
import os


DEFAULT_POLL_RATE=5
DEFAULT_REPEAT_VAL=0

"""
primary class that polls commands that match methods
"""
class polling_thread(threading.Thread):

    def __init__(self, command, actions, time, repeat):
        threading.Thread.__init__(self)
        self.command = command
        self.actions = actions
        self.time = time
        self.halt = False
        self.repeat = repeat

    def run(self):
        print("Thread up for " + str(self.command))
        lastResponse = None
        lastMatch = None
        #main thread loop
        while(not self.halt):
            currResponse = self.command.execute()
            #Check if responce changed
            if (currResponse != lastResponse):
                #loop through matchables to see what action to take
                matchFound = False #Catch when we exit loop without match
                for key in self.actions:
                    if key.search(currResponse):
                        matchFound = True
                        #Prevent reuse of same match
                        if lastMatch == key and self.repeat == 0:
                            print("New response "+str(currResponse)+
                                  " replaces "+str(lastResponse)+" but we do "+
                                  "nothing")
                        #new match
                        else:
                            print("New response "+str(currResponse)+" replaces "+
                                  str(lastResponse)+" and we run "+
                                    str(self.actions[key]))
                            os.system(str(self.actions[key]))
                            lastMatch = key
                            matchFound = True
                            break
                #Catch when no match was found
                if not matchFound:
                    print("New response "+str(currResponse)+
                          ". No match found...")
                lastResponse = currResponse
            #Wait for next poll
            time.sleep(self.time)

    def stop(self):
        self.halt = True


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

    def executeFree(self):
        subprocess.call(self.command)

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


"""
Reads a polly.conf from filename and turns into a threads
filepath: filepath to polly.conf
"""
def read(filepath):

    config = {}
    with open(filepath, "r") as infile:
        currCommand = None
        currSearch = None
        for line in infile:
            line = line.strip()
            #parse empty or commented lines by ignoring
            if line.startswith("#") or line == "":
                pass
            #parse "command:" lines, create dict and move pointer
            elif line.startswith("command:"):
                currCommand = runable(line[8:].strip())
                config[currCommand] = [{},DEFAULT_POLL_RATE,
                                       DEFAULT_REPEAT_VAL]
            #parse "search:" lines, create dict entry and move pointer
            elif line.startswith("search:"):
                regex = line[7:].strip()
                #Catch duplicates
                duplicate = False
                for e in config[currCommand][0].keys():
                    if str(e) == regex:
                        duplicate = True
                        print("Duplicate search term " + regex + " ignored")
                        break
                if not duplicate:
                    currSearch = matchable(line[7:].strip())
                    config[currCommand][0][currSearch] = None
            #parse "action:" lines, prevent overwrite
            elif line.startswith("action:"):
                currAction = runable(line[7:].strip())
                if config[currCommand][0][currSearch] == None:
                    config[currCommand][0][currSearch] = currAction
                else:
                    print("A search may only have one action!")
            #parse "rate:" lines, make sure valid
            elif line.startswith("rate:"):
                value = line[5:].strip()
                try:
                    value = float(value)
                    config[currCommand][1] = value
                except ValueError:
                    print("Invalid 'rate' for command: "+str(currCommand))
                    print(value)
            #parse "repeat:" lines
            elif line.startswith("repeat:"):
                value = line[7:].strip()
                if value == "1" or value == "0":
                    config[currCommand][2] = int(value)

    #Create threads out of what we read
    threads = []
    for key in config:
        print("Init: "+str(key)+" with "+str(config[key][1]))
        threads.append(polling_thread(key,config[key][0],config[key][1],
                                      config[key][2]))
    return threads


"""
Starts a set of threads
threads: list of threads to start
"""
def start(threads):
    for thread in threads:
        thread.start()
    return threads

"""
A basic CLI to manage threads
threads: list of threads to manage
"""
def cli(threads):
    running = True
    if len(threads) == 0:
        print("No threads to start!")
    else:
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
                running = False

"""
Creates threads from config at filepath and runs them with basic CLI
filepath: location of polly.conf
"""
def startCli(filepath):
    cli(start(read(filepath)))

"""
Creates threads from config at filepath and runs them without an interface
filepath: location of polly.conf
"""
def startHeadless(filepath):
    while(1):
        start(read())

if __name__ == "__main__":
    if len(sys.argv) == 1:
        startCli(input("Filepath: "))
    else:
        startCli(sys.argv[1])
