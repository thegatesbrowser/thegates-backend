from mixpanel import Mixpanel

key = open('keys/mixpanel.key', 'r').read()
mp = Mixpanel(key)


def track(data):
    user_id = data.pop('user_id')
    event_name = data.pop('event_name')
    
    mp.track(user_id, event_name, data)
