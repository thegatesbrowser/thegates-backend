chmod +x meilisearch-linux-amd64
nohup ./meilisearch-linux-amd64 --master-key "$(< meilisearch.key)" &