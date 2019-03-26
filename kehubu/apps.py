from django.apps import AppConfig


class KehubuConfig(AppConfig):
    name = 'kehubu'

    def ready(self):
        from . import signals