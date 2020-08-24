#!/usr/bin/env python3
from dotenv import load_dotenv
import os
import requests
import logging
from time import sleep

class StravaAPI:
    def __init__(self, secrets_path):
        self.logger= logging.getLogger('strava_api')
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        self.logger.addHandler(handler)

        self.secrets_path = secrets_path
        load_dotenv(dotenv_path=secrets_path)
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.refresh_token = os.getenv("REFRESH_TOKEN")
        self.access_token = self.get_access_token(self.client_id, self.client_secret, self.refresh_token)
        if self.access_token == None:
            self.logger.warning("Can not get access token to use Strava API")
            raise OSError

    def get_access_token(self, client_id, client_secret, refresh_token):
        token = None
        payload={"client_id": client_id, "client_secret": client_secret, "refresh_token": refresh_token, "grant_type": "refresh_token"}
        response = requests.post("https://www.strava.com/oauth/token", data=payload)
        self.logger.debug("Raw token request response ({}): {}".format(response.status_code, response.text))
        if response.status_code == 200:
            token = response.json()["access_token"]
            refresh_token = response.json()["refresh_token"]
            if refresh_token != self.refresh_token:
                self.refresh_token = refresh_token
                self.update_secrets_file()
        return token

    def update_secrets_file():
        with open(self.secrets_path, "w") as secrets_file:
            secrets_file.write("CLIENT_ID="+self.client_id)
            secrets_file.write("CLIENT_SECRET="+self.client_secret)
            secrets_file.write("REFRESH_TOKEN="+self.refresh_token)
        self.logger.info("Secrets file updated")

    def upload_activity(self, activity_path, activity_name):
        header = {"Authorization": "Bearer " + self.access_token}
        payload = {"activity_type": "ride", "name": activity_name, "data_type": "fit"}
        files =  {"file": open(activity_path, "rb")}
        response = requests.post("https://www.strava.com/api/v3/uploads", headers=header, data=payload, files=files)
        self.logger.debug("Raw upload request response ({}): {}".format(response.status_code, response.text))
        if(response.status_code != 201):
            self.logger.error("Error requesting activity upload for {}".format(activity_path))
            return
        activity_id=response.json()["id"]
        processing_status = self.poll_upload_status(activity_id)
        if processing_status == False:
            self.logger.error("Error during activity processing for {}".format(activity_path))
        else:
            self.logger.info("Activity {} properly uploaded".format(activity_path))

    def upload_n_activities(self, activities_list):
        for activity in activities_list:
            name = input("Enter a name for activity {} :\r\n". format(activity))
            self.upload_activity(activity, name)

    def poll_upload_status(self, activity_id):
        processing_finished = False
        result = False
        while processing_finished == False:
            sleep(3)
            header = {"Authorization": "Bearer " + self.access_token}
            response = requests.get("https://www.strava.com/api/v3/uploads/"+ str(activity_id), headers=header)
            self.logger.debug("Raw upload polling response ({}): {}".format(response.status_code, response.text))
            error = response.json()["error"]
            status = response.json()["status"]
            if error != None:
                print("End of processing polling with error \"{}\"".format(error))
                processing_finished = True
            elif status == "Your activity is ready.":
                processing_finished = True
                result = True
        return result

