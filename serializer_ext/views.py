from otree.models import Session
from django.views.generic import TemplateView
from django.shortcuts import render
from .serializers import SessionSerializer
from rest_framework import generics
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer

# a view that returns json for specific session
class SpecificSessionDataView(generics.ListAPIView):
    serializer_class = SessionSerializer
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)

    def get_queryset(self):
        session_code = self.kwargs['session_code']
        q = Session.objects.filter(code=session_code)
        return q

# the view to get a list of all sessions
class AllSessionsList(TemplateView):
    template_name = 'serializer_ext/all_session_list.html'
    url_name = 'json_sessions_list'
    url_pattern = r'^sessions_list_for_json/$'
    display_name = 'Exporting data to JSON'

    def get(self, request, *args, **kwargs):
        all_sessions = Session.objects.all()
        return render(request, self.template_name, {'sessions': all_sessions})
