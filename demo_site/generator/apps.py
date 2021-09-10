import os
from django.conf import settings
from django.apps import AppConfig


class GeneratorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'generator'
    PRETRAINED_MODELS_PATH = os.path.join(settings.BASE_DIR, "generator/model/")
