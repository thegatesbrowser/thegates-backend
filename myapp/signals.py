from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Gates
from myapp.auth_meilisearch import client, index


# Функция для обновления данных в MeiliSearch
def update_meilisearch_data(instance):
    # Пример: преобразование экземпляра модели Gates в словарь для передачи в MeiliSearch
    data = {
        'id': str(instance.pk),
        'url': instance.url,
        'title': instance.title,
        'description': instance.description,
        'image': instance.image,
        'resource_pack': instance.resource_pack
        # 'number_of_entries': instance.number_of_entries,
    }
    index.update_documents([data])

# Обработчик сигнала для обновления данных в MeiliSearch при сохранении модели Gates
@receiver(post_save, sender=Gates)
def gates_post_save(sender, instance, **kwargs):
    update_meilisearch_data(instance)

# Обработчик сигнала для удаления данных из MeiliSearch при удалении модели Gates
@receiver(post_delete, sender=Gates)
def gates_post_delete(sender, instance, **kwargs):
    index.delete_documents([str(instance.pk)])
