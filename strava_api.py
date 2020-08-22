#!/usr/bin/env python3
from dotenv import load_dotenv
import os
import requests
import logging

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