import requests
from myapp.models import TelegramBotUser

bot_token = open('keys/telegram_bot.key', 'r').read()
chat_id = open('keys/my_telegram_id.key', 'r').read()

url = f'https://api.telegram.org/bot{bot_token}/sendMessage'


def get_location(ip_address: str):
    response = requests.get(f"http://ip-api.com/json/{ip_address}?fields=66846719").json()
    location_data = {
        'ip': ip_address,
        'city': response.get('city'),
        'country': response.get('country')
    }
    return location_data


def bot_notify_application_open(data):
    user_id = data.get('user_id')
    event_name = data.get('event_name')

    if event_name != 'application_open':
        return
    
    telegram_bot_user = TelegramBotUser.objects.filter(user_id=user_id).first()
    if telegram_bot_user is not None and telegram_bot_user.is_ignore:
        return
    
    ip = data.get('ip')
    location_data = get_location(ip)
    city = location_data.get('city')
    country = location_data.get('country')
    
    params = {
        'chat_id': chat_id,
        'text': f'User opened TheGates {user_id}\n{city} {country}'
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        print('Message sent:\n' + params['text'])
    else:
        print('Failed to send message:', response.text)


def bot_notify_none_user_id(data):
    ip = data.get('ip')
    location_data = get_location(ip)
    city = location_data.get('city')
    country = location_data.get('country')
    
    params = {
        'chat_id': chat_id,
        'text': f'Event with \'none\' user_id from {ip} in {city} {country}:\n{data}'
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        print('Message sent:\n' + params['text'])
    else:
        print('Failed to send message:', response.text)
        return
