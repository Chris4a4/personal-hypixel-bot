from typing import Dict

from fastapi import APIRouter
from pydantic import BaseModel, field_validator

from .forge_calc import forge_calc
from .config import Config

forge_router = APIRouter()


class ItemDict(BaseModel):
    items: Dict[str, int]

    @field_validator('items')
    def check_items(cls, v):
        for item_name, quantity in v.items():
            if item_name not in Config.RECIPES:
                raise ValueError(f'{item_name} is not a forge recipe')

            if quantity <= 0:
                raise ValueError(f'Quantity of {item_name} must be positive')

        return v


@forge_router.post('/forge_calc/{username}/{profile}')
async def forge_calculator(username, profile, items: ItemDict):
    return forge_calc(items.items, username, profile)


@forge_router.post('/forge_calc/{username}')
async def forge_calculator(username, items: ItemDict):
    return forge_calc(items.items, username, None)


@forge_router.get('/forge_tracker')
async def forge_tracker():
    return Config.tracker_data
