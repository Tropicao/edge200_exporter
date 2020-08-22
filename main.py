#!/usr/bin/env python3
from device_edge200 import DeviceEdge200
import sys

def usage():
    print("Usage : {} <number_of_activities_to_upload>".format(sys.argv[0]))
    print("Exemple: {} 3".format(sys.argv[0]))

if len(sys.argv) < 2:
    usage()
    sys.exit(1)

number_of_activities = int(sys.argv[1])

try:
    device = DeviceEdge200()
    print("Device found")
except OSError:
    print("Cannot initialize device")

print(device.list_nth_activities(number_of_activities))
