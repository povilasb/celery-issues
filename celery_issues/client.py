from .celery import publish_to_nowhere, my_task1


publish_to_nowhere.apply_async()
my_task1.apply_async()
