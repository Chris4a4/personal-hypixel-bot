from api.hypixel.hypixel import get_user_data
from .config import Config

from time import time


NUM_FORGE_SLOTS = 7
QUICK_FORGE_REDUCTION = 0.3


# Represents a user's forge slot
class ForgeSlot:
    def __init__(self, start_time, item_id):
        self.start_time = start_time
        self.item_id = item_id

        if item_id in Config.RECIPES:
            self.predicted_finish = start_time / 1000 + Config.RECIPES[item_id]['forge_time'] * (1 - QUICK_FORGE_REDUCTION)
            self.item_name = Config.ITEMS[item_id]["name"]
        else:
            print(f"unknown item {item_id}")
            self.predicted_finish = None
            self.item_name = None


# Check the API and update the current forging items and their webhooks
def update_forge_tracker():
    print("Updating forge tracker...")
    for user_dict in Config.TRACKING:
        profile_data = get_user_data(username=user_dict['username'], profile=user_dict['profile'])

        # Clear forge
        if 'forge' not in profile_data:
            print("no forge")
            for slot_index in range(0, NUM_FORGE_SLOTS):
                Config.tracker_data[user_dict['username']][slot_index + 1] = None

        # Update items
        for slot_num, slot_data in profile_data['forge']['forge_processes']['forge_1'].items():
            Config.tracker_data[user_dict['username']][slot_num] = ForgeSlot(slot_data['startTime'], slot_data['id'])
    
    print("Done updating forge tracker...")
