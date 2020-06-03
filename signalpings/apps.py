from django.apps import AppConfig

class SignalPingsConfig(AppConfig):
    name = 'signalpings'
    label = 'signalpings'
    verbose_name = 'Signal Pings'

    def ready(self):
        import signalpings.signals
