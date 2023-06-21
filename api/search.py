from django.views.decorators.csrf import csrf_exempt
from django import http
import json
from myapp.models import Gates
from django.db.models import Q
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


def get_search_result(query: str) -> str:
    print(query)
    #TODO Переводить двойные пробелы в одинарные пробелы 
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
    #welcome = SearchResult(
     #       url="http://95.163.241.188:8000/world.gate",
      #      title="Welcome Page",
       #     description="Explore other worlds!",
        #    image="./exports/welcome_page/welcome.png"
    #)
    
    
    #results.append(welcome)
    #results.append(welcome)
    #results.append(welcome)
    #results.append(welcome)

    return json.dumps(results, default=vars)


@csrf_exempt
def search(req: http.HttpRequest) -> http.HttpResponse:
    if req.method == 'GET':
        query = req.GET.get('query', '')
        if query != '': return http.HttpResponse(content=get_search_result(query))
    
    return http.HttpResponse(status=400)
