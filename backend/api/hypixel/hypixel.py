from .config import Config

import requests
import json


def get_items():
    items = requests.get(
        url=f'https://api.hypixel.net/v2/resources/skyblock/items'
    ).json()['items']

    return items


def username_to_uuid(username):
    #uuid = requests.get(
    #    url=f'https://api.mojang.com/users/profiles/minecraft/{username}'
    #).json()['id']

    response = requests.get(
        url=f'https://api.mojang.com/users/profiles/minecraft/{username}'
    )

    print(f"username to id: {username}")
    print(response)

    uuid = response.json()['id']

    return uuid


def get_highest_level_profile(uuid=None, username=None):
    if username:
        uuid = username_to_uuid(username)

    data = requests.get(
        url='https://api.hypixel.net/v2/skyblock/profiles',
        params={
            'key': Config.KEY,
            'uuid': uuid
        }
    ).json()

    if 'profiles' in data:
        data = data['profiles']
    else:
        print('No data')
        print(data)

    highest_level = -1
    best_profile = None
    for profile in data:
        if 'leveling' in profile['members'][uuid]:
            level = profile["members"][uuid]["leveling"]["experience"]
        else:
            level = 0

        if level > highest_level:
            highest_level = level
            best_profile = profile['members'][uuid]

    return best_profile


# Returns all the data associated with a profile
def get_whole_profile(uuid=None, username=None, profile=None):
    if username:
        uuid = username_to_uuid(username)

    data = requests.get(
        url='https://api.hypixel.net/v2/skyblock/profiles',
        params={
            'key': Config.KEY,
            'uuid': uuid
        }
    ).json()

    if 'profiles' in data:
        data = data['profiles']
    else:
        print('No data')
        print(data)

    # Default to selected profile but try to find a profile if it's given
    if profile:
        for profile_data in data:
            if profile_data['cute_name'] == profile:
                return profile_data

    return [p for p in data if p['selected']][0]


# Returns the player-specific data associated with a profile
def get_user_data(username, profile=None):
    uuid = username_to_uuid(username)

    whole_profile = get_whole_profile(uuid=uuid, profile=profile)

    return whole_profile['members'][uuid]


