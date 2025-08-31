from django.views.decorators.csrf import csrf_exempt
from django import http
import json
from myapp.models import Gates, FeaturedGates


def is_local(url: str) -> bool:
    return "://localhost" in url \
        or "://127.0.0.1" in url \
        or "://0.0.0.0" in url


@csrf_exempt
def discover_gate(req: http.HttpRequest) -> http.HttpResponse:
    data = json.loads(req.body)
    url = data['url']
    title = data['title']
    description = data['description']
    icon = data['icon']
    image = data['image']
    resource_pack = data['resource_pack']
    
    if is_local(url): return http.HttpResponse(status=200)
    
    gates = Gates.objects.filter(url=url)
    if gates.count() == 0:
        gate = Gates(url=url, title=title, description=description, icon=icon, image=image,
                     resource_pack=resource_pack, number_of_entries=1)
        gate.save()
        print("Discovered gate: " + url)
    else:
        gate = gates[0]
        gate.url = url
        gate.title = title
        gate.description = description
        gate.icon = icon
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
    
    fgates_objs = FeaturedGates.objects.order_by('sort_order', 'id')
    
    titles = [item['title'] for item in fgates_objs.values()]
    print(titles)
    
    result_list = []
    for gate_obj in fgates_objs:
        result_list.append({
            'url': gate_obj.url,
            'title': gate_obj.title,
            'description': gate_obj.description,
            'icon': gate_obj.icon,
            'is_special': gate_obj.is_special
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
            'icon': gate_obj.icon,
            'image': gate_obj.image,
            'number_of_entries': gate_obj.number_of_entries
        })
    
    output_json = json.dumps(result_list, indent=2)
    return http.HttpResponse(content=output_json)
