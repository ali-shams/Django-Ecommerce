from django.apps import AppConfig

class WarehouseConfig(AppConfig):
    default_auto_field: str
    name: str
    label: str
    def ready(self) -> None: ...
