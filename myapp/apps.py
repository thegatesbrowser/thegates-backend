from django.apps import AppConfig

class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'
    global all_games
    all_games = ['/challenge.gate','/drawing.gate','/gdquest_demo.gate','/multiplayer.gate',
                 '/path_tracing.gate','/solar_system.gate','/starcatcher.gate','/world.gate',]