# Edge 200 Exporter

## Brief
Tiny python tool to export Garming Edge 200 activities to Strava, since Garmin tool "Garmin Connect" does not work natively on Linux

## Preparation
In order to use the tool, a `secrets.env` file must be present in the same directory as `main.py`, with the following structure :
```
CLIENT_ID=51819
CLIENT_SECRET=YYYYYYYYYYYYYY
REFRESH_TOKEN=ZZZZZZZZZZZZZZ
```

* The client ID and client secret are delivered by Strava when creating an app (please see https://www.strava.com/settings/api). So in order to use this tool you will have to create an app on Strava website
* The refresh Token is delivered by Strava API after having validate the proper identification.authorization sequence. This is done thanks to OAuth2. You can find more details at https://developers.strava.com/docs/authentication/. Please note that you will only have to fill once the refresh token, the tool will then update when needed the screts file.

## Usage

Just run the following command :

`./main.py <number_of_latest_activities_to_upload>`
