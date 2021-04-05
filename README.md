# Edge 200 Exporter

## Brief
Tiny python tool to export Garming Edge 200 activities to Strava, since Garmin tool "Garmin Connect" does not work natively on Linux

## Preparation

Since the tool is executed on your own computer (i.e. it is not a web tool hosted on any cloud), you will need to create a Strava Application on your own, and when using the tool for the first time, grant this application access to your Strava profile to let it upload your activities.
* To create an application, please go to https://www.strava.com/settings/api. Once created, your application will have its own application ID and application secrets
* When launching the tool for the first time, it will ask for your applications informations (ID and secret), and guide you to negotiate the OAuth authorization process (just follow the instructions in the tools log) to get access to Strava Application.
* When done successfully once, the tool will create a `secrets.env` file to retain your application details, so you will not have to authenticate the next time you use the tool.
* **Security warning : make sure no one has access to your `secrets.env`, or they will be able to upload and modify activities on your account.**

## Usage

Just plug your Garmin Edge 200 to your Linux host through USB and run the following command :

`./main.py`

You can also specify the number of activities you want to upload if you need multiple activities upload. In this case, it will upload the required number of activities, taking the most recent on device :

`./main.py 3`
