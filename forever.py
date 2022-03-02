#!/usr/bin/python
from subprocess import Popen
import sys

pyversion = sys.argv[1]
filename = sys.argv[2]
while True:
    print("\nStarting " + filename)
    p = Popen("python" + " " + filename, shell=True)
    p.wait()