from django.views.decorators.csrf import csrf_exempt
from django import http
import requests
import json
import re
from myapp.models import Gates, Downloads, SearchSuggestions
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from django.db.models import Count
from myapp.auth_meilisearch import index
from myapp.auth_meilisearch import client as meili_client


TOKEN_PATTERN = re.compile(r"[#@\w][\w\-]*")


def strip_non_alnum_edges(value: str) -> str:
    if not value:
        return ""

    start = 0
    end = len(value)

    while start < end and not value[start].isalnum():
        start += 1

    while end > start and not value[end - 1].isalnum():
        end -= 1

    return value[start:end]


def strip_bbcode_markup(value: str) -> str:
    if not isinstance(value, str):
        return ""
    # Remove BBCode tags like [tag], [/tag], or [tag=value]
    return re.sub(r"\[(?:/?)[^\]]+\]", " ", value)


def sanitize_source_text(value: str) -> str:
    if not isinstance(value, str):
        return ""
    text = strip_bbcode_markup(value)
    text = re.sub(r"https?://", "", text, flags=re.IGNORECASE)
    text = text.replace("\r", " ")
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_clean_tokens(text: str) -> list[str]:
    sanitized = sanitize_source_text(text)
    if not sanitized:
        return []
    return TOKEN_PATTERN.findall(sanitized)


# DJANGO ORM
def get_search_result(query: str) -> str:
    while '  ' in query:
        query = query.replace('  ',' ')
    
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


def get_search_result_by_MS(query: str) -> str:
    user_input = query
    search_results = search_in_meilisearch(user_input)
    words = user_input.split()
    all_hits = []
    all_hits.extend(search_results)
    
    for word in words:
        word_search_results = search_in_meilisearch(word)
        all_hits.extend(word_search_results)
    all_hits = remove_duplicate_hits_by_id(all_hits)
    
    for hint in all_hits:
        url = hint['url']
        gate_objs = Gates.objects.filter(url__endswith=f"{url}")
        for gate_obj in gate_objs:
            hint['number_of_entries'] = gate_obj.number_of_entries
        
        if 'icon' not in hint:
            hint['icon'] = ""
    
    output_json = json.dumps(all_hits, separators=(",", ":"))
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
                    'icon': gate_obj.icon,
                    'image': gate_obj.image,
                    'resource_pack': gate_obj.resource_pack
                })
        
        output_json = json.dumps(result_list, separators=(",", ":"))
    
    return output_json


def get_suggestions() -> str:
    print("Search suggestions:")

    suggestions = SearchSuggestions.objects.all()
    titles = [item['query'] for item in suggestions.values()]
    print(titles)
    
    result_list = []
    for suggestion in suggestions:
        result_list.append(suggestion.query)
    
    output_json = json.dumps(result_list, separators=(",", ":"))
    return output_json


def extract_words_from_json(json_data, user_input, unique_words):
    normalized_user_input = strip_non_alnum_edges(user_input.lower())
    if not normalized_user_input:
        return []

    prompts = []
    matches_position = json_data.get('_matchesPosition', {})
    for attr in ['title', 'description']:
        if attr not in json_data:
            continue
        attr_matches = matches_position.get(attr, [])
        if not attr_matches:
            continue

        text = json_data[attr]
        for match in attr_matches:
            start = match.get('start', 0)
            length = match.get('length', 0)
            if length:
                segment = text[start:start + length]
            else:
                segment = text[start:]

            for token in extract_clean_tokens(segment):
                normalized_token = strip_non_alnum_edges(token.lower())
                if not normalized_token.startswith(normalized_user_input):
                    continue
                if normalized_token in unique_words:
                    continue
                unique_words.add(normalized_token)
                prompts.append(token)
    return prompts


def get_prompt_words(query: str) -> str:
    user_input = query
    unique_words = set()
    initial_prompts = []
    max_results = 12
    
    # 1) Try Meilisearch with match positions first
    try:
        search_result = index.search(user_input, {
            'showMatchesPosition': True,
            'attributesToSearchOn': ["title","description"]
        })
        for result in search_result.get('hits', []):
            if len(initial_prompts) >= max_results:
                break
            words = extract_words_from_json(result, user_input, unique_words)
            for word in words:
                if len(initial_prompts) >= max_results:
                    break
                initial_prompts.append(word)
    except Exception:
        pass
    
    # If nothing found, or to enrich results, scan raw text tokens from the hits
    # Collect tokens and later sort to prioritize hashtags and shorter tokens
    tokens_map = {}

    def add_token_if_match(token: str, normalized_prefix: str):
        normalized_token = strip_non_alnum_edges(token.lower())
        if not normalized_token.startswith(normalized_prefix):
            return
        if len(normalized_token) <= 1:
            return
        is_hashtag = token.startswith('#')
        existing = tokens_map.get(normalized_token)
        if existing is None or (is_hashtag and not existing['is_hashtag']):
            tokens_map[normalized_token] = {'token': token, 'is_hashtag': is_hashtag}

    normalized_prefix = strip_non_alnum_edges(user_input.lower())

    # 2) Tokenize titles/descriptions from MS hits regardless of matchesPosition
    try:
        if 'search_result' not in locals():
            search_result = index.search(user_input, {
                'attributesToSearchOn': ["title","description"]
            })
        for hit in search_result.get('hits', []):
            for attr in ['title', 'description']:
                if attr in hit and isinstance(hit[attr], str):
                    for token in extract_clean_tokens(hit[attr]):
                        add_token_if_match(token, normalized_prefix)
    except Exception:
        pass

    # 3) Also scan DB for tokens starting with prefix (merge results)
    if normalized_prefix:
        gates = Gates.objects.filter(
            Q(title__icontains=normalized_prefix) | Q(description__icontains=normalized_prefix)
        )[:100]
        for gate in gates:
            for text in [gate.title or '', gate.description or '']:
                for token in extract_clean_tokens(text):
                    add_token_if_match(token, normalized_prefix)

    # Now order tokens: hashtags first, shorter first, then alphabetical
    ordered = sorted(
        tokens_map.items(),
        key=lambda kv: (
            0 if kv[1]['is_hashtag'] else 1,
            len(kv[0]),
            kv[0]
        )
    )
    # Build final list capped by max_results
    final = []
    seen_outputs = set()

    def append_output(token: str):
        normalized_token = strip_non_alnum_edges(token.lower())
        if not normalized_token:
            return
        if normalized_token in seen_outputs:
            return
        if len(final) >= max_results:
            return
        final.append(token)
        seen_outputs.add(normalized_token)

    for _, meta in ordered:
        append_output(meta['token'])

    output_json = json.dumps({"prompts": final}, ensure_ascii=False, separators=(",", ":"))
    return output_json


@csrf_exempt
def search(req: http.HttpRequest) -> http.HttpResponse:
    if req.method == 'GET':
        query = req.GET.get('query', '')
        query = requests.utils.unquote(query)

        result = {'gates': get_search_result_by_MS(query), 'suggestions': '[]'}

        if result['gates'] == '[]':
            result['suggestions'] = get_suggestions()

        output_json = json.dumps(result, separators=(",", ":"))
        if query != '': return http.HttpResponse(content=output_json)
    
    return http.HttpResponse(status=400)


@csrf_exempt
def prompt(req: http.HttpRequest) -> http.HttpResponse:
    if req.method == 'GET':
        query = req.GET.get('query', '')
        query = requests.utils.unquote(query)
        if query != '': return http.HttpResponse(content=get_prompt_words(query))
    
    return http.HttpResponse(status=400)
