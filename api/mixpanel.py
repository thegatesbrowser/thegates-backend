from mixpanel import Mixpanel

key_file = 'mixpanel.key'
f = open(key_file, 'r')
key = f.read()
print("Mixpanel key: " + key)
mp = Mixpanel(key)


def track(data):
    user_id = data.pop('user_id')
    user_id = user_id.replace('{','')
    user_id = user_id.replace('}','')
    
    event_name = data.pop('event_name')
    mp.track(user_id, event_name, data)
