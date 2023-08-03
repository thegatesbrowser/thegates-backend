import meilisearch
# Подключение к MeiliSearch
key = open('meilisearch/meilisearch.key', 'r').read()
client = meilisearch.Client('http://127.0.0.1:7700', key)

index = client.index('gates')