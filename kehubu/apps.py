from django.apps import AppConfig
from django.conf import settings


class KehubuConfig(AppConfig):
    name = 'kehubu'

    def ready(self):
        from django.contrib.auth import get_user_model
        from . import signals
        from actstream import registry
        registry.register(self.get_model('Group'))
        registry.register(get_user_model())
