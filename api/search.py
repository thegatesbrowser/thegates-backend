from django.views.decorators.csrf import csrf_exempt
from django import http
import json


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
    welcome = SearchResult(
            url="http://95.163.241.188:8000/world.gate",
            title="Welcome Page",
            description="Explore other worlds!",
            image="./exports/welcome_page/welcome.png"
    )
    
    results = []
    results.append(welcome)
    results.append(welcome)
    results.append(welcome)
    results.append(welcome)

    return json.dumps(results, default=vars)


@csrf_exempt
def search(req: http.HttpRequest) -> http.HttpResponse:
    if req.method == 'GET':
        query = req.GET.get('query', '')
        if query != '': return http.HttpResponse(content=get_search_result(query))
    
    return http.HttpResponse(status=400)
