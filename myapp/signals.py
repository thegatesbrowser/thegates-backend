from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import meilisearch
from .models import Gates

# Подключение к MeiliSearch
client = meilisearch.Client('http://127.0.0.1:7700', 'T7k0CsSOeo2vjJBl1kvym0pWlb2-G-S-RbM7kqdkErs')  # Замените на актуальный хост и ключ

# Функция для обновления данных в MeiliSearch
def update_meilisearch_data(instance):
    # Пример: преобразование экземпляра модели Gates в словарь для передачи в MeiliSearch
    data = {
        'id': str(instance.pk),
        'url': instance.url,
        'title': instance.title,
        'description': instance.description,
        'image': instance.image,
        'resource_pack': instance.resource_pack,
        'tags': instance.tags
        # 'number_of_entries': instance.number_of_entries,
    }
    index = client.index('gates')  # Замените 'gates' на имя индекса MeiliSearch
    index.update_documents([data])

# Обработчик сигнала для обновления данных в MeiliSearch при сохранении модели Gates
@receiver(post_save, sender=Gates)
def gates_post_save(sender, instance, **kwargs):
    update_meilisearch_data(instance)

# Обработчик сигнала для удаления данных из MeiliSearch при удалении модели Gates
@receiver(post_delete, sender=Gates)
def gates_post_delete(sender, instance, **kwargs):
    index = client.index('gates')  # Замените 'gates' на имя индекса MeiliSearch
    index.delete_documents([str(instance.pk)])
