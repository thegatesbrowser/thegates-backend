from django.views.decorators.csrf import csrf_exempt
from django import http
import requests
import json
from myapp.models import Gates, Downloads
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from django.db.models import Count
from myapp.auth_meilisearch import index
from myapp.auth_meilisearch import client as meili_client



class SearchResult:
    url: str
    title: str
    description: str
    image: str

    def __init__(self, url, title, description, image) -> None:
        self.url = url
        self.title = title
        self.description = description
        self.image = image


# DJANGO ORM
def get_search_result(query: str) -> str:
    print(query)
    
    while '  ' in query:
        query = query.replace('  ',' ')
    print(query)
    word = query
    gates_query = Q()
    if ' ' in word:
            word_list = word.split(' ')
            for i in word_list:
                i = i.strip()
                gates_query |= Q(title__icontains = i)
                gates_query |= Q(title__icontains = i.lower())
                gates_query |= Q(description__icontains = i)
                gates_query |= Q(description__icontains = i.lower())
    else:
        word = word.strip()
        gates_query |= Q(title__icontains = word)
        gates_query |= Q(title__icontains = word.lower())
        gates_query |= Q(description__icontains = word)
        gates_query |= Q(description__icontains = word.lower())

    results = []
    search_objects = Gates.objects.filter(gates_query)
    for gate in search_objects:
         results.append(gate)

    return json.dumps(results, default=vars)


def search_in_meilisearch(query):
    
    search_results = index.search(query)['hits']
    return search_results


def remove_duplicate_hits_by_id(hits):
    unique_hits = {}
    for hit in hits:
       
        unique_hits[hit['id']] = hit
    return list(unique_hits.values())


def extract_words_from_json(json_data, user_input, unique_words):
    user_input = user_input.lower()
    for attr in ['title', 'description', 'tags']:
        if attr in json_data:
            if attr in json_data['_matchesPosition']:
                
                matches = json_data['_matchesPosition'][attr]

                
                for match in matches:
                    start = match['start']

                    end = json_data[attr].find(' ', start)
                    if end == -1:
                     
                        end = len(json_data[attr])

                    word = json_data[attr][start:end]

                 
                    word_lower = word.lower()

                   
                    if word_lower.startswith(user_input) and word_lower not in unique_words:
                        word = word.replace(',', '')
                        unique_words.add(word_lower)
                        return {'prompt': word}  

    return {}


def get_search_result_by_MS(query: str) -> str:
    print(query)
     
    user_input = query
    search_results = search_in_meilisearch(user_input)
    words = user_input.split()
    all_hits = []
    all_hits.extend(search_results)
    
    for word in words:
        word_search_results = search_in_meilisearch(word)
        all_hits.extend(word_search_results)
    all_hits = remove_duplicate_hits_by_id(all_hits)
    
    # all_hits_json = json.dumps(all_hits, ensure_ascii=False, indent=4)  
    output_json = json.dumps(all_hits, indent=2)
    print(type(output_json))
    if output_json == '[]':
        print("JSON пустой")
        top_count = 5
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)

        
        top_downloads = Downloads.objects.filter(if_game=True, date__range=[start_date, end_date]) \
                            .values('gate_app') \
                            .annotate(download_count=Count('gate_app')) \
                            .order_by('-download_count')[:top_count]

       
        for item in top_downloads:
            print(f"Gate App: {item['gate_app']}, Download Count: {item['download_count']}")
        result_list = []
        for item in top_downloads:
            gate_app = item['gate_app']
            gate_objs = Gates.objects.filter(url__endswith=f"{gate_app}")
            for gate_obj in gate_objs:
                result_list.append({
                    'gate_app': gate_app,
                    'download_count': item['download_count'],
                    'url': gate_obj.url,
                    'title': gate_obj.title,
                    'description': gate_obj.description,
                    'image': gate_obj.image,
                    'resource_pack': gate_obj.resource_pack,
                    'tags': gate_obj.tags
                })

        
        output_json = json.dumps(result_list, indent=2)
        print(output_json)
    return output_json


def get_prompt_words(query: str) -> str:
    user_input = query
    search_result = index.search(user_input, {
        'showMatchesPosition': True,
        'attributesToSearchOn': ["title","description","tags"]
    })
    unique_words = set()
  
    words_for_user = []

    for result in search_result['hits']:
        words = extract_words_from_json(result, user_input, unique_words)
        if words:
            words_for_user.append(words)

   
    output_json = json.dumps(words_for_user, ensure_ascii=False, indent=4)

    return output_json



@csrf_exempt
def search(req: http.HttpRequest) -> http.HttpResponse:
    if req.method == 'GET':
        query = req.GET.get('query', '')
        query = requests.utils.unquote(query)
        # if query != '': return http.HttpResponse(content=get_search_result(query))        #   DJANGO ORM
        if query != '': return http.HttpResponse(content=get_search_result_by_MS(query))    
    return http.HttpResponse(status=400)


@csrf_exempt
def prompt(req: http.HttpRequest) -> http.HttpResponse:
    if req.method == 'GET':
        query = req.GET.get('query', '')
        query = requests.utils.unquote(query)
        if query != '': return http.HttpResponse(content=get_prompt_words(query))    

    return http.HttpResponse(status=400)