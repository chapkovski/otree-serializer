from django.conf.urls import url, include
from serializer_ext import views as v
from django.conf import settings
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^json_session/(?P<session_code>\w+)/$', v.SpecificSessionDataView.as_view(), name='json_export'),
]
