from django.apps import AppConfig


class TravelerConfig(AppConfig):
    name = 'traveler'

    def ready(self):
        import traveler.signals
