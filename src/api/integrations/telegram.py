import requests

bot_token = open('keys/telegram_bot.key', 'r').read()
chat_id = open('keys/my_telegram_id.key', 'r').read()

url = f'https://api.telegram.org/bot{bot_token}/sendMessage'


def notify_application_open(data):
    user_id = data['user_id']
    city = data['city']
    country = data['country']

    params = {
        'chat_id': chat_id,
        'text': f'User opened TheGates {user_id}\n{city} {country}'
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        print('Message sent:\n' + params['text'])
    else:
        print('Failed to send message:', response.text)
