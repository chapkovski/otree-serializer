from django.conf.urls import url, include
from serializer_ext import views as v
from django.conf import settings
from django.contrib.auth.decorators import login_required
from rest_framework import routers, serializers, viewsets

from serializer_ext.views import SessionUserViewSet

router = routers.DefaultRouter()
router.register(r'sessions', SessionUserViewSet)

urlpatterns = [url(r'^drfdrf/', include(router.urls)), ]
view_classes = [v.SpecificSessionDataView]

# to protect if auth level
for ViewCls in view_classes:
    if settings.AUTH_LEVEL in {'DEMO', 'STUDY'}:
        as_view = login_required(ViewCls.as_view())
    else:
        as_view = ViewCls.as_view()
    urlpatterns.append(url(ViewCls.url_pattern, as_view, name=ViewCls.url_name))
