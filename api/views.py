from django.views.decorators.csrf import csrf_exempt
from django import http
from myapp.views import get_location_info
from myapp.models import Events
import json
def data_save(location_info, user_agent,json_data):
    
    event_name= json_data['event_name']
    user_id= json_data['user_id']
    user_id= user_id.replace('{','')
    user_id = user_id.replace('}','')

    if location_info['status'] == 'success':
        continent = location_info['continent']
        continentCode = location_info['continentCode']
        country = location_info['country']
        countryCode = location_info['countryCode']
        region = location_info['region']
        regionName = location_info['regionName']
        city = location_info['city']
        lat = location_info['lat']
        lon = location_info['lon']
        timezone = location_info['timezone']
        org = location_info['org']
        as_info = location_info['as']
        asname = location_info['asname']
        reverse = location_info['reverse']
        mobile = location_info['mobile']
        proxy = location_info['proxy']
        hosting = location_info['hosting']
        ip_address = location_info['query']
        event = Events(user_id=user_id,event_name=event_name, json_data = json_data,ip_address=ip_address, user_agent=user_agent, continent=continent,
                             continentCode=continentCode, country=country, countryCode=countryCode, region=region,
                             regionName=regionName, city=city, lat=lat, lon=lon, timezone=timezone, org=org,
                             as_info=as_info, asname=asname, reverse=reverse, mobile=mobile, proxy=proxy,
                             hosting=hosting)
        event.save()
    else:
        print('Не получилось вычислить по IP')
        error_msg = location_info['message']
        ip_address = location_info['query']
        print(f"Причина {location_info['query']}: {location_info['message']}")
        event = Events(user_id=user_id,event_name=event_name, json_data = json_data, ip_address=ip_address, user_agent=user_agent, error_msg=error_msg)
        event.save()
    return 1

@csrf_exempt
def analytics_event(req: http.HttpRequest) -> http.HttpResponse:
    ip_address = req.META['REMOTE_ADDR']
    user_agent = req.META['HTTP_USER_AGENT']
    location_info = get_location_info(ip_address)
    
    json_data = json.loads(req.body)
        
    data_save(location_info,user_agent,json_data)
    return http.HttpResponse(status=200)

@csrf_exempt
def get_user_id(req: http.HttpRequest) -> http.HttpResponse:
    if req.method == 'GET':
        device_id = req.GET.get('device_id', '')
        if device_id != '': return http.HttpResponse(content=device_id) # TODO: combine with IP address
    return http.HttpResponse(status=400)