#!/usr/bin/env python3
import os
import psutil
import logging

class DeviceEdge200:
    DEVICE_LABEL="GARMIN"
    ACTIVITIES_PATH="Garmin/Activities"
    def __init__(self):
        self.logger= logging.getLogger('device_edge200')
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        self.logger.addHandler(handler)

        hard_drive_label =self.get_hard_drive_label()
        if hard_drive_label == None:
            raise OSError

        mount_point = self.get_device_mount_point(hard_drive_label)
        if mount_point == None:
            raise OSError
        else:
            self.activities_path = mount_point + "/" + self.ACTIVITIES_PATH

    def get_hard_drive_label(self):
        path = "/dev/disk/by-label/" + self.DEVICE_LABEL
        self.logger.debug("Searching for disk path {}".format(path))
        if os.path.exists(path) == False:
            self.logger.warning("Path not found")
            return None
        else:
            self.logger.debug("Path found")
            return os.path.realpath(os.path.join(os.path.dirname(path), os.readlink(path)))

    def get_device_mount_point(self, device):
        partitions = psutil.disk_partitions()
        result = None
        self.logger.debug("Searching for mount point of device {}".format(device))
        for partition in partitions:
            if partition.device == device:
                result = partition.mountpoint
        if result != None:
            self.logger.debug("Device found mounted at {}".format(result))
        else:
            self.logger.warning("Mount point not found")
        return result

    def list_all_activities(self):
        activities = []
        for (dirpath, dirnames, filenames) in os.walk(self.activities_path):
            for filename in filenames:
                activities.append(os.path.join(dirpath, filename))
        # Sort files by newest, assuming the name embed the activity date
        activities.reverse()

        return activities

    def list_nth_activities(self, number):
        returned_number = number
        activities = self.list_all_activities()
        if len(activities) < number:
            returned_number = len(activities)
        return activities[:returned_number]