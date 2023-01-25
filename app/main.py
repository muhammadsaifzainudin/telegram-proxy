import os
import asyncio
import logging
from aiogram import Bot, types
from aiogram.utils import exceptions
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List
import requests
import json
import time

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
log = logging.getLogger('broadcast')
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)


class BadRequest(Exception):
    def __init__(self, description):
        self.description = description
    
    def __str__(self):
        return self.description

def get_users():
    """
    Return users list
     """

    for chat_id in CHAT_ID.split(','):
        yield chat_id


@asyncio.coroutine
def send_telegram(user_id: str, text: str, disable_notification: bool = False):
  data = {"chat_id": user_id, "text": text, "parse_mode": "html",  "disable_notification": disable_notification}
  r = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',\
                    data = json.dumps(data),\
                    headers={'Content-Type': 'application/json'})
  response = json.loads(r.content.decode())

  if not response.get('ok'):
    raise BadRequest(response.get('description'))




async def send_payload(user_id, text) -> bool:
    loop = asyncio.get_event_loop()
    try:
        await send_telegram(user_id, text.json())
    except BadRequest:
        log.error(f"Target [ID:{user_id}]: Error in sending message", exc_info=True)
    else:
        log.info(f"Target [ID:{user_id}]: success")
        return True
    
    return False



async def send_message(user_id: int, text: str, disable_notification: bool = False) -> bool:
    """
    Safe messages sender
    :param user_id:
    :param text:
    :param disable_notification:
    :return:
    """
    try:
        await bot.send_message(user_id, text, disable_notification=disable_notification)
    except exceptions.BotBlocked:
        log.error(f"Target [ID:{user_id}]: blocked by user", exc_info=True)
    except exceptions.ChatNotFound:
        log.error(f"Target [ID:{user_id}]: invalid user ID", exc_info=True)
    except exceptions.RetryAfter as e:
        log.error(f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds.", exc_info=True)
        await asyncio.sleep(e.timeout)
        return await send_message(user_id, text)  # Recursive call
    except exceptions.UserDeactivated:
        log.error(f"Target [ID:{user_id}]: user is deactivated", exc_info=True)
    except exceptions.TelegramAPIError:
        log.error(f"Target [ID:{user_id}]: failed", exc_info=True)
    else:
        log.info(f"Target [ID:{user_id}]: success")
        return True
    return False

class Alerts(BaseModel):
    status: str
    labels: Optional[dict]
    annotations: Optional[dict]
    startsAt: Optional[str]
    endsAt: Optional[str]
    valueString: Optional[str]
    generatorURL: Optional[str]
    fingerprint: Optional[str]
    silenceURL: Optional[str]
    dashboardURL: Optional[str]
    panelURL: Optional[str]


class Body(BaseModel):
    receiver: str
    status: str
    orgId: Optional[int]
    alerts: List[Alerts]
    groupLabels: Optional[dict]
    commonLabels: Optional[dict]
    commonAnnotations: Optional[dict]
    externalURL: Optional[str]
    version: Optional[str]
    groupKey: Optional[str]
    truncatedAlerts: Optional[int]
    title: Optional[str]
    state: Optional[str]
    message: Optional[str]
    

class Test(BaseModel):
    message: str

app = FastAPI()

@app.post("/telegram_proxy")
async def broadcaster(item: Test):
    for user_id in get_users():
        await send_payload(user_id=user_id, text=item)
        time.sleep(0.5)





    













