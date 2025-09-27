import requests
from typing import Dict

from api.integrations import telegram, discord
from myapp.models import TelegramBotUser


def get_location(ip_address: str) -> Dict[str, str]:
    response = requests.get(f"http://ip-api.com/json/{ip_address}?fields=66846719").json()

    return {
        'ip': ip_address,
        'city': response.get('city'),
        'country': response.get('country')
    }


def notify_application_open(data: Dict[str, str]) -> None:
    user_id = data['user_id']
    event_name = data['event_name']

    if event_name != 'application_open':
        return

    telegram_bot_user = TelegramBotUser.objects.filter(user_id=user_id).first()
    if telegram_bot_user is not None and telegram_bot_user.is_ignore:
        return

    location_data = get_location(data['ip'])

    payload = data.copy()
    payload['city'] = location_data['city']
    payload['country'] = location_data['country']
    telegram.notify_application_open(payload.copy())
    # discord.notify_application_open(payload.copy())
