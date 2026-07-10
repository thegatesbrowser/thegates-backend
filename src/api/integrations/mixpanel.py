from mixpanel import Mixpanel, Consumer

key = open('keys/mixpanel.key', 'r').read().strip()
# EU data residency: send ingestion to Mixpanel's EU servers.
# Without an explicit api_host the library defaults to the US endpoint.
mp = Mixpanel(key, consumer=Consumer(api_host="api-eu.mixpanel.com"))


def track(data):
    user_id = data.pop('user_id')
    event_name = data.pop('event_name')
    
    mp.track(user_id, event_name, data)
