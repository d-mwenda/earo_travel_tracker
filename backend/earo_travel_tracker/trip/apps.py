from django.apps import AppConfig



class TripConfig(AppConfig):
    name = 'trip'

    def ready(self):
        import trip.signals
