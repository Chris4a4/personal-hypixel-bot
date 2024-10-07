from os import path
from api.hypixel.hypixel import get_items

import json


class Config:
    RECIPES = None
    TRACKING = None

    ITEMS = None
    ITEM_PRIO = None

    tracker_data = {}

    @classmethod
    def initialize_variables(cls):
        cls.RECIPES = cls.load_recipes()
        cls.TRACKING = cls.load_tracking_data()

        cls.ITEMS = cls.load_items(cls.RECIPES)
        cls.ITEM_PRIO = cls.order_items(cls.RECIPES, cls.ITEMS)

        for user in cls.TRACKING:
            cls.tracker_data[user['username']] = {
                1: None,
                2: None,
                3: None,
                4: None,
                5: None,
                6: None,
                7: None
            }

    @staticmethod
    def load_recipes():
        cur_dir = path.dirname(path.abspath(__file__))
        recipes_path = path.join(cur_dir, 'data', 'recipes.json')
        with open(recipes_path) as f:
            return json.load(f)

    @staticmethod
    def load_tracking_data():
        cur_dir = path.dirname(path.abspath(__file__))
        tracking_path = path.join(cur_dir, 'data', 'tracking.json')
        with open(tracking_path) as f:
            return json.load(f)

    @staticmethod
    def load_items(recipes):
        forge_items = set()

        # Add all recipe items and all potentially non-recipe item children
        for item, recipe in recipes.items():
            forge_items.add(item)
            for component in recipe['recipe']:
                forge_items.add(component)

        # Populate details using Hypixel API
        hypixel_data = get_items()

        # TODO upgrade this
        # https://sky.shiiyu.moe/head/53fd8e87dd9032cd72f6fa2d6b45e53f0827b527263da648e0ee5552cdad6cbc
        result = {}
        for item in forge_items:
            item_hypixel_data = [a for a in hypixel_data if a['id'] == item][0]

            result[item] = {
                'name': item_hypixel_data['name']
            }

        return result

    @staticmethod
    def order_items(recipes, items):
        prio_list = list(items.keys() - recipes.keys())
        remaining_recipes = list(recipes.keys())

        # Remove items from all_items and add them to prio_list in order
        while remaining_recipes:
            for item in remaining_recipes:
                # Are any of this item's components not in the list yet?
                for component in recipes[item]['recipe']:
                    if component not in prio_list:
                        break
                # All components are already present, so add it too
                else:
                    remaining_recipes.remove(item)
                    prio_list.insert(0, item)
                    break

        return prio_list


Config.initialize_variables()
