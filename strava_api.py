#!/usr/bin/env python3
from dotenv import load_dotenv
import os
import requests
import logging
from time import sleep
from urllib.parse import urlparse
from urllib.parse import parse_qs

class StravaAPI:
    def __init__(self):
        self.logger= logging.getLogger('strava_api')
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        self.logger.addHandler(handler)

        self.secrets_path=os.path.dirname(os.path.realpath(__file__)) + "/secrets.env"
        if os.path.exists(self.secrets_path) == False:
            self.logger.info("No secrets file detected.")
            authorization_result = self.get_strava_authorization()
            if authorization_result == False:
                self.logger.error("Did not manage to grant authorization to exporter. Abort.")
            else:
                self.update_secrets_file()
        load_dotenv(dotenv_path=self.secrets_path)
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.refresh_token = os.getenv("REFRESH_TOKEN")
        self.access_token = self.get_access_token_from_refresh_token(self.client_id, self.client_secret, self.refresh_token)
        if self.access_token == None:
            self.logger.warning("Can not get access token to use Strava API")
            raise OSError

    def get_strava_authorization(self):
        self.logger.info("You need to create a Strava application. When done, please note client id and client secret, needed for export authorization")
        self.logger.info("Please enter your application ID :")
        self.client_id = input()
        self.logger.info("Please enter your application secret :")
        self.client_secret = input()
        oauth_url = "https://www.strava.com/oauth/authorize?client_id="+self.client_id+"&response_type=code&redirect_uri=http://localhost&approval_prompt=force&scope=activity:write"
        self.logger.info("Now, please enter this URL in your browser : {}".format(oauth_url))
        self.logger.info("Then authorize application, and copy redirected URL here to grant authorization to exporter :")
        oauth_url_response = input()
        try:
            authorization_code = parse_qs(urlparse(oauth_url_response).query)["code"]
        except:
            self.logger.warning("Can not parse OAuth url response")
            return False
        self.access_token = self.get_access_token_from_authorization_code(self.client_id, self.client_secret, authorization_code)
        if self.refresh_token == None:
            self.logger.warning("Did not get access and refresh token from authorization code")
            return False
        self.logger.info("Application authorized for Strava API")
        return True

    def get_access_token_from_authorization_code(self, client_id, client_secret, authorization_code):
        token = None
        payload={"client_id": client_id, "client_secret": client_secret, "code": authorization_code, "grant_type": "authorization_code"}
        response = requests.post("https://www.strava.com/oauth/token", data=payload)
        self.logger.debug("Raw token request response ({}): {}".format(response.status_code, response.text))
        if response.status_code == 200:
            token = response.json()["access_token"]
            self.refresh_token = response.json()["refresh_token"]
            self.update_secrets_file()
        return token

    def get_access_token_from_refresh_token(self, client_id, client_secret, refresh_token):
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

    def update_secrets_file(self):
        with open(self.secrets_path, "w") as secrets_file:
            secrets_file.write("CLIENT_ID="+self.client_id+"\r\n")
            secrets_file.write("CLIENT_SECRET="+self.client_secret+"\r\n")
            secrets_file.write("REFRESH_TOKEN="+self.refresh_token+"\r\n")
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

