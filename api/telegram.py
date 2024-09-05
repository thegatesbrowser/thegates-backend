import requests

bot_token = open('keys/telegram_bot.key', 'r').read()
chat_id = open('keys/my_telegram_id.key', 'r').read()

url = f'https://api.telegram.org/bot{bot_token}/sendMessage'


def bot_notify_event(data):
    user_id = data.pop('user_id')
    event_name = data.pop('event_name')
    user_ignore = open('staticfiles/telegram_bot_user_ignore.txt', 'r').read()
    
    if event_name != "application_open" or user_id in user_ignore:
        return
    
    params = {
        'chat_id': chat_id,
        'text': 'User opened TheGates ' + user_id
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        print('Message sent: ' + params['text'])
    else:
        print('Failed to send message:', response.text)
