from django.apps import AppConfig


class CoflexBookingAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "CoFlex_Booking_app"

    def ready(self):
        import CoFlex_Booking_app.signals