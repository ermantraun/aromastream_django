from django.apps import AppConfig
from django.core.signals import request_finished

class AromastreamConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aromastream'
    
    def ready(self):

        from . import signals

        request_finished.connect(signals.user_created)

        