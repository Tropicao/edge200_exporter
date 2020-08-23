#!/usr/bin/env python3
from device_edge200 import DeviceEdge200
from strava_api import StravaAPI
import sys
import os

def usage():
    print("Usage : {} <number_of_activities_to_upload>".format(sys.argv[0]))
    print("Exemple: {} 3".format(sys.argv[0]))

if len(sys.argv) < 2:
    usage()
    sys.exit(1)
number_of_activities = int(sys.argv[1])

secrets_path=os.path.dirname(os.path.realpath(__file__)) + "/secrets.env"
if os.path.exists(secrets_path) == False:
    print("File {} does not exist, please create it and fill it with Strava credentials", secrets_path)
    sys.exit(1)

try:
    device = DeviceEdge200()
    print("Device found")
except OSError:
    print("Cannot initialize device")

try:
    api = StravaAPI(secrets_path)
except OSError:
    print("Cannot initialize Strava API")

print(device.list_nth_activities(number_of_activities))
