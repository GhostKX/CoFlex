from django.apps import AppConfig


class CoflexStaffAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "CoFlex_Staff_app"

    def ready(self):
        import CoFlex_Staff_app.signals