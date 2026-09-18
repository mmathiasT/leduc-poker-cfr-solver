import pickle

from django.apps import AppConfig

STRATEGY = None

class PokerbotConfig(AppConfig):
    name = "pokerbot"

    def ready(self):
        global STRATEGY
        with open("leduc_strategy.pkl", "rb") as file:
            STRATEGY = pickle.load(file)