from mixpanel import Mixpanel

key = open('mixpanel.key', 'r').read()
mp = Mixpanel(key)


def track(data):
    user_id = data.pop('user_id')
    user_id = user_id.replace('{','')
    user_id = user_id.replace('}','')
    
    event_name = data.pop('event_name')
    mp.track(user_id, event_name, data)
