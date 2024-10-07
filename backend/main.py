import threading

import time
import schedule

from contextlib import asynccontextmanager
from threading import Thread, Event

from fastapi import FastAPI
from api.forge.router import forge_router
from api.forge.forge_tracker import update_forge_tracker


# Run scheduler every second, returns event to stop it
def run_continuously(interval=1):
    cease_continuous_run = Event()

    class ScheduleThread(Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.daemon = True
    continuous_thread.start()
    return cease_continuous_run


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Schedule all periodic jobs
    schedule.every(10).minutes.do(update_forge_tracker)

    stop_var = run_continuously()

    yield

    # Shutdown and kill thread
    stop_var.set()


tags_metadata = [
    {
        'name': 'Forge',
        'description': 'Hypixel Skyblock forge features, including a recipe calculator and forge tracker',
    }
]

app = FastAPI(openapi_tags=tags_metadata,
              title='ChrisAPI',
              description='Fun little API I set up for Skyblock stuff',
              version='0.0.1',
              lifespan=lifespan
              )
app.include_router(forge_router, tags=['Forge'])
