from django.views.decorators.csrf import csrf_exempt
from django import http
import requests
import json
from myapp.models import Gates
from urllib.parse import urlparse
import re

def is_valid_hostname(hostname):
    # Проверяем, является ли `hostname` IP-адресом
    # Возвращает False, если `hostname` - IP-адрес, иначе True
    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", hostname):
        return False
    return True

def extract_words_from_url(url):
    # Разбираем URL на его компоненты
    parsed_url = urlparse(url)
    # Обработка netloc (адрес хоста) на предмет наличия слов (если не является IP-адресом)
    netloc_words = [word for word in re.findall(r'\b[a-zA-Z]{2,}\b', parsed_url.netloc) if is_valid_hostname(parsed_url.netloc)]
    # Извлекаем слова из path с помощью разделителей '/' и '.'
    path_parts = re.findall(r'[a-zA-Z]{2,}', parsed_url.path)
    # Объединяем слова из path, query и fragment
    combined_text = ' '.join(path_parts + [parsed_url.query, parsed_url.fragment])
    # Удаляем знаки препинания и разделители, оставляем только буквы и цифры
    cleaned_text = re.sub(r'[^\w\s]', '', combined_text)
    # Разделяем текст по пробелам для извлечения отдельных слов
    words = cleaned_text.split()
    # Фильтруем и удаляем пустые строки из списка
    words = [word for word in words if word.strip()]
    # Добавляем слова из netloc, но удаляем дубликаты
    words.extend(netloc_words)
    words = list(set(words))
    # Удаляем заданные слова "http", "https" и "gate", если они присутствуют
    words = [word for word in words if word.lower() not in ['http', 'https', 'gate', 'me', 'com']]
    return words

def is_local(url: str) -> bool:
    # return ''
    return "://localhost" in url \
        or "://127.0.0.1" in url \
        or "://0.0.0.0" in url


@csrf_exempt
def discover_gate(req: http.HttpRequest) -> http.HttpResponse:
    data = json.loads(req.body)
    print(data)

    url = data['url']   # url = "http://95.163.241.188:8000/solar_system.gate"
    title = data['title']
    description = data['description']
    image = data['image']
    resource_pack = data['resource_pack']
    # libraries = data['libraries']
    tags = ''
    words = extract_words_from_url(url)
    if words:
        print(", ".join(words))
        tags = ", ".join(words)
    else:
        print("No meaningful words found in the URL.")

    if is_local(url):
        return http.HttpResponse(status=200)
    
    gates = Gates.objects.filter(url=url)
    if gates.count() == 0:
        gate = Gates(url=url, title=title, description=description, image=image, resource_pack=resource_pack,tags = tags) #, libraries=libraries
        gate.number_of_entries = gate.number_of_entries + 1
        gate.save()
        print("Discovered gate: " + url)
    else:
        gate = gates[0]
        gate.url = url
        gate.title = title
        gate.description = description
        gate.image = image
        gate.resource_pack = resource_pack
        gate.number_of_entries = gate.number_of_entries + 1
    
    return http.HttpResponse(status=200)
