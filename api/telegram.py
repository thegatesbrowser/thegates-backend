import requests

bot_token = open('keys/telegram_bot.key', 'r').read()
chat_id = open('keys/my_telegram_id.key', 'r').read()

url = f'https://api.telegram.org/bot{bot_token}/sendMessage'


def get_location(ip_address: str):
    response = requests.get(f'https://ipapi.co/{ip_address}/json/').json()
    location_data = {
        'ip': ip_address,
        'city': response.get('city'),
        'region': response.get('region'),
        'country': response.get('country_name')
    }
    return location_data


def bot_notify_event(data):
    user_id = data.get('user_id')
    event_name = data.get('event_name')
    user_ignore = open('staticfiles/telegram_bot_user_ignore.txt', 'r').read()
    
    if event_name != 'application_open' or user_id in user_ignore:
        return
    
    ip = data.get('ip')
    location_data = get_location(ip)
    city = location_data.get('city')
    country = location_data.get('country')
    
    params = {
        'chat_id': chat_id,
        'text': f'User opened TheGates {user_id} {city} {country}'
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        print('Message sent: ' + params['text'])
    else:
        print('Failed to send message:', response.text)
