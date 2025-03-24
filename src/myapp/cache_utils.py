# from django.core.cache import cache
# from django.conf import settings
# from cacheops import cached_as
# from transformers import MBartForConditionalGeneration, MBartTokenizer
#
# def get_model():
#     # попытаться получить модель из кеша
#     model = cache.get('model')
#     if model is None:
#         # если модель не найдена в кеше, загрузить ее
#         model = MBartForConditionalGeneration.from_pretrained("mbart_ru_sum_gazeta/model/")
#         # сохранить модель в кеше
#         cache.set('model', model, timeout=None)
#     return model
#
# def get_tokenizer():
#     # попытаться получить токенизатор из кеша
#     tokenizer = cache.get('tokenizer')
#     if tokenizer is None:
#         # если токенизатор не найден в кеше, загрузить его
#         tokenizer = MBartTokenizer.from_pretrained("mbart_ru_sum_gazeta/tokenizer/")
#         # сохранить токенизатор в кеше
#         cache.set('tokenizer', tokenizer, timeout=None)
#     return tokenizer
