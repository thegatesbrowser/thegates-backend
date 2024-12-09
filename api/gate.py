from django.views.decorators.csrf import csrf_exempt
from django import http
import requests
import json
from myapp.models import Gates, FeaturedGates
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

    url = data['url']
    title = data['title']
    description = data['description']
    image = data['image']
    resource_pack = data['resource_pack']
    # libraries = data['libraries']

    if is_local(url):
        return http.HttpResponse(status=200)
    
    gates = Gates.objects.filter(url=url)
    if gates.count() == 0:
        gate = Gates(url=url, title=title, description=description, image=image,
                     resource_pack=resource_pack, number_of_entries=1) #, libraries=libraries
        gate.save()
        print("Discovered gate: " + url)
    else:
        gate = gates[0]
        gate.url = url
        gate.title = title
        gate.description = description
        gate.image = image
        gate.resource_pack = resource_pack
        
        if gate.number_of_entries is None: gate.number_of_entries = 1
        else: gate.number_of_entries += 1
        
        gate.save()
    
    return http.HttpResponse(status=200)


@csrf_exempt
def featured_gates(req: http.HttpRequest) -> http.HttpResponse:
    if req.method != 'GET': return http.HttpResponse(status=400)
    print("Featured gates:")
    
    fgates_objs = FeaturedGates.objects.all()

    titles = [item['title'] for item in fgates_objs.values()]
    print(titles)
    
    result_list = []
    for gate_obj in fgates_objs:
        result_list.append({
            'url': gate_obj.url,
            'title': gate_obj.title,
            'description': gate_obj.description,
            'image': gate_obj.image,
        })
    
    output_json = json.dumps(result_list, indent=2)
    return http.HttpResponse(content=output_json)


@csrf_exempt
def all_gates(req: http.HttpRequest) -> http.HttpResponse:
    if req.method != 'GET': return http.HttpResponse(status=400)
    print("All gates:")
    
    gates_objs = Gates.objects.all()

    titles = [item['title'] for item in gates_objs.values()]
    print(titles)
    
    result_list = []
    for gate_obj in gates_objs:
        result_list.append({
            'id': str(gate_obj.pk),
            'url': gate_obj.url,
            'title': gate_obj.title,
            'description': gate_obj.description,
            'image': gate_obj.image,
            'number_of_entries': gate_obj.number_of_entries
        })
    
    output_json = json.dumps(result_list, indent=2)
    return http.HttpResponse(content=output_json)
