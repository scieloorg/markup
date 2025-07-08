from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from reference.api.v1.views import ReferenceViewSet

app_name = "reference"

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("reference", ReferenceViewSet, basename="reference")

urlpatterns = router.urls


#app_name = "pid_provider"

#if settings.DEBUG:
#    router = DefaultRouter()
#else:
#    router = SimpleRouter()