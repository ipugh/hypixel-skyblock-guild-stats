import time
import httpx
import asyncio
import json
import base64
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import sys
import argparse

# Parse any incoming arguments
parser = argparse.ArgumentParser(description='Hypixel Skyblock Guild Stats')
parser.add_argument('-f', dest='checkfailure', action='store_const',
                    const=True, default=False,
                    help='Only checks any failed members')

args = parser.parse_args()

# Set arguments from command line
CHECK_FAILURE = args.checkfailure

# Get environment variables
api_key =  os.environ.get('HYPIXEL_API_KEY')
spreadsheet_id = os.environ.get('STATS_SHEETS_ID')

# Spreadsheet permissions
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Initialize global variables
service = None

# Xp needed for skill level map
xp_needed = {
    0: 0,
    1: 50,
    2: 175,
    3: 375,
    4: 675,
    5: 1175,
    6: 1925,
    7: 2925,
    8: 4425,
    9: 6425,
    10: 9925,
    11: 14925,
    12: 22425,
    13: 32425,
    14: 47425,
    15: 67425,
    16: 97425,
    17: 147425,
    18: 222425,
    19: 322425,
    20: 522425,
    21: 822425,
    22: 1222425,
    23: 1722425,
    24: 2322425,
    25: 3022425,
    26: 3822425,
    27: 4722425,
    28: 5722425,
    29: 6822425,
    30: 8022425,
    31: 9322425,
    32: 10722425,
    33: 12222425,
    34: 13822425,
    35: 15522425,
    36: 17322425,
    37: 19222425,
    38: 21222425,
    39: 23322425,
    40: 25522425,
    41: 27822425,
    42: 30222425,
    43: 32722425,
    44: 35322425,
    45: 38072425,
    46: 40972425,
    47: 44072425,
    48: 47472425,
    49: 51172425,
    50: 55172425,
}


# Gets a player uuid from their username
async def get_uuid(username):
    url = "https://api.mojang.com/users/profiles/minecraft/" + username
    response = httpx.get(url)
    return response


# Gets a hypixel player profile given a player `uuid`
async def get_profile(uuid):
    url = 'https://api.hypixel.net/player'
    response = httpx.get(
        url,
        params={'key': api_key, 'uuid': uuid},
    )
    json = response.json()
    return json


# Gets skyblock profiles from hypixel given hypixel player `profile`
async def get_skyblock(profile):
    url = 'https://api.hypixel.net/skyblock/profile'
    response = httpx.get(
        url,
        params={'key': api_key, 'profile': profile},
    )
    json = response.json()
    return json


# Get the skyblock profile from `profile` that is specified by `name`
def get_profile_id(profile, name):
    profiles = profile['player']['stats']['SkyBlock']['profiles']
    for p in profiles:
        if str(profiles[p]['cute_name']).lower() == name.lower():
            print(", profile: ", profiles[p]['cute_name'], "- ", end="")
            return str(p)

    return None


# Get stats from player `name` with skyblock profile name `cutename`
def get_stats(name, cutename):
    name = asyncio.run(get_uuid(name))
    id = name.json()['id']

    profile = asyncio.run(get_profile(id))

    profile_id = get_profile_id(profile, cutename)

    response = asyncio.run(get_skyblock(profile_id))
    stats = response['profile']['members'][id]  # this should be the data
    return stats


# Using the xp_needed dictionary, return a skill level given `xp` in that skill
def get_level(xp):
    if xp == 0:
        return 0
    lvl = -1
    for i in range(51):
        if xp < xp_needed[i]:
            lvl = i - 1
            break

    if lvl == -1:
        return 50

    xp = xp - xp_needed[lvl]
    current_xp = xp_needed[lvl]
    next_xp = xp_needed[lvl + 1]
    level_cost = next_xp - current_xp
    progress = round(xp / level_cost, 2)
    lvl = lvl + progress
    return lvl


# Authenticates and sets up service with google sheets
def setup_spreadsheets():
    # use the global var service so later methods can access sheets
    global service

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)


# Gets the (names, profiles, failure_status) from the spreadsheet
# Currently those are the first 3 columns
def spreadsheets():
    # A2:A gets names
    # B2:B gets profiles
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                range="A3:A").execute()
    names = result.get('values', [])

    result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                range="B3:B").execute()
    profiles = result.get('values', [])

    result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                range="C3:C").execute()
    failure = result.get('values', [])

    return (names, profiles, failure)


# Inserts a user's data into the spreadsheet
def insert_spreadsheet(user_data, row):
    values = [
        ["",
        user_data['skill_average'],
        user_data['total_slayer'],
        user_data['combat'],
        user_data['foraging'],
        user_data['mining'],
        user_data['fishing'],
        user_data['farming'],
        user_data['alchemy'],
        user_data['enchanting'],
        user_data['zombie'],
        user_data['spider'],
        user_data['wolf'],
        user_data['gifts_given'],
        user_data['death_count'],
        user_data['coin_purse']]
    ]

    body = {
        'values': values
    }

    rangename = 'C' + str(row) + ':R' + str(row)

    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=rangename,
        valueInputOption="RAW", body=body).execute()


# This sets the failure flag in a row inside the spreadsheet
def fail_spreadsheet(row):
    values = [
        ['T']
    ]

    body = {
        'values': values
    }

    rangename = 'C' + str(row)

    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=rangename,
        valueInputOption="RAW", body=body).execute()


# --------------------------------------------
# This is the stuff that actually runs in main

if (CHECK_FAILURE):
    print("Only checking for failed users")

setup_spreadsheets()
members = spreadsheets()

for i in range(len(members[0])):

    if (CHECK_FAILURE and len(members[2][i]) == 0):
        continue

    user_data = {}
    try:
        print(members[0][i][0], end="")
        stats = get_stats(members[0][i][0], members[1][i][0])
        user_data['foraging'] = get_level(stats['experience_skill_foraging'])
        user_data['farming'] = get_level(stats['experience_skill_farming'])
        user_data['alchemy'] = get_level(stats['experience_skill_alchemy'])
        user_data['combat'] = get_level(stats['experience_skill_combat'])
        user_data['enchanting'] = get_level(stats['experience_skill_enchanting'])
        user_data['mining'] = get_level(stats['experience_skill_mining'])
        user_data['fishing'] = get_level(stats['experience_skill_fishing'])
        user_data['skill_average'] = round(
            (user_data['foraging'] + user_data['farming'] + user_data['alchemy'] + user_data['combat'] +
             user_data['enchanting'] + user_data['mining'] + user_data['fishing']) / 7, 2)
        user_data['zombie'] = stats['slayer_bosses']['zombie']['xp']
        user_data['spider'] = stats['slayer_bosses']['spider']['xp']
        user_data['wolf'] = stats['slayer_bosses']['wolf']['xp']
        user_data['total_slayer'] = user_data['zombie'] + user_data['spider'] + user_data['wolf']
        user_data['death_count'] = stats['death_count']
        user_data['coin_purse'] = stats['coin_purse']
        user_data['gifts_given'] = stats['stats']['gifts_given']
    except:
        fail_spreadsheet(i+3)
        print("Failed")
        time.sleep(3)
        continue

    insert_spreadsheet(user_data, i+3)
    print("Success")

    time.sleep(3)
