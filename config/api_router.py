from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from reference.api.v1.views import ReferenceViewSet
from markup_doc.api.v1.views import ArticleViewSet

#app_name = "reference"

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("reference", ReferenceViewSet, basename="reference")
router.register("first_block", ArticleViewSet, basename="first_block")

urlpatterns = router.urls


#app_name = "pid_provider"

#if settings.DEBUG:
#    router = DefaultRouter()
#else:
#    router = SimpleRouter()