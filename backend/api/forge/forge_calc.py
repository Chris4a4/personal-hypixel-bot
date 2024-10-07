from nbt.nbt import NBTFile
from base64 import b64decode
from io import BytesIO

from collections import Counter
from copy import copy

from api.hypixel.hypixel import get_user_data
from .config import Config

from functools import cache


# Multiplies all the values in a counter by num
def multiply_counter(counter, num):
    new_counter = copy(counter)
    for key in new_counter:
        new_counter[key] *= num

    return new_counter


# Returns a counter with all crafts required to make an item
@cache
def compute_crafts(item_id):
    crafts = Counter({item_id: 1})

    recipe = Config.RECIPES.get(item_id)
    if not recipe:
        return crafts

    for item, qty in recipe['recipe'].items():
        crafts += multiply_counter(compute_crafts(item), qty)

    return crafts


# Decompresses and parses NBT tag data for an inventory
def parse_inventory(data):
    item_counts = Counter()

    nbt_file = NBTFile(fileobj=BytesIO(b64decode(data)))
    for slot in nbt_file[0]:
        # Empty bag slots
        if 'tag' not in slot:
            continue

        slot_id = str(slot['tag']['ExtraAttributes']['id'])
        slot_count = int(str(slot['Count']))

        item_counts.update({slot_id: slot_count})

    return item_counts


# Gets all the player's items and returns them as Counters
def get_player_items(data):
    sacks = Counter()
    inv = data['inventory']
    if 'sacks_counts' in inv:
        sacks.update(inv['sacks_counts'])

    ender_chest = Counter()
    if 'ender_chest_contents' in inv:
        ender_chest.update(parse_inventory(inv['ender_chest_contents']['data']))

    inventory = Counter()
    if 'inv_contents' in inv:
        inventory.update(parse_inventory(inv['inv_contents']['data']))

    backpacks = Counter()
    if 'backpack_contents' in inv:
        for key, value in inv['backpack_contents'].items():
            backpacks.update(parse_inventory(value['data']))

    forge = Counter()
    if 'forge' in data:
        for forge_slot in data['forge']['forge_processes']['forge_1'].values():
            forge.update({forge_slot['id'], 1})

    return sacks, ender_chest, inventory, backpacks, forge


# Takes two counters with materials we need/have and outputs directions on how to create the final product(s)
def generate_howto(original_required, actual_required):
    we_supplied = original_required - actual_required

    # Populate dictionary showing how to make the item
    how_to = {'raw': [], 'craft': [], 'forge': []}
    for item_id in reversed(Config.ITEM_PRIO):
        if item_id not in original_required:
            continue

        recipe = Config.RECIPES.get(item_id)
        details = {
            'id': item_id,
            'have': we_supplied[item_id],
            'need': original_required[item_id],
            'time': 0
        }

        # Raw materials
        if not recipe:
            how_to['raw'].append(details)

        # Craft items
        elif recipe['forge_time'] == 0:
            how_to['craft'].append(details)

        # Forged items
        else:
            details['time'] = recipe['forge_time'] * actual_required[item_id]
            how_to['forge'].append(details)

    return how_to


# Generates instructions to make a given set of forge recipes
def forge_calc(input_dict, username, profile):
    # Count items we need
    items_required = Counter()
    for item, qty in input_dict.items():
        items_required += multiply_counter(compute_crafts(item), qty)
    original_required = copy(items_required)

    # Look up profile and count items we have
    profile_data = get_user_data(username=username, profile=profile)
    sacks, ender_chest, inventory, backpacks, forge = get_player_items(profile_data)
    have_items = sacks + ender_chest + inventory + backpacks + forge

    # If the user is only asking for one item, don't count it even if we already have it
    if len(input_dict) == 1:
        item_id = list(input_dict.keys())[0]

        have_items[item_id] = 0

    # Subtract items we have from the items we need
    for item in Config.ITEM_PRIO:
        if item in items_required and item in have_items:
            qty_have = have_items[item]
            qty_need = items_required[item]

            if qty_have >= qty_need:
                items_required -= multiply_counter(compute_crafts(item), qty_need)
            else:
                items_required -= multiply_counter(compute_crafts(item), qty_have)

    return generate_howto(original_required, items_required)