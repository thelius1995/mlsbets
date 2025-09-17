import requests
import json
import datetime
from datetime import timedelta
from dateutil import tz
import itertools
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

'''
MLS ID - 89345
J-League ID - 20619
LigaMX ID - 44525
France Ligue 1 - 40032
Italy Serie A - 40030
Germany Bundesliga - 40481
Spain La Liga - 40031
English Premier League - 40253
League 1 - 40822
League 2 - 40823
Championship - 40817
Portugal Primeira liga - 44069
'''


from_zone = tz.tzutc()
to_zone = tz.tzlocal()

headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 OPR/113.0.0.0'

}

league_ids = [89345]

events_key = "events"

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# The ID and range of a sample spreadsheet.
#SAMPLE_SPREADSHEET_ID = "1bpf-YcpdSpIJW-gqhfMkASqYwsxuxbgG7C2Df-7DD2k"
SAMPLE_SPREADSHEET_ID = "18Uvemr8wQz4Hy8iBqFZYG1RABRxGe0rrLKWRLULtzTc"

def append_values(spreadsheet_id, range_name, value_input_option, _values):
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    try:
        service = build("sheets", "v4", credentials=creds)

        values = _values
        body = {"values": values}
        result = (
            service.spreadsheets()
            .values()
            .append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption=value_input_option,
                body=body,
            )
            .execute()
        )
        print(f"{(result.get('updates').get('updatedCells'))} cells appended.")
        return result

    except HttpError as error:
        print(f"An error occurred: {error}")
        return error

def serialize_datetime(obj): 
    if isinstance(obj, datetime.datetime): 
        return obj.isoformat() 
    raise TypeError("Type not serializable") 

for league_id in league_ids:
    url = f"https://sportsbook.draftkings.com/sites/US-OH-SB/api/v5/eventgroups/{league_id}/categories/543?format=json"
    
    payload={}
    response = requests.request("GET", url, headers=headers, data=payload)
    json_obj = response.json()

    """
    Build two seperate lists from the web request to pull info from
    """
    if "eventGroup" in json_obj and events_key in json_obj["eventGroup"]:
        dk_events_list = json_obj["eventGroup"][events_key]
        for i, offerCategory in enumerate(json_obj["eventGroup"]["offerCategories"]):
            categoryId = offerCategory.get("offerCategoryId")
            if categoryId == 543:
                corners_list = json_obj["eventGroup"]["offerCategories"][i]["offerSubcategoryDescriptors"][0]["offerSubcategory"]["offers"]

        """
        Iterate through both lists simultaneously pulling out relevent data from each list
        """
        for (event, corner) in itertools.zip_longest(dk_events_list, corners_list):
            eventId = event.get("eventId")
            name = event.get("name")
            startdate = event.get("startDate")
            #enddate = startdate + timedelta(3)
            stamp = datetime.datetime.fromisoformat(startdate[:-1])
            stamp = stamp.astimezone(to_zone)
            stamp = json.dumps(stamp, default=serialize_datetime) 
            team1 = event.get("team1").get("name")
            team2 = event.get("team2").get("name")
            data = [stamp,team1,team2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

            cornerevent = corner[0].get("eventId")
            outcomes = corner[0].get("outcomes")
            if cornerevent == eventId:
                for outcome in outcomes:
                    label = outcome.get("label")
                    line = outcome.get("line")
                    oddsDecimalDisplay = outcome.get("oddsDecimalDisplay")
                    oddsAmerican = outcome.get("oddsAmerican")
                    if line == 7.5:
                        if label == "Under":
                            data[3] = oddsDecimalDisplay
                        if label == "Over":
                            #print(f"Label: {label}, Line: {line}, OddsDecimal: {oddsDecimalDisplay}, OddsAmerican: {oddsAmerican}, StartDate: {startdate}")
                            data[6] = oddsDecimalDisplay
                    if line == 8.5:
                        if label == "Under":
                            data[8] = oddsDecimalDisplay
                        if label == "Over":
                            #print(f"Label: {label}, Line: {line}, OddsDecimal: {oddsDecimalDisplay}, OddsAmerican: {oddsAmerican}, StartDate: {startdate}")
                            data[11] = oddsDecimalDisplay
                    if line == 9.5:
                        if label == "Under":
                            data[15] = oddsDecimalDisplay
                        if label == "Over":
                            #print(f"Label: {label}, Line: {line}, OddsDecimal: {oddsDecimalDisplay}, OddsAmerican: {oddsAmerican}, StartDate: {startdate}")
                            data[19] = oddsDecimalDisplay
                            
            else:
                break
            
            if league_id == 89345:
                append_values(
                    SAMPLE_SPREADSHEET_ID,
                    "MLSAuto",
                    "USER_ENTERED",
                    [data],
                )
            elif league_id == 20619:
                append_values(
                    SAMPLE_SPREADSHEET_ID,
                    "JapaneseLeagueAuto",
                    "USER_ENTERED",
                    [data],
                )
            elif league_id == 44525:
                append_values(
                    SAMPLE_SPREADSHEET_ID,
                    "MexicoLigaMXAuto",
                    "USER_ENTERED",
                    [data],
                )
            elif league_id == 40032:
                append_values(
                    SAMPLE_SPREADSHEET_ID,
                    "FranceLigue1Auto",
                    "USER_ENTERED",
                    [data],
                )
            elif league_id == 40030:
                append_values(
                    SAMPLE_SPREADSHEET_ID,
                    "ItalySerieAAuto",
                    "USER_ENTERED",
                    [data],
                )
            elif league_id == 40481:
                append_values(
                    SAMPLE_SPREADSHEET_ID,
                    "GermanyBundesligaAuto",
                    "USER_ENTERED",
                    [data],
                )
            elif league_id == 40031:
                append_values(
                    SAMPLE_SPREADSHEET_ID,
                    "SpainLaLigaAuto",
                    "USER_ENTERED",
                    [data],
                )
            elif league_id == 40253:
                append_values(
                    SAMPLE_SPREADSHEET_ID,
                    "EnglishPremierAuto",
                    "USER_ENTERED",
                    [data],
                )
            elif league_id == 40822:
                append_values(
                    SAMPLE_SPREADSHEET_ID,
                    "EnglishLeague1Auto",
                    "USER_ENTERED",
                    [data],
                )
            elif league_id == 40823:
                append_values(
                    SAMPLE_SPREADSHEET_ID,
                    "EnglishLeague2Auto",
                    "USER_ENTERED",
                    [data],
                )
            elif league_id == 40817:
                append_values(
                    SAMPLE_SPREADSHEET_ID,
                    "EnglishChampionshipAuto",
                    "USER_ENTERED",
                    [data],
                )
            elif league_id == 44069:
                append_values(
                    SAMPLE_SPREADSHEET_ID,
                    "PortugalPrimeiraLigaAuto",
                    "USER_ENTERED",
                    [data],
                )
            else:
                print("LeagueID does not match known IDs")
            
    else:
        print(f"Key '{events_key}' not found in the nested JSON.")